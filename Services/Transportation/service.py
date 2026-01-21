# Services/shipment/services.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, or_
from typing import Dict, List, Optional
import datetime

from Services.Transportation.model import Shipment
from Services.Car.model import Car
from Services.Driver.model import Driver
from Services.Route.model import Route
from Services.Rate.model import Tariff


def get_all_shipments(session: Session, auto_recalculate: bool = True) -> List[Dict]:
    """Получить все перевозки с информацией из связанных таблиц"""
    shipments = session.query(Shipment).options(
        joinedload(Shipment.driver),
        joinedload(Shipment.tariff)
    ).order_by(desc(Shipment.shipment_date)).all()

    result = []
    updated_shipments = []  # Для хранения перевозок, которые нужно обновить

    for shipment in shipments:
        # Получаем связанные данные через отдельные запросы
        car = session.query(Car).filter(Car.id == shipment.car_id).first()
        route = session.query(Route).filter(Route.id == shipment.route_id).first()

        # Рассчитываем стоимость
        total_cost = 0
        if route and shipment.tariff:
            cost = route.distance_km * shipment.tariff.price_per_km
            total_cost = max(cost, shipment.tariff.min_price)

            # Если включен авто-перерасчет и стоимость изменилась
            if auto_recalculate and shipment.total_cost != total_cost:
                shipment.total_cost = total_cost
                updated_shipments.append(shipment)

        result.append({
            "id": shipment.id,
            "shipment_date": shipment.shipment_date.isoformat(),
            "cargo_weight": shipment.cargo_weight,
            "status": shipment.status,
            "total_cost": total_cost,
            "car_id": shipment.car_id,
            "car_info": {
                "brand": car.brand if car else None,
                "license_plate": car.license_plate if car else None,
                "load_capacity": car.load_capacity if car else None
            } if car else None,
            "driver_id": shipment.driver_id,
            "driver_info": {
                "full_name": shipment.driver.full_name if shipment.driver else None,
                "license_number": shipment.driver.license_number if shipment.driver else None,
                "car_id": shipment.driver.car_id if shipment.driver else None
            } if shipment.driver else None,
            "route_id": shipment.route_id,
            "route_info": {
                "origin": route.origin if route else None,
                "destination": route.destination if route else None,
                "distance_km": route.distance_km if route else None,
                "avg_time_hours": route.avg_time_hours if route else None
            } if route else None,
            "tariff_id": shipment.tariff_id,
            "tariff_info": {
                "price_per_km": shipment.tariff.price_per_km if shipment.tariff else None,
                "min_price": shipment.tariff.min_price if shipment.tariff else None,
                "date_start": shipment.tariff.date_start.isoformat() if shipment.tariff else None,
                "date_end": shipment.tariff.date_end.isoformat() if shipment.tariff and shipment.tariff.date_end else None
            } if shipment.tariff else None
        })

    # Сохраняем обновленные стоимости, если есть
    if updated_shipments and auto_recalculate:
        session.commit()
        print(f"✅ Автоматически обновлено {len(updated_shipments)} перевозок")

    return result

def get_active_tariffs(session: Session, date: datetime.datetime = None) -> List[Dict]:
    """Получить активные тарифы на указанную дату"""
    if date is None:
        date = datetime.datetime.now()

    query = session.query(Tariff).filter(
        Tariff.date_start <= date,
        or_(Tariff.date_end == None, Tariff.date_end >= date)
    )

    tariffs = query.all()

    return [
        {
            "id": tariff.id,
            "price_per_km": tariff.price_per_km,
            "min_price": tariff.min_price,
            "date_start": tariff.date_start.isoformat(),
            "date_end": tariff.date_end.isoformat() if tariff.date_end else None,
            "full_info": f"{tariff.price_per_km} руб/км (мин. {tariff.min_price} руб)"
        }
        for tariff in tariffs
    ]


