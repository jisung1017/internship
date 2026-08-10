import pytest

from src.application.cart_service import CartService
from src.application.kiosk_admin_service import KioskAdminService
from src.application.order_application_service import OrderApplicationService
from src.application.unit_of_work import AbstractUnitOfWork
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.payment import Payment
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem
from src.interface.cli import CLI


class FakeRepository:
    def __init__(self):
        self.items = []

    def save(self, item):
        self.items.append(item)

    def find_all(self):
        return self.items


class FakeInventoryRepository:
    def __init__(self, inventory=None):
        self._inventory = inventory

    def load(self) -> Inventory:
        return self._inventory

    def save(self, inventory: Inventory) -> None:
        self._inventory = inventory


class FakeOrderRepository:
    def __init__(self):
        self.orders = []

    def save(self, order) -> None:
        self.orders.append(order)

    def find_by_uuid(self, order_uuid):
        return None

    def find_today(self) -> list:
        return []


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self, inventory=None, menus=None, orders=None):
        self.inventories = FakeInventoryRepository(inventory)
        self.menus = menus or FakeRepository()
        self.orders = orders or FakeOrderRepository()
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def build_americano() -> Menu:
    bean = Ingredient("원두")

    temperature_group = OptionGroup(
        name="온도",
        min_quantity=Quantity(1),
        max_quantity=Quantity(1),
        options=[
            Option(name="HOT", additional_price=Money(0)),
            Option(name="ICE", additional_price=Money(0)),
        ],
    )

    shot_group = OptionGroup(
        name="샷추가",
        min_quantity=Quantity(0),
        max_quantity=Quantity(4),
        selection_mode="count",
        options=[
            Option(
                name="샷추가",
                additional_price=Money(500),
                recipe=Recipe(items=[RecipeItem(bean, Quantity(10))]),
            )
        ],
    )

    return Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=Recipe(items=[RecipeItem(bean, Quantity(18))]),
        option_groups=[temperature_group, shot_group],
    )


def build_inventory(bean_quantity: int) -> Inventory:
    return Inventory(items=[InventoryItem(Ingredient("원두"), Quantity(bean_quantity))])


def get_quantity(inventory: Inventory, ingredient: Ingredient) -> Quantity:
    for item in inventory.items:
        if item.ingredient == ingredient:
            return item.quantity

    raise AssertionError(f"{ingredient.name} 재고를 찾을 수 없습니다.")


def build_cli(monkeypatch, inputs: list[str], is_approved: bool, bean_quantity: int) -> CLI:
    responses = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    menus = [build_americano()]
    inventory = build_inventory(bean_quantity)
    payment = Payment(is_approved=is_approved)

    cart_service = CartService()
    fake_uow = FakeUnitOfWork(inventory=inventory)
    order_app_service = OrderApplicationService(uow=fake_uow)
    admin_service = KioskAdminService(uow=fake_uow)

    return CLI(
        menus=menus,
        payment=payment,
        inventory=inventory,
        cart_service=cart_service,
        order_app_service=order_app_service,
        admin_service=admin_service,
    )


class TestSuccessfulCheckout:
    def test_inventory_decrease_correctly(self, monkeypatch):
        cli = build_cli(
            monkeypatch,
            inputs=["1", "HOT", "0", "1", "2", "2", "1", "0"],
            is_approved=True,
            bean_quantity=1000,
        )

        cli.run()

        assert get_quantity(cli.inventory, Ingredient("원두")) == Quantity(982)
        assert len(cli.cart) == 0


class TestOptionConsumesInventory:
    def test_option_recipe_is_consumed_on_checkout(self, monkeypatch):
        cli = build_cli(
            monkeypatch,
            inputs=["1", "HOT", "2", "1", "2", "2", "1", "0"],
            is_approved=True,
            bean_quantity=1000,
        )

        cli.run()

        assert get_quantity(cli.inventory, Ingredient("원두")) == Quantity(962)


class TestOutOfStock:
    def test_cart_is_cleared_and_inventory_untouched(self, monkeypatch, capsys):
        cli = build_cli(
            monkeypatch,
            inputs=["1", "HOT", "0", "1", "2", "2", "1", "0"],
            is_approved=True,
            bean_quantity=5,
        )

        cli.run()

        captured = capsys.readouterr()
        assert "재고가 부족합니다" in captured.out
        assert get_quantity(cli.inventory, Ingredient("원두")) == Quantity(5)
        assert len(cli.cart) == 0


class TestInvalidMenuAndOptionInput:
    def test_retries_after_invalid_input_and_completes_order(self, monkeypatch):
        cli = build_cli(
            monkeypatch,
            inputs=["9", "1", "COLD", "HOT", "0", "1", "2", "2", "1", "0"],
            is_approved=True,
            bean_quantity=1000,
        )

        cli.run()

        assert len(cli.cart) == 0


class TestOptionValidationDefenseInDepth:
    def test_add_to_cart_rejects_option_missing_required_group(self):
        menu = build_americano()
        cart_service = CartService()

        from src.domain.cart import Cart

        cart = Cart()

        with pytest.raises(ValueError):
            cart_service.add_item(cart, menu, Quantity(1), [])

        assert len(cart) == 0


class TestDevelopmentModeValidation:
    def test_restock_increases_inventory_and_records_history(self, monkeypatch):
        cli = build_cli(
            monkeypatch,
            inputs=["77", "1", "원두", "100", "0", "0"],
            is_approved=True,
            bean_quantity=1000,
        )

        cli.run()

        inventory = cli.admin_service.get_inventory()
        assert inventory.get_quantity(Ingredient("원두")) == Quantity(1100)
        assert len(inventory.history) == 1
        assert inventory.history[0].change == 100
        assert inventory.history[0].reason == "RESTOCK"

    def test_restock_unregistered_ingredient_shows_error_and_does_not_change_state(
        self, monkeypatch, capsys
    ):
        cli = build_cli(
            monkeypatch,
            inputs=["77", "1", "우유", "50", "0", "0"],
            is_approved=True,
            bean_quantity=1000,
        )

        cli.run()

        captured = capsys.readouterr()
        assert "등록되지 않은 재료" in captured.out

        inventory = cli.admin_service.get_inventory()
        assert inventory.get_quantity(Ingredient("원두")) == Quantity(1000)
        assert len(inventory.history) == 0

    def test_multiple_restocks_accumulate_history_in_order(self, monkeypatch):
        cli = build_cli(
            monkeypatch,
            inputs=["77", "1", "원두", "50", "1", "원두", "30", "0", "0"],
            is_approved=True,
            bean_quantity=1000,
        )

        cli.run()

        inventory = cli.admin_service.get_inventory()
        assert inventory.get_quantity(Ingredient("원두")) == Quantity(1080)
        assert [h.change for h in inventory.history] == [50, 30]