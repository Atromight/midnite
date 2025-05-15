from contextlib import asynccontextmanager
import logging
import logging.config

from fastapi import FastAPI
from sqlalchemy.orm import Session

from midnite_api.cache import cache
from midnite_api.const import APP_NAME
from midnite_api.db import Base, engine, SessionLocal
from midnite_api.logger import LOGGING_CONFIG
from midnite_api.middleware import RequestIDMiddleware
from midnite_api.models import Event
from midnite_api.router import router


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
app.include_router(router)
app.add_middleware(RequestIDMiddleware)
