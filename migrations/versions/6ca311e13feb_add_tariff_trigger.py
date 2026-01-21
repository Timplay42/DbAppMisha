"""add_tariff_trigger

Revision ID: 6ca311e13feb
Revises: 6a7b765bd512
Create Date: 2026-01-20 22:28:33.816547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6ca311e13feb'
down_revision: Union[str, Sequence[str], None] = '6a7b765bd512'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Функция триггера для перерасчета стоимости перевозок
    op.execute("""
        CREATE OR REPLACE FUNCTION recalc_shipment_on_tariff_change()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Если изменилась цена за км или минимальная цена
            IF OLD.price_per_km != NEW.price_per_km OR OLD.min_price != NEW.min_price THEN
                -- Пересчитываем стоимость всех активных перевозок с этим тарифом
                UPDATE shipment s
                SET total_cost = GREATEST(r.distance_km * NEW.price_per_km, NEW.min_price)
                FROM route r
                WHERE s.route_id = r.id
                  AND s.tariff_id = NEW.id
                  AND s.status IN ('pending', 'in_transit');
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        -- Создаем триггер
        CREATE TRIGGER recalc_shipment_cost_trigger
            AFTER UPDATE OF price_per_km, min_price
            ON tariff
            FOR EACH ROW
            EXECUTE FUNCTION recalc_shipment_on_tariff_change();
    """)


def downgrade():
    # Удаляем триггер и функцию
    op.execute("DROP TRIGGER IF EXISTS recalc_shipment_cost_trigger ON tariff;")
    op.execute("DROP FUNCTION IF EXISTS recalc_shipment_on_tariff_change();")