from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from midnite_api.db import Base, engine, get_db


@asynccontextmanager
async def db_init(app: FastAPI):
    # Startup
    print("Creating tables and loading data...")
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(lifespan=db_init)

@app.get("/")
async def root():
    return {"message": "Welcome to the Midnite API!"}

@app.post("/event")
def post_event(
    # event: EventInput,
    db: Annotated[Session, Depends(get_db)],
):
    pass