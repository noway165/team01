"""Vehicle Maintenance Log — 72ITDS30103 Software Development Platforms."""

import os

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

APP_NAME = os.getenv("APP_NAME", "vehicle-maintenance-log")
APP_VERSION = "0.2.2"
APP_ENV = os.getenv("APP_ENV", "development")

# Connection string comes from the environment, never from the code.
DATABASE_URL = os.environ.get("DATABASE_URL")

app = FastAPI(title=APP_NAME, version=APP_VERSION)

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
    symptom_text: str


@app.get("/")
def root():
    return {"app": APP_NAME, "version": APP_VERSION, "env": APP_ENV, "message": "Vehicle Maintenance Log API"}


@app.get("/health")
def health():
    """Used by Render (Lab 3) and the pipeline (Week 6) to check the app is alive."""
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    """Proves the application itself can reach the database."""
    if not DATABASE_URL:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not set")
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
            n = conn.execute("SELECT count(*) FROM notes").fetchone()[0]
    except psycopg.Error as err:
        print(f"database error: {err}", flush=True)
        raise HTTPException(status_code=503, detail=str(err))
    return {"db": "ok", "notes": n}


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


@app.post("/diagnose")
def diagnose(symptom: SymptomInput):
    # Placeholder — real AI call added in Week 8
    return {
        "symptom_text": symptom.symptom_text,
        "ai_suggestion": "AI integration not yet implemented",
        "urgency_level": "unknown",
    }
