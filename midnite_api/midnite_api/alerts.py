from typing import List

from sqlalchemy.orm import Session

from midnite_api.const import AlertCode, EventType
from midnite_api.models import Event
from midnite_api.schemas import EventSchema


def generate_alert_codes(
    db: Session,
    user_id: int,
    event: EventSchema
) -> List[AlertCode]:
    alert_codes = []
    # For Code 1100: A withdraw amount over 100
    if event.type == EventType.WITHDRAW and event.amount > 100.00:
        alert_codes.append(AlertCode.CODE_1100)
    
    return alert_codes



