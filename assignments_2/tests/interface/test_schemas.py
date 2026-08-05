from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.interface.api.schemas import MenuResponse


def test_menu_response_from_domain():
    option_group = OptionGroup(
        name="온도",
        min_quantity=Quantity(1),
        max_quantity=Quantity(1),
        options=[Option(name="HOT", additional_price=Money(0))],
    )
    menu = Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=Recipe(items=[]),
        option_groups=[option_group],
    )

    response = MenuResponse.from_domain(menu)

    assert response.name == "아메리카노"
    assert response.price == 3000
    assert len(response.option_groups) == 1
    assert response.option_groups[0].options[0].name == "HOT"