def get_available_cars_with_drivers(session: Session, cargo_weight: float = 0) -> List[Dict]:
    """Получить автомобили с назначенными водителями"""
    cars = session.query(Car).options(joinedload(Car.driver)).all()

    result = []
    for car in cars:
        # Проверяем грузоподъемность
        if cargo_weight > 0 and car.load_capacity * 1000 < cargo_weight:
            continue  # Пропускаем, если груз слишком тяжелый

        result.append({
            "id": car.id,
            "brand": car.brand,
            "license_plate": car.license_plate,
            "load_capacity": car.load_capacity,
            "body_type": car.body_type,
            "has_driver": car.driver is not None,
            "driver_id": car.driver.id if car.driver else None,
            "driver_name": car.driver.full_name if car.driver else None,
            "driver_license": car.driver.license_number if car.driver else None,
            "full_info": f"{car.brand} ({car.license_plate}) - {car.driver.full_name if car.driver else 'Без водителя'}"
        })

    return result


def get_all_drivers(session: Session) -> List[Dict]:
    """Получить всех водителей"""
    drivers = session.query(Driver).all()
    return [
        {
            "id": driver.id,
            "full_name": driver.full_name,
            "license_number": driver.license_number,
            "car_id": driver.car_id,
            "has_car": driver.car_id is not None
        }
        for driver in drivers
    ]


def get_all_routes(session: Session) -> List[Dict]:
    """Получить все маршруты"""
    routes = session.query(Route).all()
    return [
        {
            "id": route.id,
            "origin": route.origin,
            "destination": route.destination,
            "distance_km": route.distance_km,
            "avg_time_hours": route.avg_time_hours,
            "road_type": route.road_type,
            "full_info": f"{route.origin} → {route.destination} ({route.distance_km} км, {route.avg_time_hours} ч)"
        }
        for route in routes
    ]


def create_shipment(session: Session, **kwargs) -> Shipment:
    """Создать новую перевозку"""
    # Проверяем, что выбранный тариф активен
    if 'tariff_id' in kwargs and 'shipment_date' in kwargs:
        tariff = session.query(Tariff).filter(Tariff.id == kwargs['tariff_id']).first()
        shipment_date = kwargs['shipment_date']

        if isinstance(shipment_date, str):
            shipment_date = datetime.datetime.fromisoformat(shipment_date)

        if tariff:
            if tariff.date_start > shipment_date:
                raise ValueError(f"Тариф начинает действовать с {tariff.date_start}")

            if tariff.date_end and tariff.date_end < shipment_date:
                raise ValueError(f"Тариф действовал до {tariff.date_end}")

    # Проверяем, что автомобиль существует и может перевезти груз
    if 'car_id' in kwargs and 'cargo_weight' in kwargs:
        car = session.query(Car).filter(Car.id == kwargs['car_id']).first()
        if car and car.load_capacity * 1000 < kwargs['cargo_weight']:
            raise ValueError(f"Груз слишком тяжелый для автомобиля {car.brand} (макс: {car.load_capacity * 1000} кг)")

    shipment = Shipment(**kwargs)
    session.add(shipment)
    session.commit()
    return shipment


def update_shipment(session: Session, shipment_id: int, **kwargs) -> bool:
    """Обновить данные перевозки"""
    shipment = session.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        return False

    for key, value in kwargs.items():
        setattr(shipment, key, value)

    session.commit()
    return True


def delete_shipment(session: Session, shipment_id: int) -> bool:
    """Удалить перевозку"""
    shipment = session.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        return False

    session.delete(shipment)
    session.commit()
    return True


def calculate_shipment_cost(session: Session, shipment_id: int) -> float:
    """Рассчитать стоимость перевозки"""
    shipment = session.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        return 0

    route = session.query(Route).filter(Route.id == shipment.route_id).first()
    tariff = session.query(Tariff).filter(Tariff.id == shipment.tariff_id).first()

    if not route or not tariff:
        return 0

    cost = route.distance_km * tariff.price_per_km
    return max(cost, tariff.min_price)


