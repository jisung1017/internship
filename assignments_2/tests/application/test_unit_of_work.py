from typing import Any
import pytest

from src.application.order_application_service import OrderApplicationService
from src.application.unit_of_work import AbstractUnitOfWork
from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.exceptions import OutOfStockError
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.payment import Payment
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem


class FakeRepository:

    def __init__(self) -> None:
        self.items: list[Any] = []

    def save(self, item: Any) -> None:
        self.items.append(item)


class FakeInventoryRepository:

    def __init__(self, inventory: Inventory) -> None:
        self._inventory = inventory
        self.saved_inventory: Inventory | None = None

    def get_all(self) -> Inventory:
        return self._inventory

    def save(self, inventory: Inventory) -> None:
        self.saved_inventory = inventory


class FakeUnitOfWork(AbstractUnitOfWork):

    def __init__(self, inventory: Inventory) -> None:
        self.menus = FakeRepository()
        self.inventories = FakeInventoryRepository(inventory)
        self.orders = FakeRepository()
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def test_order_application_service_commits_on_success():
    ingredient = Ingredient("원두", "g")
    inventory = Inventory(items=[InventoryItem(ingredient, Quantity(100))])
    recipe = Recipe(items=[RecipeItem(ingredient, Quantity(18))])
    menu = Menu(name="아메리카노", price=Money(3000), recipe=recipe, option_groups=[])

    cart = Cart()
    cart.add_item(CartItem(menu=menu, quantity=Quantity(1)))
    payment = Payment(balance=Money(10000))

    fake_uow = FakeUnitOfWork(inventory)
    service = OrderApplicationService(uow=fake_uow)

    order = service.place_order(cart=cart, payment=payment)

    assert order is not None
    assert fake_uow.committed is True
    assert fake_uow.rolled_back is False
    assert len(fake_uow.orders.items) == 1


def test_order_application_service_rolls_back_on_out_of_stock():
    ingredient = Ingredient("원두", "g")
    inventory = Inventory(items=[InventoryItem(ingredient, Quantity(5))])
    recipe = Recipe(items=[RecipeItem(ingredient, Quantity(18))])
    menu = Menu(name="아메리카노", price=Money(3000), recipe=recipe, option_groups=[])

    cart = Cart()
    cart.add_item(CartItem(menu=menu, quantity=Quantity(1)))
    payment = Payment(balance=Money(10000))

    fake_uow = FakeUnitOfWork(inventory)
    service = OrderApplicationService(uow=fake_uow)

    with pytest.raises(OutOfStockError):
        service.place_order(cart=cart, payment=payment)

    assert fake_uow.committed is False
    assert fake_uow.rolled_back is True
    assert len(fake_uow.orders.items) == 0