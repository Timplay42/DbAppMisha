from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Integer, Float, Date, ForeignKey
)
from typing import Optional, List

from Shared.Base import Base

class Car(Base):
    __tablename__ = "car"

    brand: Mapped[str] = mapped_column(String(100))
    license_plate: Mapped[str] = mapped_column(String(20), unique=True)

    load_capacity: Mapped[float] = mapped_column(Float)  # т
    body_type: Mapped[str] = mapped_column(String(50))
    fuel_consumption: Mapped[float] = mapped_column(Float)  # л/100км

    from Services.Driver.model import Driver
    from Services.Transportation.model import Shipment
    driver: Mapped["Driver"] = relationship(back_populates="car", uselist=False)
    shipments: Mapped[List["Shipment"]] = relationship(back_populates="car")
