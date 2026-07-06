from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.money import Money


class Order:
    def __init__(self, items: list[CartItem]):
        if not isinstance(items, list):
            raise TypeError("items must be a list")

        if not items:
            raise ValueError("Order must contain at least one CartItem")

        if not all(isinstance(item, CartItem) for item in items):
            raise TypeError("items must contain only CartItem")

        # Cart와 리스트를 공유하지 않도록 복사
        self.items = items.copy()

    @classmethod
    def from_cart(cls, cart: Cart) -> "Order":
        if not isinstance(cart, Cart):
            raise TypeError("cart must be a Cart")

        return cls(cart.items)

    def total_price(self) -> Money:
        total = Money(0)

        for item in self.items:
            total = total.add(item.total_price())

        return total