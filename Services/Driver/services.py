# Services/driver/services.py
from sqlalchemy.orm import Session, joinedload
from Services.Driver.model import Driver
from Services.Car.model import Car
from typing import Dict, List, Optional
import datetime


def get_all_drivers_with_cars(session: Session) -> List[Dict]:
    """Получить всех водителей с информацией об автомобилях"""
    drivers = session.query(Driver).options(
        joinedload(Driver.car)  # Жадная загрузка автомобиля
    ).all()

    return [
        {
            "id": driver.id,
            "full_name": driver.full_name,
            "license_number": driver.license_number,
            "license_category": driver.license_category,
            "experience_years": driver.experience_years,
            "hire_date": driver.hire_date.isoformat(),
            "car_id": driver.car_id,
            "car_info": {
                "id": driver.car.id if driver.car else None,
                "brand": driver.car.brand if driver.car else None,
                "license_plate": driver.car.license_plate if driver.car else None,
                "full_info": f"{driver.car.brand} ({driver.car.license_plate})"
                if driver.car else "Не назначен"
            } if driver.car else {
                "id": None,
                "brand": None,
                "license_plate": None,
                "full_info": "Не назначен"
            }
        }
        for driver in drivers
    ]


def get_all_available_cars(session: Session) -> List[Dict]:
    """Получить все автомобили без водителей"""
    cars = session.query(Car).filter(Car.driver == None).all()
    return [
        {
            "id": car.id,
            "full_info": f"{car.brand} - {car.license_plate} ({car.body_type})"
        }
        for car in cars
    ]


def get_all_cars_for_assignment(session: Session) -> List[Dict]:
    """Получить все автомобили с информацией о назначении"""
    cars = session.query(Car).options(joinedload(Car.driver)).all()
    return [
        {
            "id": car.id,
            "brand": car.brand,
            "license_plate": car.license_plate,
            "body_type": car.body_type,
            "has_driver": car.driver is not None,
            "driver_info": f"{car.driver.full_name}" if car.driver else None,
            "full_info": f"{car.brand} - {car.license_plate}" +
                         (f" (водитель: {car.driver.full_name})" if car.driver else " (свободен)")
        }
        for car in cars
    ]


def assign_driver_to_car(session: Session, driver_id: int, car_id: Optional[int]) -> bool:
    """Назначить или открепить водителя от автомобиля"""
    driver = session.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        return False

    # Если указан car_id, проверяем автомобиль
    if car_id:
        car = session.query(Car).filter(Car.id == car_id).first()
        if not car:
            return False

        # Проверяем, не занят ли автомобиль другим водителем
        existing_driver = session.query(Driver).filter(Driver.car_id == car_id).first()
        if existing_driver and existing_driver.id != driver_id:
            return False

        driver.car_id = car_id
    else:
        # Открепляем водителя от автомобиля
        driver.car_id = None

    session.commit()
    return True


def swap_driver_car(session: Session, driver1_id: int, driver2_id: int) -> bool:
    """Поменять местами автомобили между водителями"""
    driver1 = session.query(Driver).filter(Driver.id == driver1_id).first()
    driver2 = session.query(Driver).filter(Driver.id == driver2_id).first()

    if not driver1 or not driver2:
        return False

    # Сохраняем текущие автомобили
    car1_id = driver1.car_id
    car2_id = driver2.car_id

    # Меняем местами
    driver1.car_id = car2_id
    driver2.car_id = car1_id

    session.commit()
    return True


# Остальные функции остаются без изменений
def get_driver_by_id(session: Session, driver_id: int) -> Optional[Driver]:
    return session.query(Driver).filter(Driver.id == driver_id).first()


def create_driver(session: Session, **kwargs) -> Driver:
    """Создать нового водителя"""
    # Преобразуем дату приема
    if 'hire_date' in kwargs and isinstance(kwargs['hire_date'], str):
        kwargs['hire_date'] = datetime.date.fromisoformat(kwargs['hire_date'])

    # Проверка стажа перед созданием (дополнительная проверка на стороне Python)
    if 'experience_years' in kwargs and kwargs['experience_years'] > 40:
        raise ValueError(f"Стаж водителя не может превышать 40 лет. Указано: {kwargs['experience_years']} лет.")

    # Проверка по дате приема (если указана)
    if 'hire_date' in kwargs:
        hire_date = kwargs['hire_date']
        if isinstance(hire_date, str):
            hire_date = datetime.date.fromisoformat(hire_date)

        # Рассчитываем стаж по дате приема
        today = datetime.date.today()
        years_experience_from_hire = today.year - hire_date.year

        # Корректировка, если день рождения в этом году еще не наступил
        if (today.month, today.day) < (hire_date.month, hire_date.day):
            years_experience_from_hire -= 1

        if years_experience_from_hire > 40:
            raise ValueError(f"По дате приема стаж водителя превышает 40 лет. "
                             f"Стаж: {years_experience_from_hire} лет (дата приема: {hire_date}).")

        # Проверка минимального возраста (18 лет)
        min_age_date = today - datetime.timedelta(days=18 * 365)
        if hire_date < min_age_date:
            # Это предупреждение, а не ошибка - некоторые водители могут быть приняты в молодом возрасте
            print(f"Внимание: Водитель принят на работу в очень молодом возрасте "
                  f"(дата приема: {hire_date})")

    driver = Driver(**kwargs)
    session.add(driver)
    session.commit()
    return driver


def update_driver(session: Session, driver_id: int, **kwargs) -> bool:
    """Обновить данные водителя"""
    driver = session.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        return False

    # Проверка стажа перед обновлением
    if 'experience_years' in kwargs and kwargs['experience_years'] > 40:
        raise ValueError(f"Стаж водителя не может превышать 40 лет. Указано: {kwargs['experience_years']} лет.")

    # Проверка по дате приема
    if 'hire_date' in kwargs:
        hire_date_value = kwargs['hire_date']
        if isinstance(hire_date_value, str):
            hire_date_value = datetime.date.fromisoformat(hire_date_value)

        # Рассчитываем стаж по дате приема
        today = datetime.date.today()
        years_experience_from_hire = today.year - hire_date_value.year

        # Корректировка
        if (today.month, today.day) < (hire_date_value.month, hire_date_value.day):
            years_experience_from_hire -= 1

        if years_experience_from_hire > 40:
            raise ValueError(f"По дате приема стаж водителя превышает 40 лет. "
                             f"Стаж: {years_experience_from_hire} лет (дата приема: {hire_date_value}).")

    for key, value in kwargs.items():
        if key == 'hire_date' and isinstance(value, str):
            value = datetime.date.fromisoformat(value)
        setattr(driver, key, value)

    session.commit()
    return True



def delete_driver(session: Session, driver_id: int) -> bool:
    """Удалить водителя"""
    try:
        driver = session.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            return False

        # Если есть активные перевозки, запрещаем удаление (дополнительная проверка на стороне Python)
        from Services.Transportation.model import Shipment
        from sqlalchemy import and_

        active_shipments = session.query(Shipment).filter(
            and_(
                Shipment.driver_id == driver_id,
                Shipment.status.in_(["pending", "in_transit"])
            )
        ).count()

        if active_shipments > 0:
            raise ValueError(f"У водителя есть активные перевозки ({active_shipments} шт.)")

        session.delete(driver)
        session.commit()
        return True

    except Exception as e:
        session.rollback()
        # Пробрасываем исключение дальше, чтобы GUI мог его обработать
        raise e