import datetime
import uuid

from sqlalchemy import text
from sqlalchemy.orm import Session

from Services.Transportation.model import Shipment


# services/route_service.py



def create_route(
    session: Session,
    origin: str,
    destination: str,
    distance_km: float,
    avg_time_hours: float,
    road_type: str,
):
    session.execute(
        text("""
        INSERT INTO route (
            id, origin, destination,
            distance_km, avg_time_hours, road_type,
            created_at, updated_at, active
        )
        VALUES (
            :id, :origin, :destination,
            :distance_km, :avg_time_hours, :road_type,
            :created_at, :updated_at, :active
        )
        """),
        {
            "id": uuid.uuid4(),
            "origin": origin,
            "destination": destination,
            "distance_km": distance_km,
            "avg_time_hours": avg_time_hours,
            "road_type": road_type,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "active": True
        }
    )
    session.commit()


def link_route_tariff(
    session: Session,
    route_id: int,
    tariff_id: int
):
    session.execute(
        text("""
        INSERT INTO route_tariff (id, route_id, tariff_id, created_at, updated_at, active)
        VALUES (:id, :route_id, :tariff_id, :created_at, :updated_at, :active)
        """),
        {
            "id": uuid.uuid4(),
            "route_id": route_id,
            "tariff_id": tariff_id,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "active": True
        }
    )
    session.commit()


def get_all_routes(session: Session):
    return session.execute(
        text("""
        SELECT id, origin, destination, distance_km, avg_time_hours, road_type
        FROM route
        ORDER BY created_at
        """)
    ).mappings().all()


def delete_route(session: Session, route_id):
    """Удалить маршрут с проверкой связанных записей"""
    try:
        # Сначала проверяем, есть ли связанные перевозки
        shipment_count = session.query(Shipment).filter(Shipment.route_id == route_id).count()

        if shipment_count > 0:
            return False, f"Нельзя удалить маршрут, так как он связан с {shipment_count} перевозками"

        # Удаляем связи с тарифами
        session.execute(
            text("DELETE FROM route_tariff WHERE route_id = :route_id"),
            {"route_id": route_id}
        )

        # Теперь удаляем маршрут
        session.execute(
            text("DELETE FROM route WHERE id = :id"),
            {"id": route_id}
        )

        session.commit()
        return True, "Маршрут успешно удален"

    except Exception as e:
        session.rollback()
        return False, f"Ошибка при удалении: {str(e)}"

def update_route(
    session: Session,
    route_id,
    origin: str,
    destination: str,
    distance_km: float,
    avg_time_hours: float,
    road_type: str
):
    session.execute(
        text("""
        UPDATE route
        SET origin = :origin,
            destination = :destination,
            distance_km = :distance_km,
            avg_time_hours = :avg_time_hours,
            road_type = :road_type
        WHERE id = :id
        """),
        {
            "id": route_id,
            "origin": origin,
            "destination": destination,
            "distance_km": distance_km,
            "avg_time_hours": avg_time_hours,
            "road_type": road_type
        }
    )
    session.commit()


def get_routes_with_filters(session: Session, **filters):
    """Получить маршруты с фильтрами"""
    query = """
        SELECT id, origin, destination, distance_km, avg_time_hours, road_type
        FROM route
        WHERE active = true
    """

    params = {}
    conditions = []

    if "min_distance" in filters:
        conditions.append("distance_km >= :min_distance")
        params["min_distance"] = filters["min_distance"]

    if "max_distance" in filters:
        conditions.append("distance_km <= :max_distance")
        params["max_distance"] = filters["max_distance"]

    if "road_type" in filters:
        conditions.append("LOWER(road_type) LIKE :road_type")
        params["road_type"] = f"%{filters['road_type'].lower()}%"

    if "origin" in filters:
        conditions.append("LOWER(origin) LIKE :origin")
        params["origin"] = f"%{filters['origin'].lower()}%"

    if "destination" in filters:
        conditions.append("LOWER(destination) LIKE :destination")
        params["destination"] = f"%{filters['destination'].lower()}%"

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " ORDER BY created_at DESC"

    return session.execute(text(query), params).mappings().all()


def get_route_by_id(session: Session, route_id):
    """Получить маршрут по ID"""
    result = session.execute(
        text("""
        SELECT id, origin, destination, distance_km, avg_time_hours, road_type
        FROM route
        WHERE id = :id AND active = true
        """),
        {"id": route_id}
    ).mappings().first()
    return result


def get_route_statistics(session: Session):
    """Получить статистику по маршрутам"""
    result = session.execute(
        text("""
        SELECT 
            COUNT(*) as total_routes,
            SUM(distance_km) as total_distance,
            AVG(distance_km) as avg_distance,
            AVG(avg_time_hours) as avg_time,
            MIN(distance_km) as min_distance,
            MAX(distance_km) as max_distance
        FROM route
        WHERE active = true
        """)
    ).mappings().first()
    return result