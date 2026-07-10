import pytest

from src.domain.money import Money
from src.domain.quantity import Quantity
from src.domain.ingredient import Ingredient
from src.domain.recipe_item import RecipeItem
from src.domain.recipe import Recipe
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.menu import Menu
from src.domain.cart_item import CartItem
from src.domain.inventory_item import InventoryItem
from src.domain.inventory import Inventory
from src.domain.payment import Payment


@pytest.fixture
def make_ingredient():
    def _make(name: str = "원두") -> Ingredient:
        return Ingredient(name)
    return _make


@pytest.fixture
def make_recipe_item(make_ingredient):
    def _make(ingredient: Ingredient | None = None, quantity: int = 18) -> RecipeItem:
        return RecipeItem(ingredient or make_ingredient(), Quantity(quantity))
    return _make


@pytest.fixture
def make_recipe(make_recipe_item):
    def _make(items: list[RecipeItem] | None = None) -> Recipe:
        return Recipe(items=items if items is not None else [make_recipe_item()])
    return _make


@pytest.fixture
def make_option():
    def _make(name: str = "샷추가", price: int = 500, recipe: Recipe | None = None) -> Option:
        return Option(
            name=name,
            additional_price=Money(price),
            recipe=recipe if recipe is not None else Recipe(items=[]),
        )
    return _make


@pytest.fixture
def make_option_group(make_option):
    def _make(
        name: str = "샷",
        min_quantity: int = 0,
        max_quantity: int = 3,
        options: list[Option] | None = None,
    ) -> OptionGroup:
        return OptionGroup(
            name=name,
            min_quantity=Quantity(min_quantity),
            max_quantity=Quantity(max_quantity),
            options=options if options is not None else [make_option()],
        )
    return _make


@pytest.fixture
def make_menu(make_recipe):
    def _make(
        name: str = "아메리카노",
        price: int = 3000,
        recipe: Recipe | None = None,
        option_groups: list[OptionGroup] | None = None,
    ) -> Menu:
        return Menu(
            name=name,
            price=Money(price),
            recipe=recipe if recipe is not None else make_recipe(),
            option_groups=option_groups or [],
        )
    return _make


@pytest.fixture
def make_cart_item(make_menu):
    def _make(
        menu: Menu | None = None,
        quantity: int = 1,
        selected_options: list[Option] | None = None,
    ) -> CartItem:
        return CartItem(
            menu=menu or make_menu(),
            quantity=Quantity(quantity),
            selected_options=selected_options or [],
        )
    return _make


@pytest.fixture
def make_inventory_item(make_ingredient):
    def _make(ingredient: Ingredient | None = None, quantity: int = 1000) -> InventoryItem:
        return InventoryItem(ingredient or make_ingredient(), Quantity(quantity))
    return _make


@pytest.fixture
def make_inventory(make_inventory_item):
    def _make(items: list[InventoryItem] | None = None) -> Inventory:
        return Inventory(items=items if items is not None else [make_inventory_item()])
    return _make


@pytest.fixture
def make_payment():
    def _make(balance: int = 10000) -> Payment:
        return Payment(balance=Money(balance))
    return _make