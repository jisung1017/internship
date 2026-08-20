import os
import sys

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.db import DEFAULT_DATABASE_URL
from src.infrastructure.seeder import seed_initial_data_from_json


def run_seed():
    db_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    if db_url.startswith("postgresql://"):
        sqlalchemy_url = db_url.replace("postgresql://", "postgresql+psycopg://")
    else:
        sqlalchemy_url = db_url

    engine = create_engine(sqlalchemy_url)
    session_factory = sessionmaker(bind=engine)
    with session_factory() as session:
        seed_initial_data_from_json(session)
        print("초기 시드 데이터 주입 완료")


if __name__ == "__main__":
    run_seed()