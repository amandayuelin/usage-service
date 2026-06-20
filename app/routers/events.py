from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from .. import schemas
from ..db import SessionLocal
from ..models import Event
from sqlalchemy import text
import json

router = APIRouter()

# In-memory quick dedupe cache for same-process idempotency (MVP)
SEEN_EVENTS = set()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from fastapi.responses import JSONResponse


@router.post("/events")
def ingest_event(event: schemas.EventIn, db: Session = Depends(get_db)):
    # Debug: show current dedupe cache
    # debug prints removed
    # Check for existing event_id to provide idempotent behavior
    # Fast in-process dedupe check
    if event.event_id in SEEN_EVENTS:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "duplicate", "event_id": event.event_id})

    # Perform atomic insert-if-not-exists to avoid duplicates across concurrent requests
    sql = text(
        """
        INSERT INTO events (event_id, customer_id, resource_id, resource_type, usage, usage_unit, timestamp, metadata)
        SELECT :event_id, :customer_id, :resource_id, :resource_type, :usage, :usage_unit, :timestamp, :metadata
        WHERE NOT EXISTS (SELECT 1 FROM events WHERE event_id = :event_id)
        """
    )
    params = {
        "event_id": event.event_id,
        "customer_id": event.customer_id,
        "resource_id": event.resource_id,
        "resource_type": event.resource_type,
        "usage": event.usage,
        "usage_unit": event.usage_unit,
        "timestamp": event.timestamp,
        "metadata": json.dumps(event.metadata) if event.metadata is not None else None,
    }
    res = db.execute(sql, params)
    db.commit()
    # record in in-memory dedupe cache
    SEEN_EVENTS.add(event.event_id)
    # rowcount may be 1 if inserted, 0 if ignored
    try:
        inserted = res.rowcount and int(res.rowcount) > 0
    except Exception:
        inserted = False

    if not inserted:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "duplicate", "event_id": event.event_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"status": "created", "event_id": event.event_id})


@router.get("/events", response_model=schemas.EventsList)
def list_events(
    customer_id: str = Query(...),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(Event).filter(Event.customer_id == customer_id)
    if start:
        q = q.filter(Event.timestamp >= start)
    if end:
        q = q.filter(Event.timestamp <= end)
    total = q.count()
    rows = q.order_by(Event.timestamp).limit(limit).offset(offset).all()
    events = [
        schemas.EventOut(
            event_id=r.event_id,
            customer_id=r.customer_id,
            resource_id=r.resource_id,
            resource_type=r.resource_type,
            usage=r.usage,
            usage_unit=r.usage_unit,
            timestamp=r.timestamp,
            metadata=r.metadata_,
        )
        for r in rows
    ]
    return {"events": events, "limit": limit, "offset": offset}


@router.get("/summaries", response_model=schemas.SummaryOut)
def summaries(
    customer_id: str = Query(...),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    granularity: str = Query("day"),
    db: Session = Depends(get_db),
):
    # Simple in-memory aggregation per-day
    q = db.query(Event).filter(Event.customer_id == customer_id)
    if start:
        q = q.filter(Event.timestamp >= start)
    if end:
        q = q.filter(Event.timestamp <= end)
    rows = q.all()
    # group by day
    buckets = {}
    for r in rows:
        key = r.timestamp.date()
        buckets.setdefault(key, 0.0)
        buckets[key] += float(r.usage)

    out_buckets = []
    for day, total in sorted(buckets.items()):
        start_dt = datetime.combine(day, datetime.min.time())
        end_dt = start_dt + timedelta(days=1)
        out_buckets.append(schemas.SummaryBucket(start=start_dt, end=end_dt, usage_total=total))

    return schemas.SummaryOut(customer_id=customer_id, granularity=granularity, buckets=out_buckets)
