import os
from collections.abc import Iterator
from contextlib import contextmanager

from psycopg import Connection
from psycopg import connect
from psycopg.rows import dict_row

# 로컬 개발 기본값. DATABASE_URL 환경변수가 설정되면 그쪽이 우선한다.
DEFAULT_DATABASE_URL = "postgresql://kiosk:kiosk@localhost:5432/kiosk"


class Database:
    def __init__(
        self,
        dsn: str | None = None,
    ) -> None:
        self._dsn = dsn or os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)

    @contextmanager
    def transaction(self) -> Iterator[Connection]:
        with connect(
            self._dsn,
            row_factory=dict_row,
        ) as connection:
            yield connection