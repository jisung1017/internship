from psycopg import Connection
from psycopg import connect
from psycopg.rows import dict_row


class Database:

    def connect(self) -> Connection:
        return connect(
            host="localhost",
            port=5432,
            dbname="kiosk",
            user="kiosk",
            password="kiosk",
            row_factory=dict_row,
        )