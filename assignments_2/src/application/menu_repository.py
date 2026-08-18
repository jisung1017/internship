from typing import Protocol

from src.domain.menu import Menu
from src.domain.category import Category
from src.domain.menu_tag import MenuTag

class MenuRepository(Protocol):
    def find_all(
        self, 
        category: Category | None = None, 
        tag: MenuTag | None = None,
        limit: int | None = None,
        offset: int | None = None
    ) -> list[Menu]:
        ...

    def find_by_name(self, name: str) -> Menu | None:
        ...