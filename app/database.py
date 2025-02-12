import json
from contextlib import contextmanager
from pathlib import Path
from app.models import *

from sqlmodel import Session, SQLModel, create_engine

db_path = Path(__file__).parent.parent / "config.json"

with open(db_path, 'r') as config_file:
    config = json.load(config_file)

DATABASE_URL = config['database_dev']['url']

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    with Session(engine) as session:
        yield session

if __name__ == '__main__':
    create_db_and_tables()