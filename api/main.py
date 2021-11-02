import os

import fastapi_chameleon
from decouple import config
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from .db import create_db_and_tables, get_session
from .models import (
    Measurement,
    MeasurementCreate,
    MeasurementRead,
    Observer,
    ObserverCreate,
    ObserverRead,
)
from .services.email_service import send_email_data_entry
from .services.twilio_service import send_webpage_url

dev_mode = config("DEV_MODE")

app = FastAPI()
folder = os.path.dirname(__file__)
template_folder = os.path.join(folder, "templates")
template_folder = os.path.abspath(template_folder)

fastapi_chameleon.global_init(template_folder, auto_reload=dev_mode)

DOMAIN = config("DOMAIN")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/observers/", response_model=ObserverRead)
def create_observer(
    *, session: Session = Depends(get_session), observer: ObserverCreate
):
    query = select(Observer).where(Observer.email == observer.email)
    existing_observer = session.exec(query).first()
    if existing_observer is not None:
        return existing_observer

    db_observer = Observer.from_orm(observer)
    session.add(db_observer)
    session.commit()
    session.refresh(db_observer)
    return db_observer


@app.delete("/observers/{observer_id}")
def delete_observer(*, session: Session = Depends(get_session), observer_id: int):
    observer = session.get(Observer, observer_id)
    if not observer:
        raise HTTPException(status_code=404, detail="Observer not found")
    session.delete(observer)
    session.commit()
    return {"ok": True}


@app.post("/measurements/", response_model=MeasurementRead)
def create_measurement(
    *, session: Session = Depends(get_session), measurement: MeasurementCreate
):

    db_measurement = Measurement.from_orm(measurement)

    observer = session.get(Observer, measurement.observer_id)
    if observer is None:
        raise HTTPException(status_code=400, detail="Not a valid observer id")

    session.add(db_measurement)
    session.commit()
    session.refresh(db_measurement)

    send_email_data_entry(observer, db_measurement)
    send_webpage_url(observer, db_measurement)

    return db_measurement


@app.get("/measurements/{measurement_id}", response_model=MeasurementRead)
def read_measurement(*, session: Session = Depends(get_session), measurement_id: int):
    measurement = session.get(Measurement, measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return measurement


@app.delete("/measurements/{measurement_id}")
def delete_measurement(*, session: Session = Depends(get_session), measurement_id: int):
    measurement = session.get(Measurement, measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    session.delete(measurement)
    session.commit()
    return {"ok": True}


@app.get("/measurement_graphic/{measurement_id}", response_class=HTMLResponse)
@fastapi_chameleon.template("measurement_graphic.pt")
def show_measurement_graphic(
    *, session: Session = Depends(get_session), measurement_id: int, request: Request
):
    measurement = session.get(Measurement, measurement_id)
    return {"measurement": measurement, "domain": DOMAIN}
