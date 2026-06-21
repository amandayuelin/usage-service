from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class EventIn(BaseModel):
    event_id: str = Field(..., max_length=255)
    customer_id: str
    resource_id: str
    resource_type: str
    usage: float
    usage_unit: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class EventOut(BaseModel):
    event_id: str
    customer_id: str
    resource_id: str
    resource_type: str
    usage: float
    usage_unit: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class EventsList(BaseModel):
    events: List[EventOut]
    limit: int
    offset: int


class SummaryBucket(BaseModel):
    start: datetime
    end: datetime
    usage_total: float


class SummaryOut(BaseModel):
    customer_id: str
    granularity: str
    buckets: List[SummaryBucket]
