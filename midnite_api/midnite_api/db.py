from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.

    Yields a SQLAlchemy session and ensures it is properly closed after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
