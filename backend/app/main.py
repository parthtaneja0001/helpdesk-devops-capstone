from fastapi import Depends, FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import get_db
from .routes import tickets

app = FastAPI(title="HelpDesk API", version="1.0.0")
app.include_router(tickets.router)

# Exposes Prometheus metrics (request count, latency, in-flight) at /metrics
Instrumentator(excluded_handlers=["/metrics"]).instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)


@app.get("/", tags=["meta"])
def root():
    return {"service": "helpdesk-api", "docs": "/docs"}


@app.get("/health", tags=["meta"])
def health():
    """Liveness: the process is up."""
    return {"status": "ok"}


@app.get("/ready", tags=["meta"])
def ready(db: Session = Depends(get_db)):
    """Readiness: the database is reachable."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ready"}
