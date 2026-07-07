import pytest

from src.domain.exceptions import InsufficientBalanceError, OutOfStockError
from src.domain.payment import Payment
from src.domain.money import Money
from src.domain.inventory import Inventory, InventoryItem
from src.domain.ingredient import Ingredient
from src.domain.quantity import Quantity
from src.application.order_service import OrderService
from src.domain.cart import Cart, CartItem
from src.domain.menu import Menu
from src.domain.recipe import Recipe, RecipeItem
from src.domain.option import Option

def create_enough_payment(balance: int = 10000) -> Payment:
    return Payment(balance=Money(balance))

def create_poor_payment(balance: int = 100) -> Payment:
    return Payment(balance=Money(balance))

def create_inventory_with_bean(quantity: int) -> Inventory:
    return Inventory(items=[InventoryItem(Ingredient("원두"), Quantity(quantity))])

def create_menu(name: str, price: int) -> Menu:
    recipe = Recipe(
        items=[
            RecipeItem(
                ingredient=Ingredient("원두"),
                quantity=Quantity(18),
            )
        ]
    )

    return Menu(
        name=name,
        price=Money(price),
        recipe=recipe,
        option_groups=[],
    )


def create_cart_item(
    name: str,
    price: int,
    quantity: int,
    selected_options: list[Option] | None = None,
) -> CartItem:
    return CartItem(
        menu=create_menu(name, price),
        quantity=Quantity(quantity),
        selected_options=selected_options or [],
    )

@pytest.fixture
def americano_cart() -> Cart:
        cart = Cart()
        item = create_cart_item(
            name="아메리카노",
            price=3000,
            quantity=1,
        )

        cart.add_item(item)

        return cart


class TestOrderServiceValidation:
    
    def test_checkout_raises_out_of_stock_error_and_clears_cart(self, americano_cart):
        """재고가 부족하면 OutOfStockError가 발생하고 장바구니가 비워진다."""
        # Given: 잔액은 충분하지만, 원두 재고는 부족한 상황 (아메리카노는 18개 필요)
        payment = create_enough_payment()
        inventory = create_inventory_with_bean(quantity=5) 
        service = OrderService(payment, inventory)

        # When & Then: 결제 시 예외 발생 확인
        with pytest.raises(OutOfStockError):
            service.checkout(americano_cart)

        # Then: 장바구니가 비워졌는지 확인
        assert len(americano_cart) == 0

    def test_checkout_raises_insufficient_balance_and_clear_cart(self, americano_cart):
        """잔액이 부족하면 InsufficientBalanceError가 발생하고 장바구니가 비워진다."""
        # Given: 재고는 충분하지만, 돈이 없는 상황
        payment = create_poor_payment()
        inventory = create_inventory_with_bean(quantity=100)
        service = OrderService(payment, inventory)

        # When & Then
        with pytest.raises(InsufficientBalanceError):
            service.checkout(americano_cart)   

        assert len(americano_cart) == 0


class TestOrderServiceAtomicity:
    
    def test_checkout_does_not_charge_when_is_out_of_stock(self, americano_cart):
        """재고가 부족하여 실패했을 때, 유저의 잔액은 차감되지 않아야 한다 (원자성)."""
        # Given
        initial_balance = 10000
        payment = create_enough_payment(balance=initial_balance)
        inventory = create_inventory_with_bean(quantity=5)
        service = OrderService(payment, inventory)

        # When
        with pytest.raises(OutOfStockError):
            service.checkout(americano_cart)

        # Then: 처음 잔액 그대로 유지되었는지 검증
        assert payment.balance == Money(initial_balance)
