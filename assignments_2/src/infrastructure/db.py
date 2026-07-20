from collections.abc import Iterator
from contextlib import contextmanager

from psycopg import Connection
from psycopg import connect
from psycopg.rows import dict_row


class Database:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        dbname: str = "kiosk",
        user: str = "kiosk",
        password: str = "kiosk",
    ) -> None:
        self._host = host
        self._port = port
        self._dbname = dbname
        self._user = user
        self._password = password

    @contextmanager
    def transaction(self) -> Iterator[Connection]:
        with connect(
            host=self._host,
            port=self._port,
            dbname=self._dbname,
            user=self._user,
            password=self._password,
            row_factory=dict_row,
        ) as connection:
            yield connection