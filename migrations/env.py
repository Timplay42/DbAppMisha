import os
import dotenv
import logging

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, text

from alembic import context
from Shared.Base import Base

from Services.Driver.model import Driver
from Services.Car.model import Car
from Services.Rate.model import Tariff
from Services.Route.model import Route, RouteTariff
from Services.Transportation.model import Shipment


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Загружаем переменные окружения из .env файла
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env')
config_proj = dotenv.dotenv_values(env_path)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Формируем URL для синхронного подключения (Alembic работает синхронно)
# Используем те же переменные окружения, что и в DBSession.py
db_user = config_proj.get('DB_USER')
db_password = config_proj.get('DB_PASSWORD')
db_host = config_proj.get('DB_HOST')
db_port = config_proj.get('DB_PORT')
db_name = config_proj.get('DB_NAME')

# Формируем синхронный URL (без +asyncpg, так как Alembic работает синхронно)
database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

config.set_main_option("sqlalchemy.url", database_url)

# Убеждаемся, что все модели зарегистрированы в Base.py.metadata
target_metadata = Base.metadata

# Отладочная информация: выводим список всех таблиц
logging.info(f"Registered tables in metadata: {list(target_metadata.tables.keys())}")


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Удаляем таблицу alembic_version, если она существует (для начала с чистого листа)
        # Это нужно, если вы удалили все миграции и хотите начать заново
        # ЗАКОММЕНТИРОВАНО: не удаляем автоматически, чтобы не потерять историю миграций
        # try:
        #     connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
        #     connection.commit()
        #     logging.info("Dropped alembic_version table to start fresh")
        # except Exception as e:
        #     logging.debug(f"Could not drop alembic_version table (might not exist): {e}")

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Сравнивать типы колонок
            compare_server_default=True,  # Сравнивать значения по умолчанию
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()