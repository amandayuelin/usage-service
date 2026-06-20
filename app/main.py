from fastapi import FastAPI
from .logging import configure_logging
from .config import settings
from .db import init_db
from .routers import events

configure_logging(settings.LOG_LEVEL.upper())


app = FastAPI(title="Usage Events Service")

# Ensure DB is initialized at import time for tests and simple startup
init_db()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


app.include_router(events.router)
