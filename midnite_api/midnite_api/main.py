from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from midnite_api.alerts import generate_alert_codes
from midnite_api.db import Base, engine, get_db
from midnite_api.event import insert_event
from midnite_api.models import Event
from midnite_api.schemas import EventResponse, EventsResponse, EventSchema


@asynccontextmanager
async def db_init(app: FastAPI):
    # Startup
    print("Creating tables and loading data...")
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(lifespan=db_init)


@app.get("/events")
def get_events(db: Annotated[Session, Depends(get_db)]) -> EventsResponse:
    query = db.query(Event)
    events = query.all()
    return EventsResponse(events=[EventSchema.from_orm(event) for event in events])


@app.post("/event")
def post_event(
    event: EventSchema,
    db: Annotated[Session, Depends(get_db)],
) -> EventResponse:
    insert_event(db, event)

    alert = False
    alert_codes = generate_alert_codes(db, event)
    if alert_codes:
        alert = True

    return EventResponse(alert=alert, alert_codes=alert_codes, user_id=event.user_id)
