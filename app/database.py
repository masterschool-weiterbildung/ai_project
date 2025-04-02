import json
from contextlib import contextmanager
from app.models import *
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine
from app.utility.logger import get_logger
from app.utility.others import get_database_configuration

logger = get_logger()

db_path = Path(__file__).parent.parent / "config.json"

engine = create_engine(get_database_configuration("database_dev", "url", db_path),
                       echo=get_database_configuration("database_dev", "echo", db_path))


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    create_db_and_tables()