def get_shipments_with_filters(session: Session, **filters) -> List[Dict]:
    """Получить перевозки с фильтрами"""
    from sqlalchemy import and_, or_

    query = session.query(Shipment).options(
        joinedload(Shipment.driver),
        joinedload(Shipment.tariff)
    )

    conditions = []

    # Фильтр по статусу
    if "status" in filters:
        status_list = filters["status"]
        if isinstance(status_list, str):
            status_list = [status_list]
        conditions.append(Shipment.status.in_(status_list))

    # Фильтр по дате (от)
    if "date_from" in filters:
        date_from = filters["date_from"]
        if isinstance(date_from, str):
            date_from = datetime.datetime.fromisoformat(date_from)
        conditions.append(Shipment.shipment_date >= date_from)

    # Фильтр по дате (до)
    if "date_to" in filters:
        date_to = filters["date_to"]
        if isinstance(date_to, str):
            date_to = datetime.datetime.fromisoformat(date_to)
        conditions.append(Shipment.shipment_date <= date_to)

    # Фильтр по автомобилю
    if "car_id" in filters:
        conditions.append(Shipment.car_id == filters["car_id"])

    # Фильтр по водителю
    if "driver_id" in filters:
        conditions.append(Shipment.driver_id == filters["driver_id"])

    # Фильтр по маршруту
    if "route_id" in filters:
        conditions.append(Shipment.route_id == filters["route_id"])

    # Фильтр по тарифу
    if "tariff_id" in filters:
        conditions.append(Shipment.tariff_id == filters["tariff_id"])

    # Фильтр по весу (от)
    if "weight_from" in filters:
        conditions.append(Shipment.cargo_weight >= filters["weight_from"])

    # Фильтр по весу (до)
    if "weight_to" in filters:
        conditions.append(Shipment.cargo_weight <= filters["weight_to"])

    # Применяем условия
    if conditions:
        query = query.filter(and_(*conditions))

    shipments = query.order_by(Shipment.shipment_date.desc()).all()

    # Преобразуем в словари с полной информацией
    result = []
    for shipment in shipments:
        # Получаем связанные данные через отдельные запросы
        car = session.query(Car).filter(Car.id == shipment.car_id).first()
        route = session.query(Route).filter(Route.id == shipment.route_id).first()

        # Рассчитываем стоимость
        total_cost = 0
        if route and shipment.tariff:
            cost = route.distance_km * shipment.tariff.price_per_km
            total_cost = max(cost, shipment.tariff.min_price)

        result.append({
            "id": shipment.id,
            "shipment_date": shipment.shipment_date.isoformat(),
            "cargo_weight": shipment.cargo_weight,
            "status": shipment.status,
            "total_cost": total_cost,
            "car_id": shipment.car_id,
            "car_info": {
                "brand": car.brand if car else None,
                "license_plate": car.license_plate if car else None,
                "load_capacity": car.load_capacity if car else None
            } if car else None,
            "driver_id": shipment.driver_id,
            "driver_info": {
                "full_name": shipment.driver.full_name if shipment.driver else None,
                "license_number": shipment.driver.license_number if shipment.driver else None,
                "car_id": shipment.driver.car_id if shipment.driver else None
            } if shipment.driver else None,
            "route_id": shipment.route_id,
            "route_info": {
                "origin": route.origin if route else None,
                "destination": route.destination if route else None,
                "distance_km": route.distance_km if route else None,
                "avg_time_hours": route.avg_time_hours if route else None
            } if route else None,
            "tariff_id": shipment.tariff_id,
            "tariff_info": {
                "price_per_km": shipment.tariff.price_per_km if shipment.tariff else None,
                "min_price": shipment.tariff.min_price if shipment.tariff else None,
                "date_start": shipment.tariff.date_start.isoformat() if shipment.tariff else None,
                "date_end": shipment.tariff.date_end.isoformat() if shipment.tariff and shipment.tariff.date_end else None
            } if shipment.tariff else None
        })

    return result