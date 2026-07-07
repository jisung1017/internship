from src.domain.cart_item import CartItem
from src.domain.money import Money


class Cart:
    def __init__(self):
        self.items: list[CartItem] = []

    def __len__(self):
        return len(self.items)
    
    def add_item(self, item: CartItem) -> None:
        if not isinstance(item, CartItem):
            raise TypeError("item 은 CartItem 이여야 한다.")

        self.items.append(item)

    def total_price(self) -> Money:
        total = Money(0)

        for item in self.items:
            total = total.add(item.total_price())

        return total
    
    def clear(self) -> None:
        self.items.clear()