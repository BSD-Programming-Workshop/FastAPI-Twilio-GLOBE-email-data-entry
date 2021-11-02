from datetime import datetime
from typing import List, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel


class ObserverBase(SQLModel):
    phone: str
    email: str

    class Config:
        anystr_strip_whitespace = True
        anystr_lower = True


class Observer(ObserverBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    measurements: List["Measurement"] = Relationship(
        back_populates="observer", sa_relationship_kwargs={"cascade": "all,delete"}
    )


class ObserverCreate(ObserverBase):
    pass


class ObserverRead(ObserverBase):
    id: int


class MeasurementBase(SQLModel):
    temperaturescale: str
    temperature: int
    organizationid: int
    siteid: int
    date_time: Optional[datetime] = Field(
        sa_column=Column(DateTime, default=datetime.utcnow)
    )
    observer_id: Optional[int] = Field(default=None, foreign_key="observer.id")

    class Config:
        anystr_strip_whitespace = True
        anystr_lower = True


class Measurement(MeasurementBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    observer: Optional[Observer] = Relationship(back_populates="measurements")


class MeasurementCreate(MeasurementBase):
    pass


class MeasurementRead(MeasurementBase):
    id: int
