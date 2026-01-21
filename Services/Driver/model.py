import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Integer, Float, Date, ForeignKey
)
from typing import Optional, List
from Shared.Base import Base


class Driver(Base):
    __tablename__ = "driver"

    full_name: Mapped[str] = mapped_column(String(150))
    license_number: Mapped[str] = mapped_column(String(50), unique=True)

    license_category: Mapped[str] = mapped_column(String(10))
    experience_years: Mapped[int]
    hire_date: Mapped[datetime.datetime]

    car_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("car.id"), unique=True
    )

    car: Mapped[Optional['Car']] = relationship(back_populates="driver")
    shipments: Mapped[List["Shipment"]] = relationship(back_populates="driver")
