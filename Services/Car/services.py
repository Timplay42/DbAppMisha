# Services/Car/services.py
from sqlalchemy.orm import Session, joinedload
from Services.Car.model import Car
from typing import Dict, List


def get_all_cars(session: Session) -> List[Dict]:
    cars = session.query(Car).all()
    return [
        {
            "id": car.id,
            "brand": car.brand,
            "license_plate": car.license_plate,
            "load_capacity": car.load_capacity,
            "body_type": car.body_type,
            "fuel_consumption": car.fuel_consumption
        }
        for car in cars
    ]

# Services/driver/services.py
# Обновляем функцию get_all_cars_for_assignment:

def get_all_cars_for_assignment(session: Session) -> List[Dict]:
    """Получить все автомобили с информацией о назначении"""
    cars = session.query(Car).options(joinedload(Car.driver)).all()
    return [
        {
            "id": car.id,
            "brand": car.brand,
            "license_plate": car.license_plate,
            "body_type": car.body_type,
            "load_capacity": car.load_capacity,  # Добавляем это поле
            "fuel_consumption": car.fuel_consumption,  # Добавляем это поле
            "has_driver": car.driver is not None,
            "driver_info": f"{car.driver.full_name}" if car.driver else None,
            "full_info": f"{car.brand} - {car.license_plate}" +
                        (f" (водитель: {car.driver.full_name})" if car.driver else " (свободен)")
        }
        for car in cars
    ]


def get_car_by_id(session: Session, car_id: int) -> Car:
    """Получить машину по ID"""
    return session.query(Car).filter(Car.id == car_id).first()


def create_car(session: Session, **kwargs) -> Car:
    """Создать новую машину"""
    car = Car(**kwargs)
    session.add(car)
    session.commit()
    return car


def update_car(session: Session, car_id: int, **kwargs) -> bool:
    """Обновить данные машины"""
    car = session.query(Car).filter(Car.id == car_id).first()
    if not car:
        return False

    for key, value in kwargs.items():
        setattr(car, key, value)

    session.commit()
    return True


def delete_car(session: Session, car_id: int) -> bool:
    """Удалить машину"""
    car = session.query(Car).filter(Car.id == car_id).first()
    if not car:
        return False

    session.delete(car)
    session.commit()
    return True


# Services/Car/services.py - добавляем новые функции
from sqlalchemy.orm import Session, joinedload
from Services.Car.model import Car
from typing import Dict, List, Optional


def get_all_cars_with_drivers(session: Session) -> List[Dict]:
    """Получить все машины с информацией о водителях"""
    cars = session.query(Car).options(joinedload(Car.driver)).all()
    return [
        {
            "id": car.id,
            "brand": car.brand,
            "license_plate": car.license_plate,
            "load_capacity": car.load_capacity,
            "body_type": car.body_type,
            "fuel_consumption": car.fuel_consumption,
            "has_driver": car.driver is not None,
            "driver_name": car.driver.full_name if car.driver else None,
            "driver_id": car.driver.id if car.driver else None,
            "status": "Занята" if car.driver else "Свободна"
        }
        for car in cars
    ]


def get_free_cars(session: Session) -> List[Dict]:
    """Получить свободные машины (без водителя)"""
    cars = session.query(Car).filter(Car.driver == None).all()
    return [
        {
            "id": car.id,
            "brand": car.brand,
            "license_plate": car.license_plate,
            "load_capacity": car.load_capacity,
            "body_type": car.body_type,
            "fuel_consumption": car.fuel_consumption,
            "has_driver": False,
            "status": "Свободна"
        }
        for car in cars
    ]


def get_cars_by_load_capacity(session: Session, min_load: float) -> List[Dict]:
    """Получить машины с грузоподъемностью больше указанной"""
    cars = session.query(Car).filter(Car.load_capacity >= min_load).all()
    return [
        {
            "id": car.id,
            "brand": car.brand,
            "license_plate": car.license_plate,
            "load_capacity": car.load_capacity,
            "body_type": car.body_type,
            "fuel_consumption": car.fuel_consumption,
            "has_driver": car.driver is not None,
            "status": "Занята" if car.driver else "Свободна"
        }
        for car in cars
    ]


def get_cars_by_fuel_consumption(session: Session, max_fuel: float) -> List[Dict]:
    """Получить машины с расходом топлива меньше указанного"""
    cars = session.query(Car).filter(Car.fuel_consumption <= max_fuel).all()
    return [
        {
            "id": car.id,
            "brand": car.brand,
            "license_plate": car.license_plate,
            "load_capacity": car.load_capacity,
            "body_type": car.body_type,
            "fuel_consumption": car.fuel_consumption,
            "has_driver": car.driver is not None,
            "status": "Занята" if car.driver else "Свободна"
        }
        for car in cars
    ]


