import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from midnite_api.alerts import generate_alert_codes
from midnite_api.cache import cache
from midnite_api.const import APP_NAME
from midnite_api.event import insert_event
from midnite_api.schemas import EventSchema, EventResponse
from midnite_api.db import get_db
from midnite_api.cache import cache

logger = logging.getLogger(APP_NAME)

router = APIRouter()


@router.post("/event", status_code=status.HTTP_201_CREATED)
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
    logger.info(f"Received event: {event.dict()}")
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
