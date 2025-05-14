from typing import List

from pydantic import BaseModel

from midnite_api.const import AlertCode, EventType


class EventSchema(BaseModel):
    user_id: int
    amount: float
    t: int
    type: EventType

    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    alert: bool
    alert_codes: List[AlertCode] = []
    user_id: int
