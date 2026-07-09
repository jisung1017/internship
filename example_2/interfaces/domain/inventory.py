from dataclasses import dataclass


@dataclass
class Inventory:
    id: int
    ingredient_id: int
    amount: int

    # 재고 확인
    def check_inventory_amount(self):
        return self.amount

    # 출고
    def outbound(self, amount: int):
        if amount < 0:
            raise ValueError("수량은 0, 양수")
        if self.amount < amount:
            raise ValueError("재고가 부족해요")
        self.amount -= amount
