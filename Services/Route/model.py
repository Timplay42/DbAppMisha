import uuid

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Integer, Float, Date, ForeignKey
)
from typing import Optional, List

from Shared.Base import Base



class Route(Base):
    __tablename__ = "route"

    origin: Mapped[str] = mapped_column(String(100))
    destination: Mapped[str] = mapped_column(String(100))

    distance_km: Mapped[float]
    avg_time_hours: Mapped[float]
    road_type: Mapped[str] = mapped_column(String(50))

    shipments: Mapped[List["Shipment"]] = relationship(back_populates="route")
    route_tariffs: Mapped[List["RouteTariff"]] = relationship(back_populates="route")


class RouteTariff(Base):
    from Services.Rate.model import Tariff

    __tablename__ = "route_tariff"

    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("route.id"))
    tariff_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tariff.id"))

    route: Mapped[Route] = relationship(back_populates="route_tariffs")
    tariff: Mapped[Tariff] = relationship(back_populates="route_tariffs")
