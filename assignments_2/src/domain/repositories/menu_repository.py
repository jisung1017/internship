from abc import ABC, abstractmethod

from src.domain.menu import Menu


class MenuRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[Menu]:
        """전체 메뉴를 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def find_by_name(self, name: str) -> Menu | None:
        """이름으로 메뉴를 조회한다."""
        raise NotImplementedError