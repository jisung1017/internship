import uuid
from uuid import UUID

from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.money import Money
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe


class Order:
    def __init__(
        self,
        items: list[CartItem],
        id: int | None = None,
        order_uuid: UUID | None = None,
    ):
        if not isinstance(items, list):
            raise TypeError("items 은 list 형 입니다.")

        if not items:
            raise ValueError("Order 는 적어도 하나의 CartItem 이 있어야합니다.")

        if not all(isinstance(item, CartItem) for item in items):
            raise TypeError("items 는 오로지 CartItem 로만 이루어져있습니다.")

        # Cart와 리스트를 공유하지 않도록 복사
        self.items = items.copy()
        self.id = id
        self.order_uuid = order_uuid or uuid.uuid4()

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

    def get_recipe_requirements(self) -> list[tuple[Recipe, Quantity]]:
        """전체 주문 항목들의 레시피 요구량을 취합하여 반환합니다."""
        requirements: list[tuple[Recipe, Quantity]] = []
        for item in self.items:
            requirements.extend(item.get_recipe_requirements())
        return requirements