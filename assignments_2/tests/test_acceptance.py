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
from src.domain.option_item import OptionItem
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

    def find_all(
        self,
        category=None,
        tag=None,
        limit=None,
        offset=None,
    ):
        result = self.items
        if category is not None:
            result = [m for m in result if getattr(m, "category", None) == category]
        if tag is not None:
            result = [m for m in result if tag in getattr(m, "tags", [])]
        if offset is not None:
            result = result[offset:]
        if limit is not None:
            result = result[:limit]
        return result

    def find_by_name(self, name: str):
        return next((item for item in self.items if item.name == name), None)


class FakeInventoryRepository:
    def __init__(self, inventory=None):
        self._inventory = inventory

    def load(self) -> Inventory:
        return self._inventory

    def load_for_update(self, ingredient_names=None) -> Inventory:
        return self.load()

    def save(self, inventory: Inventory) -> None:
        self._inventory = inventory

    def load_for_update(self, ingredient_names: list[str]) -> Inventory:
        return self.load()

    def find_histories(
        self,
        ingredient_name: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list:
        if not self._inventory:
            return []
        histories = self._inventory.history
        if ingredient_name:
            histories = [h for h in histories if h.ingredient.name == ingredient_name]
        
        histories = list(reversed(histories))
        
        if offset is not None:
            histories = histories[offset:]
        if limit is not None:
            histories = histories[:limit]
        return histories


class FakeOrderRepository:
    def __init__(self):
        self.orders = []

    def save(self, order) -> None:
        self.orders.append(order)

    def find_by_uuid(self, order_uuid):
        return None

    def find_today(self, status=None) -> list:
        result = self.orders
        if status is not None:
            result = [o for o in result if getattr(o, "status", None) == status]
        return result
    
    def update_status(self, order_uuid, new_status) -> None:
        for o in self.orders:
            if getattr(o, "order_uuid", None) == order_uuid:
                o.status = new_status

    def update_status_by_id(self, order_id: int, new_status) -> None:
        for o in self.orders:
            if getattr(o, "id", None) == order_id:
                o.status = new_status

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

    temperature_option = Option(
        name="온도",
        default_min=Quantity(1),
        default_max=Quantity(1),
        selection_mode="choice",
        items=[
            OptionItem("HOT", additional_price=Money(0)),
            OptionItem("ICE", additional_price=Money(0)),
        ],
    )

    shot_option = Option(
        name="샷 추가",
        default_min=Quantity(0),
        default_max=Quantity(4),
        selection_mode="count",
        items=[
            OptionItem(
                "샷 추가",
                additional_price=Money(500),
                recipe=Recipe(items=[RecipeItem(bean, Quantity(10))]),
            )
        ],
    )

    temperature_group = OptionGroup(option=temperature_option)
    shot_group = OptionGroup(option=shot_option)

    return Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=Recipe(items=[RecipeItem(bean, Quantity(18))]),
        option_groups=[temperature_group, shot_group],
    )


def build_inventory(bean_quantity: int) -> Inventory:
    return Inventory(
        items=[InventoryItem(Ingredient("원두"), Quantity(bean_quantity))]
    )


def get_quantity(inventory: Inventory, ingredient: Ingredient) -> Quantity:
    for item in inventory.items:
        if item.ingredient == ingredient:
            return item.quantity
    raise AssertionError(f"{ingredient.name} 재고가 없습니다.")


def build_cli(
    monkeypatch, inputs: list[str], is_approved: bool, bean_quantity: int
) -> CLI:
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
        assert "부족" in captured.out or "품절" in captured.out
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
        self, monkeypatch
    ):
        cli = build_cli(
            monkeypatch,
            inputs=["77", "1", "우유", "50", "0", "0"],
            is_approved=True,
            bean_quantity=1000,
        )
        cli.run()
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