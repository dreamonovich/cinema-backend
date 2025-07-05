from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5435/cinema")


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
