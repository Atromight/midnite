from contextlib import asynccontextmanager
import logging
import logging.config
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from midnite_api.alerts import generate_alert_codes
from midnite_api.cache import cache
from midnite_api.const import APP_NAME
from midnite_api.db import Base, engine, get_db, SessionLocal
from midnite_api.event import insert_event
from midnite_api.logger import LOGGING_CONFIG
from midnite_api.models import Event
from midnite_api.schemas import EventResponse, EventSchema


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(APP_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application lifespan handler.

    This function is called on application startup and shutdown. On startup,
    it initializes the database schema (creates tables) and sets up the in-memory
    cache with the latest event timestamp (`t`) if any events exist.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    logger.info("Creating tables and initializing cache...")
    Base.metadata.create_all(bind=engine)

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

    yield

    logger.info("Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.post("/event", status_code=status.HTTP_201_CREATED)
def post_event(
    event: EventSchema,
    db: Annotated[Session, Depends(get_db)],
) -> EventResponse:
    """
    Handles POST request for a new financial event and checks for alert conditions.

    Validates that the event's timestamp (`t`) is strictly increasing relative to
    the latest processed event. If valid, stores the event in the database,
    updates the cache, and evaluates applicable alert codes.

    Args:
        event (EventSchema): The incoming financial event payload.
        db (Session): SQLAlchemy database session dependency.

    Returns:
        EventResponse: A response indicating whether any alerts were triggered and
        which alert codes were matched.

    Raises:
        HTTPException:
            - 400 if the event's `t` is not strictly increasing.
            - 500 for any unexpected server error.
    """
    try:
        latest_t = cache.get_latest_t()
        if latest_t is not None and event.t <= latest_t:
            logger.warning(
                f"Rejected event with t={event.t}: must be strictly greater than last t={latest_t}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event time t: must be strictly increasing.",
            )

        insert_event(db, event)
        cache.update_latest_t(event.t)

        alert = False
        alert_codes = generate_alert_codes(db, event)
        if alert_codes:
            alert = True

        return EventResponse(
            alert=alert, alert_codes=alert_codes, user_id=event.user_id
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Unexpected error processing event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
