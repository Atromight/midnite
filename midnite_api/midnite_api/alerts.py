import logging
from typing import Set

from sqlalchemy import func
from sqlalchemy.orm import Session

from midnite_api.const import AlertCode, APP_NAME, EventType
from midnite_api.models import Event
from midnite_api.schemas import EventSchema


logger = logging.getLogger(APP_NAME)


def generate_alert_codes(db: Session, event: EventSchema) -> Set[AlertCode]:
    """
    Generates alert codes for a given financial event.

    This function checks the event against a predefined set of rules and returns
    a set of applicable alert codes. It handles logic for:
      - Code 1100: Withdrawal over 100
      - Code 30: 3 consecutive withdrawals
      - Code 300: Last 3 deposits have been increasing over time
      - Code 123: Accumulated deposits' amount is over 200 in a 30-second window

    Args:
        db (Session): SQLAlchemy session used to query historical event data.
        event (EventSchema): The event to analyze for potential alerts.

    Returns:
        Set[AlertCode]: A set of triggered alert codes for the given event.

    Raises:
        Exception: If any unexpected error occurs during alert code generation.
    """
    logger.info("Generating alert codes...")
    alert_codes = set()
    try:
        add_code_1100(alert_codes, event)
        add_code_30(alert_codes, event, db)
        add_code_300(alert_codes, event, db)
        add_code_123(alert_codes, event, db)

    except Exception as e:
        logger.error("Failed to generate alert codes")
        raise e

    return alert_codes


def add_code_1100(alert_codes: Set[AlertCode], event: EventSchema):
    """
    Adds alert code 1100 if the user made a withdraw of 100 or more.

    Args:
        alert_codes: The set to which alert codes are added.
        event: The current event (transaction) being processed.
    """
    try:
        if event.type == EventType.WITHDRAW and event.amount >= 100.00:
            logger.info(f"Adding Code: {AlertCode.CODE_1100} to alert_codes")
            alert_codes.add(AlertCode.CODE_1100)

    except Exception as e:
        logger.error(
            f"Error while trying to generate alert code: {AlertCode.CODE_1100}"
        )
        raise e


def add_code_30(alert_codes: Set[AlertCode], event: EventSchema, db: Session):
    """
    Adds alert code 30 if the user has made 3 consecutive withdraws.

    Args:
        alert_codes: The set to which alert codes are added.
        event: The current event (transaction) being processed.
        db: SQLAlchemy session for querying past events.
    """
    try:
        results = (
            db.query(Event)
            .filter(Event.user_id == event.user_id)
            .order_by(Event.t.desc())
            .limit(3)
            .all()
        )
        if len(results) == 3 and all(
            result.type == EventType.WITHDRAW for result in results
        ):
            logger.info(f"Adding Code: {AlertCode.CODE_30} to alert_codes")
            alert_codes.add(AlertCode.CODE_30)

    except Exception as e:
        logger.error(f"Error while trying to generate alert code: {AlertCode.CODE_30}")
        raise e


def add_code_300(alert_codes: Set[AlertCode], event: EventSchema, db: Session):
    """
    Adds alert code 300 if the user's last 3 deposits have been increasing.

    Args:
        alert_codes: The set to which alert codes are added.
        event: The current event (transaction) being processed.
        db: SQLAlchemy session for querying past events.
    """
    try:
        results = (
            db.query(Event)
            .filter(
                Event.user_id == event.user_id,
                Event.type == EventType.DEPOSIT,
            )
            .order_by(Event.t.desc())
            .limit(3)
            .all()
        )
        if len(results) == 3 and all(
            results[i].amount > results[i + 1].amount for i in range(2)
        ):
            logger.info(f"Adding Code: {AlertCode.CODE_300} to alert_codes")
            alert_codes.add(AlertCode.CODE_300)

    except Exception as e:
        logger.error(f"Error while trying to generate alert code: {AlertCode.CODE_300}")
        raise e


def add_code_123(alert_codes: Set[AlertCode], event: EventSchema, db: Session):
    """
    Adds alert code 123 if the user's deposit total in the last 30s is over 200.

    Args:
        alert_codes: The set to which alert codes are added.
        event: The current event (transaction) being processed.
        db: SQLAlchemy session for querying past events.
    """
    try:
        min_t = event.t - 30
        deposit_sum = (
            db.query(func.sum(Event.amount))
            .filter(
                Event.user_id == event.user_id,
                Event.type == EventType.DEPOSIT,
                Event.t >= min_t,
            )
            .scalar()
        )
        if deposit_sum and deposit_sum >= 200.0:
            logger.info(f"Adding Code: {AlertCode.CODE_123} to alert_codes")
            alert_codes.add(AlertCode.CODE_123)

    except Exception as e:
        logger.error(f"Error while trying to generate alert code: {AlertCode.CODE_123}")
        raise e
