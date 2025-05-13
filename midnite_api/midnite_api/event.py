from sqlalchemy.orm import Session

from midnite_api.models import Event
from midnite_api.schemas import EventSchema


def insert_event(db: Session, event: EventSchema):
    new_event = Event(
        type=event.type, amount=event.amount, user_id=event.user_id, t=event.t
    )

    db.add(new_event)  # Stage the object for insert
    db.commit()  # Commit the transaction (insert happens here)
    db.refresh(new_event)  # Optional: populate fields like `id` from DB
