import json
from contextlib import contextmanager
from pathlib import Path
from app.models import *

from sqlmodel import Session, SQLModel, create_engine
from app.utility.logger import get_logger

logger = get_logger()

db_path = Path(__file__).parent.parent / "config.json"

try:
    with open(db_path, 'r') as config_file:
        config = json.load(config_file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logger.error(f"Error loading database configuration: {e}")
    raise SystemExit(1)

DATABASE_URL = config['database_dev']['url']

engine = create_engine(DATABASE_URL, echo=config['database_dev']['echo'])


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
