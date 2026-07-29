import os

import psycopg
import pytest
from psycopg.rows import dict_row
from src.infrastructure.db import DEFAULT_DATABASE_URL


def _test_dsn() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL) 

@pytest.fixture
def connection():
    conn = psycopg.connect(_test_dsn(), row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()