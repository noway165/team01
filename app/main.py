"""Vehicle Maintenance Log — 72ITDS30103 Software Development Platforms."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from psycopg_pool import ConnectionPool
from pydantic import BaseModel, Field

from app import ai

APP_NAME = os.getenv("APP_NAME", "vehicle-maintenance-log")
APP_VERSION = "0.5.0"  # Lab 5: the visible change for this pull request
FRIENDLY = "The AI feature is unavailable right now. Please try again in a minute."
PAGE = (Path(__file__).parent / "ui.html").read_text(encoding="utf-8")
APP_ENV = os.getenv("APP_ENV", "development")

# Connection string comes from the environment, never from the code.
DATABASE_URL = os.environ["DATABASE_URL"]  # crash at start if it is missing

# One pool per running copy of the app. Created closed: tests can import this
# file without a database; the server opens it at start-up (lifespan below).
pool = ConnectionPool(
    DATABASE_URL,
    min_size=1,
    max_size=5,  # small pool: several copies run
    max_lifetime=300,  # recycle: replace after 5 minutes
    check=ConnectionPool.check_connection,  # pre-ping: test before lending
    kwargs={
        "prepare_threshold": None,  # port 6543: no prepared statements
        "connect_timeout": 5,  # fail fast instead of hanging
    },
    open=False,
)


@asynccontextmanager
async def lifespan(app):
    pool.open()  # does not wait: the app starts even if the database is paused
    yield
    pool.close()  # Render stops the container: return the connections cleanly


app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)

vehicles: dict[int, dict] = {}
maintenance_records: dict[int, dict] = {}
next_vehicle_id = 1
next_record_id = 1


class Vehicle(BaseModel):
    name: str
    license_plate: str
    year: int


class MaintenanceRecord(BaseModel):
    vehicle_id: int
    category: str
    description: str
    cost: float


class SymptomInput(BaseModel):
    symptom_text: str = Field(min_length=1, max_length=8000)  # empty or huge text gets 422


@app.get("/")
def root():
    return {"app": APP_NAME, "version": APP_VERSION, "env": APP_ENV, "message": "Vehicle Maintenance Log API"}


@app.get("/health")
def health():
    """Used by Render (Lab 3) and the pipeline (Week 6) to check the app is alive."""
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    """Proves the database works. Borrows a connection from the pool for one query."""
    try:
        with pool.connection(timeout=5) as conn:
            n = conn.execute("SELECT count(*) FROM notes").fetchone()[0]
        return {"db": "ok", "notes": n}
    except psycopg.Error as err:  # also PoolTimeout / PoolClosed from the pool
        print("health/db failed:", type(err).__name__, err, flush=True)  # details to the logs only
        return JSONResponse(status_code=503, content={"db": "error"})


@app.get("/vehicles")
def list_vehicles():
    return vehicles


@app.post("/vehicles")
def create_vehicle(vehicle: Vehicle):
    global next_vehicle_id
    vehicles[next_vehicle_id] = vehicle.model_dump()
    next_vehicle_id += 1
    return vehicles[next_vehicle_id - 1]


@app.get("/maintenance-records")
def list_records():
    return maintenance_records


@app.post("/maintenance-records")
def create_record(record: MaintenanceRecord):
    global next_record_id
    if record.vehicle_id not in vehicles:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    maintenance_records[next_record_id] = record.model_dump()
    next_record_id += 1
    return maintenance_records[next_record_id - 1]


@app.get("/ui", response_class=HTMLResponse)
def ui():
    """The diagnosis page. It calls only POST /diagnose on this server."""
    return PAGE


@app.post("/diagnose")
def diagnose(symptom: SymptomInput):
    """The AI call happens here, on the server; the key never reaches the browser."""
    try:
        answer = ai.summarize_safe(symptom.symptom_text)
    except ai.AIUnavailable as err:
        print("ai failed:", err.reason, flush=True)  # the reason goes to the logs, never the key
        return JSONResponse(status_code=503, content={"ai_suggestion": None, "message": FRIENDLY})
    # The prompt asks for LOW / MEDIUM / HIGH on the first line; anything else is "unknown".
    first, _, rest = answer.partition("\n")
    urgency = first.strip(" *.:").lower()
    if urgency not in ("low", "medium", "high"):
        urgency, rest = "unknown", answer
    return {
        "symptom_text": symptom.symptom_text,
        "ai_suggestion": rest.strip() or answer,
        "urgency_level": urgency,
    }
