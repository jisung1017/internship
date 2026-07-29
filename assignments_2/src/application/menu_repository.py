from typing import Protocol

from src.domain.menu import Menu


class MenuRepository(Protocol):
    def find_all(self) -> list[Menu]:
        ...

    def find_by_name(self, name: str) -> Menu | None:
        ...