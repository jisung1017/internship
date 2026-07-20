from abc import ABC, abstractmethod

from src.domain.ingredient import Ingredient


class IngredientRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[Ingredient]:
        """모든 재료를 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def find_by_name(self, name: str) -> Ingredient | None:
        """이름으로 재료를 조회한다."""
        raise NotImplementedError