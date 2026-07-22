from abc import ABC, abstractmethod

from src.domain.inventory import Inventory


class InventoryRepository(ABC):
    @abstractmethod
    def load(self) -> Inventory:
        """현재 재고를 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def load_for_update(self, ingredient_names: list[str]) -> Inventory:
        """주어진 재료들의 재고 행을 잠근 채로 최신 값을 조회한다.

        (SELECT ... FOR UPDATE. 같은 트랜잭션이 끝날 때까지 다른 트랜잭션의
        동일 행에 대한 FOR UPDATE 조회를 대기시킨다.)
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, inventory: Inventory) -> None:
        """재고 상태를 저장한다."""
        raise NotImplementedError