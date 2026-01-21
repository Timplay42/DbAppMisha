# Models/shipment.py
from __future__ import annotations
import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, ForeignKey, DateTime
from typing import Optional

from Shared.Base import Base


class Shipment(Base):
    __tablename__ = "shipment"

    shipment_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    cargo_weight: Mapped[float] = mapped_column(Float)  # вес груза в
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, in_transit, delivered, cancelled

    # Внешние ключи
    car_id: Mapped[int] = mapped_column(ForeignKey("car.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("driver.id"))
    route_id: Mapped[int] = mapped_column(ForeignKey("route.id"))
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariff.id"))

    # Расчетные поля (будут вычисляться автоматически)
    total_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Отношения (без Car и Route отношений, т.к. они не нужны напрямую)
    route: Mapped["Route"] = relationship("Route")
    car: Mapped["Car"] = relationship("Car")
    driver: Mapped["Driver"] = relationship(back_populates="shipments")
    tariff: Mapped["Tariff"] = relationship(back_populates="shipments")

    def __repr__(self) -> str:
        return f"Shipment(id={self.id}, status='{self.status}', type='{self.cargo_type}')"