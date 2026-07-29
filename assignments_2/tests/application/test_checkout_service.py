from unittest.mock import MagicMock
import pytest

from src.application.checkout_service import CheckoutService
from src.application.order_service import OrderService
from src.domain.cart import Cart, CartItem
from src.domain.exceptions import OutOfStockError
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory, InventoryItem
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.payment import Payment
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe, RecipeItem


def create_menu(name: str, price: int) -> Menu:
    return Menu(
        name=name,
        price=Money(price),
        recipe=Recipe(items=[RecipeItem(Ingredient("원두"), Quantity(10))]),
        option_groups=[],
    )


class TestCheckoutService:
    def test_checkout_persists_order_and_inventory_on_success(self):
        """결제 성공 시 OrderPersister.persist가 주문 및 변경된 재고와 함께 호출된다."""
        # Given
        payment = Payment(balance=Money(10000))
        inventory = Inventory(items=[InventoryItem(Ingredient("원두"), Quantity(100))])
        order_service = OrderService(payment, inventory)

        mock_persister = MagicMock()
        checkout_service = CheckoutService(
            order_service=order_service,
            order_persister=mock_persister,
        )

        cart = Cart()
        cart.add_item(CartItem(menu=create_menu("아메리카노", 3000), quantity=Quantity(1)))

        # When
        order = checkout_service.checkout(cart)

        # Then
        assert order.total_price() == Money(3000)
        # OrderPersister.persist(order, inventory)가 올바른 인자로 호출되었는지 검증
        mock_persister.persist.assert_called_once_with(order, inventory)

    def test_checkout_does_not_persist_when_order_fails(self):
        """재고 부족 등으로 결제가 실패하면 OrderPersister가 호출되지 않는다."""
        # Given: 재고 부족 상황 (필요: 10, 보유: 5)
        payment = Payment(balance=Money(10000))
        inventory = Inventory(items=[InventoryItem(Ingredient("원두"), Quantity(5))])
        order_service = OrderService(payment, inventory)

        mock_persister = MagicMock()
        checkout_service = CheckoutService(
            order_service=order_service,
            order_persister=mock_persister,
        )

        cart = Cart()
        cart.add_item(CartItem(menu=create_menu("아메리카노", 3000), quantity=Quantity(1)))

        # When & Then
        with pytest.raises(OutOfStockError):
            checkout_service.checkout(cart)

        # 영속화 메서드가 전혀 호출되지 않았음을 검증
        mock_persister.persist.assert_not_called()