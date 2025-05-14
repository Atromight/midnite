from contextlib import asynccontextmanager
import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from midnite_api.alerts import generate_alert_codes
from midnite_api.cache import cache
from midnite_api.db import Base, engine, get_db, SessionLocal
from midnite_api.event import insert_event
from midnite_api.models import Event
from midnite_api.schemas import EventResponse, EventsResponse, EventSchema


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("Creating tables and initializing cache...")
    Base.metadata.create_all(bind=engine)

    # Init cache with latest `t`
    db: Session = SessionLocal()
    try:
        latest_t = db.query(Event.t).order_by(Event.t.desc()).limit(1).scalar()
        if latest_t is not None:
            cache.initialize(latest_t)
            logger.info(f"Initialized cache with t={latest_t}")
        else:
            logger.info("No events found. Cache starts empty.")

    except Exception as e:
        logger.error(f"Failed to initialize cache: {e}")

    finally:
        db.close()

    yield  # Run the app

    # SHUTDOWN
    logger.info("Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.get("/events")
def get_events(db: Annotated[Session, Depends(get_db)]) -> EventsResponse:
    query = db.query(Event)
    events = query.all()
    return EventsResponse(events=[EventSchema.from_orm(event) for event in events])


@app.post("/event", status_code=status.HTTP_201_CREATED)
def post_event(
    event: EventSchema,
    db: Annotated[Session, Depends(get_db)],
) -> EventResponse:
    try:
        # Validate new event.t
        latest_t = cache.get_latest_t()
        if latest_t is not None and event.t <= latest_t:
            logger.warning(f"Rejected event with t={event.t}: must be strictly greater than last t={latest_t}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event time t: must be strictly increasing."
            )

        insert_event(db, event)
        cache.update_latest_t(event.t)

        alert = False
        alert_codes = generate_alert_codes(db, event)
        if alert_codes:
            alert = True

        return EventResponse(alert=alert, alert_codes=alert_codes, user_id=event.user_id)

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Unexpected error processing event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
