from sqlalchemy import Column, Enum, Integer, Numeric

from midnite_api.const import EventType
from midnite_api.db import Base


class Event(Base):
    __tablename__ = "tEvent"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    t = Column(Integer, unique=True, nullable=False)
    type = Column(Enum(EventType), nullable=False)
