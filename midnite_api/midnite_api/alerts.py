import logging
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from midnite_api.const import AlertCode, EventType
from midnite_api.models import Event
from midnite_api.schemas import EventSchema


logger = logging.getLogger(__name__)

def generate_alert_codes(db: Session, event: EventSchema) -> List[AlertCode]:
    alert_codes = []
    try:
        # For Code 1100: A withdraw amount over 100
        add_code_1100(alert_codes, event)

        # For Code 30: 3 consecutive withdraws
        add_code_30(alert_codes, event, db)

        # For Code 300: 3 consecutive increasing deposits (ignoring withdraws)
        add_code_300(alert_codes, event, db)

        # For Code 123: Accumulative deposit amount over a window of 30 seconds is over 200
        add_code_123(alert_codes, event, db)

    except Exception as e:
        logger.error("Failed to generate alert codes")
        raise e

    return alert_codes


def add_code_1100(alert_codes: List[AlertCode], event: EventSchema):
    try:
        if event.type == EventType.WITHDRAW and event.amount > 100.00:
            alert_codes.append(AlertCode.CODE_1100)

    except Exception as e:
        logger.error(f"Error while trying to generate alert code: {AlertCode.CODE_1100}")
        raise e


def add_code_30(alert_codes: List[AlertCode], event: EventSchema, db: Session):
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
            alert_codes.append(AlertCode.CODE_30)

    except Exception as e:
        logger.error(f"Error while trying to generate alert code: {AlertCode.CODE_30}")
        raise e


def add_code_300(alert_codes: List[AlertCode], event: EventSchema, db: Session):
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
            alert_codes.append(AlertCode.CODE_300)

    except Exception as e:
        logger.error(f"Error while trying to generate alert code: {AlertCode.CODE_300}")
        raise e

def add_code_123(alert_codes: List[AlertCode], event: EventSchema, db: Session):
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
            alert_codes.append(AlertCode.CODE_123)

    except Exception as e:
        logger.error(f"Error while trying to generate alert code: {AlertCode.CODE_123}")
        raise e
