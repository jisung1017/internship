import psycopg
import pytest
from psycopg.rows import dict_row


@pytest.fixture
def connection():
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="kiosk",
        user="kiosk",
        password="kiosk",
        row_factory=dict_row,
    )
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()