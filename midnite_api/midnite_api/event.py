import logging
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from midnite_api.const import APP_NAME, EventType
from midnite_api.models import Event
from midnite_api.schemas import EventSchema


logger = logging.getLogger(APP_NAME)


def insert_event(db: Session, event: EventSchema):
    """
    Inserts a new event into the database.

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


def fetch_latest_n_user_events(db: Session, user_id: int, n: int) -> List[Event]:
    """
    Fetches the latest `n` events for a specific user from the database.

    This function queries the `tEvent` table for a given `user_id`, orders the results
    in descending order of time `t`, and returns the latest `n` events.

    Args:
        db (Session): SQLAlchemy session used to query the database.
        user_id (int): The ID of the user whose events should be fetched.
        n (int): The number of latest events to retrieve.

    Returns:
        List[Event]: A list of the most recent `n` Event records for the user.

    Raises:
        SQLAlchemyError: If the database query fails.
    """
    try:
        logger.info(f"Fetching latest {n} events for user_id: {user_id}")
        results = (
            db.query(Event)
            .filter(Event.user_id == user_id)
            .order_by(Event.t.desc())
            .limit(n)
            .all()
        )

        return results

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database Error while fetching events for user {user_id}: {e}")
        raise e


def fetch_latest_n_user_deposits(db: Session, user_id: int, n: int) -> List[Event]:
    """
    Fetches the latest `n` deposits for a specific user from the database.

    This function queries the `tEvent` table for a given `user_id`, orders the results
    in descending order of time `t`, and returns the latest `n` deposits.

    Args:
        db (Session): SQLAlchemy session used to query the database.
        user_id (int): The ID of the user whose deposits should be fetched.
        n (int): The number of latest deposits to retrieve.

    Returns:
        List[Event]: A list of the most recent `n` deposit Event records for the user.

    Raises:
        SQLAlchemyError: If the database query fails.
    """
    try:
        logger.info(f"Fetching latest {n} deposits for user_id: {user_id}")
        results = (
            db.query(Event)
            .filter(
                Event.user_id == user_id,
                Event.type == EventType.DEPOSIT,
            )
            .order_by(Event.t.desc())
            .limit(n)
            .all()
        )

        return results

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database Error while fetching events for user {user_id}: {e}")
        raise e


def fetch_sum_user_deposits_min_t(
    db: Session, user_id: int, min_t: int
) -> Optional[float]:
    """
    Calculates the total amount of deposits made by a user since a given minimum time.

    This function queries the `Event` table to sum the amounts of all deposit events
    for the specified `user_id` where the event time `t` is greater than or equal to `min_t`.

    Args:
        db (Session): SQLAlchemy session used for querying the database.
        user_id (int): The ID of the user whose deposits are being summed.
        min_t (int): The minimum event time (inclusive) from which to include deposits.

    Returns:
        Optional[float]: The total sum of deposits if any exist, otherwise `None`.

    Raises:
        SQLAlchemyError: If the database query fails.
    """
    try:
        logger.info(f"Fetching sum of deposits for user_id={user_id} from t >= {min_t}")
        deposit_sum = (
            db.query(func.sum(Event.amount))
            .filter(
                Event.user_id == user_id,
                Event.type == EventType.DEPOSIT,
                Event.t >= min_t,
            )
            .scalar()
        )

        return deposit_sum

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error while fetching deposit sum for user {user_id}: {e}"
        )
        raise e
