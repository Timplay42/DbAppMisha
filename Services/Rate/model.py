# Models/tariff.py
from __future__ import annotations
import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime
from typing import Optional, List

from Shared.Base import Base


class Tariff(Base):
    __tablename__ = "tariff"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    price_per_km: Mapped[float] = mapped_column(Float)
    cargo_type: Mapped[str] = mapped_column(String(50))
    min_price: Mapped[float] = mapped_column(Float)
    date_start: Mapped[datetime.datetime] = mapped_column(DateTime)
    date_end: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    shipments: Mapped[List["Shipment"]] = relationship(back_populates="tariff")
    route_tariffs: Mapped[List["RouteTariff"]] = relationship(back_populates="tariff")

    def __repr__(self) -> str:
        return f"Tariff(id={self.id}, cargo_type='{self.cargo_type}', price={self.price_per_km} руб/км)"

    def is_active(self, date: datetime.datetime = None) -> bool:
        """Проверить, активен ли тариф на указанную дату"""
        if date is None:
            date = datetime.datetime.now()

        if self.date_start > date:
            return False

        if self.date_end and self.date_end < date:
            return False

        return True

    def get_active_period(self) -> str:
        """Получить строковое представление периода действия"""
        date_format = "%d.%m.%Y"
        start_str = self.date_start.strftime(date_format)

        if self.date_end:
            end_str = self.date_end.strftime(date_format)
            return f"{start_str} - {end_str}"
        else:
            return f"с {start_str} (бессрочно)"