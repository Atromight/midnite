import logging

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from midnite_api.const import APP_NAME
from midnite_api.models import Event
from midnite_api.schemas import EventSchema


logger = logging.getLogger(APP_NAME)


def insert_event(db: Session, event: EventSchema):
    """
    Inserts a new financial event into the database.

    This function creates a new `Event` record from the provided schema and commits
    it to the database. It handles transaction management and error logging.

    Args:
        db (Session): SQLAlchemy session used to insert the event.
        event (EventSchema): The event data to be stored.

    Raises:
        SQLAlchemyError: If the database transaction fails.
    """
    try:
        logger.info(f"Inserting event: {event.dict()} to DB")
        new_event = Event(
            type=event.type, amount=event.amount, user_id=event.user_id, t=event.t
        )

        db.add(new_event)
        db.commit()
        db.refresh(new_event)

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database Error: {e}")
        raise e
