from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()


DB_URL = os.getenv("DB_URL", default="sqlite:///db.db")

engine = create_engine(
    DB_URL,
    echo=True,
)

SessionLocal = sessionmaker(bind=engine)


def get_db_session() -> Generator[Session]:
    with SessionLocal() as session:
        with session.begin():
            yield session
