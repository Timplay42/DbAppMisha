# Services/tariff/services.py
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import Dict, List, Optional
import datetime

from Services.Rate.model import Tariff


def get_all_tariffs(session: Session) -> List[Dict]:
    """Получить все тарифы"""
    tariffs = session.query(Tariff).order_by(desc(Tariff.date_start)).all()

    return [
        {
            "id": tariff.id,
            "price_per_km": tariff.price_per_km,
            "cargo_type": tariff.cargo_type,
            "min_price": tariff.min_price,
            "date_start": tariff.date_start.isoformat(),
            "date_end": tariff.date_end.isoformat() if tariff.date_end else None,
            "description": tariff.description,
            "is_active": tariff.is_active(),
            "active_period": tariff.get_active_period()
        }
        for tariff in tariffs
    ]


def get_active_tariffs(session: Session, date: datetime.datetime = None) -> List[Dict]:
    """Получить активные тарифы на указанную дату"""
    if date is None:
        date = datetime.datetime.now()

    tariffs = session.query(Tariff).filter(
        Tariff.date_start <= date,
        or_(Tariff.date_end == None, Tariff.date_end >= date)
    ).order_by(desc(Tariff.date_start)).all()

    return [
        {
            "id": tariff.id,
            "price_per_km": tariff.price_per_km,
            "cargo_type": tariff.cargo_type,
            "min_price": tariff.min_price,
            "date_start": tariff.date_start.isoformat(),
            "date_end": tariff.date_end.isoformat() if tariff.date_end else None,
            "description": tariff.description,
            "full_info": f"{tariff.cargo_type}: {tariff.price_per_km} руб/км (мин. {tariff.min_price} руб)"
        }
        for tariff in tariffs
    ]


def get_tariff_by_id(session: Session, tariff_id: int) -> Optional[Tariff]:
    """Получить тариф по ID"""
    return session.query(Tariff).filter(Tariff.id == tariff_id).first()


def get_tariffs_by_cargo_type(session: Session, cargo_type: str) -> List[Dict]:
    """Получить тарифы по типу груза"""
    tariffs = session.query(Tariff).filter(
        Tariff.cargo_type == cargo_type
    ).order_by(desc(Tariff.date_start)).all()

    return [
        {
            "id": tariff.id,
            "price_per_km": tariff.price_per_km,
            "min_price": tariff.min_price,
            "date_start": tariff.date_start.isoformat(),
            "date_end": tariff.date_end.isoformat() if tariff.date_end else None,
            "is_active": tariff.is_active()
        }
        for tariff in tariffs
    ]


def create_tariff(session: Session, **kwargs) -> Tariff:
    """Создать новый тариф"""
    # Преобразуем строки дат в datetime
    if 'date_start' in kwargs and isinstance(kwargs['date_start'], str):
        kwargs['date_start'] = datetime.datetime.fromisoformat(kwargs['date_start'])

    if 'date_end' in kwargs and isinstance(kwargs['date_end'], str):
        if kwargs['date_end']:  # Если не пустая строка
            kwargs['date_end'] = datetime.datetime.fromisoformat(kwargs['date_end'])
        else:
            kwargs['date_end'] = None

    # Дополнительная проверка на стороне Python перед сохранением
    if kwargs.get('date_end') is not None:
        if kwargs['date_end'] <= kwargs['date_start']:
            raise ValueError(
                f"Дата окончания ({kwargs['date_end']}) должна быть позже даты начала ({kwargs['date_start']})")

    # Проверка, что дата начала не слишком далеко в прошлом (опционально)
    if kwargs['date_start'] < datetime.datetime.now() - datetime.timedelta(days=365):
        # Можно вывести предупреждение или запросить подтверждение
        print(f"Внимание: Дата начала тарифа более года назад: {kwargs['date_start']}")

    tariff = Tariff(**kwargs)
    session.add(tariff)
    session.commit()
    return tariff


def update_tariff(session: Session, tariff_id: int, **kwargs) -> bool:
    """Обновить тариф"""
    tariff = session.query(Tariff).filter(Tariff.id == tariff_id).first()
    if not tariff:
        return False

    # Преобразуем строки дат в datetime
    if 'date_start' in kwargs and isinstance(kwargs['date_start'], str):
        kwargs['date_start'] = datetime.datetime.fromisoformat(kwargs['date_start'])

    if 'date_end' in kwargs and isinstance(kwargs['date_end'], str):
        if kwargs['date_end']:  # Если не пустая строка
            kwargs['date_end'] = datetime.datetime.fromisoformat(kwargs['date_end'])
        else:
            kwargs['date_end'] = None

    # Проверка дат перед обновлением
    date_start = kwargs.get('date_start', tariff.date_start)
    date_end = kwargs.get('date_end', tariff.date_end)

    if date_end is not None and date_end <= date_start:
        raise ValueError(f"Дата окончания ({date_end}) должна быть позже даты начала ({date_start})")

    for key, value in kwargs.items():
        setattr(tariff, key, value)

    session.commit()
    return True


def delete_tariff(session: Session, tariff_id: int) -> bool:
    """Удалить тариф"""
    tariff = session.query(Tariff).filter(Tariff.id == tariff_id).first()
    if not tariff:
        return False

    # Проверяем, нет ли связанных перевозок
    if tariff.shipments:
        return False  # Не удаляем, если есть связанные перевозки

    session.delete(tariff)
    session.commit()
    return True


def get_cargo_types(session: Session) -> List[str]:
    """Получить все типы грузов из тарифов"""
    cargo_types = session.query(Tariff.cargo_type).distinct().all()
    return [cargo_type[0] for cargo_type in cargo_types]


# В Services/tariff/services.py добавьте:

