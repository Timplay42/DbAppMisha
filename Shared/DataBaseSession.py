#import dotenv
import sqlalchemy.engine.url as SQURL
#from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

#current_dir = Path(__file__).parent.parent
#env_path = current_dir / '.env'

#config_app = dotenv.dotenv_values(env_path)


class SyncDatabaseSessions:

    def __init__(self):
        # Захардкоженные настройки
        self.URL = SQURL.URL.create(
            drivername="postgresql+psycopg2",
            username="postgres",          # DB_USER
            password="postgres",          # DB_PASSWORD
            host="localhost",             # DB_HOST
            port=5432,                    # DB_PORT
            database="postgres",          # DB_NAME
        )

        self.engine = create_engine(
            self.URL,
            pool_pre_ping=True,
            echo=False
        )

        self.factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False
        )

    def get_session(self) -> Session:
        return self.factory()


SyncDatabase = SyncDatabaseSessions()