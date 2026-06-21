from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, func
from sqlalchemy.sql import expression
from .db import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(255), unique=True, index=True, nullable=False)
    customer_id = Column(String(255), index=True, nullable=False)
    resource_id = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False)
    usage = Column(Float, nullable=False)
    usage_unit = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    metadata_ = Column('metadata', JSON, nullable=True)
    ingested_at = Column(DateTime, server_default=func.now(), nullable=False)
