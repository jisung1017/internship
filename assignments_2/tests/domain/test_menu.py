import pytest

from src.domain.money import Money
from src.domain.quantity import Quantity
from src.domain.menu import Menu
from src.domain.option_group import OptionGroup

def test_creat_menu():
    menu = Menu(
        name = "아메리카노",
        price = Money(3500),
    )

    assert menu.name == "아메리카노"
    assert menu.price == Money(3500)

def test_empty_menu_raises_value_error():
    with pytest.raises(ValueError):
        Menu(
            name= "",
            price = Money(3500),
        )

def test_blank_menu_raises_value_error():
    with pytest.raises(ValueError):
        Menu(
            name= "   ",
            price = Money(3500),
        )

def test_menu_must_be_string():
    with pytest.raises(TypeError):
        Menu(
            name= 1234,
            price = Money(3500),
        )

def test_price_must_be_Money():
    with pytest.raises(TypeError):
        Menu(
            name= "아메리카노",
            price = 3500,
        )

def test_menu_name_is_required():
    with pytest.raises(TypeError):
        Menu(
            price = Money(3500),
        )
    
def test_menu_price_is_required():
    with pytest.raises(TypeError):
        Menu(
            name = "아메리카노",
        )
    
def test_create_menu_with_option_groups():
    temperature = OptionGroup(
        name="온도",
        min_quantity=Quantity(1),
        max_quantity=Quantity(1),
    )
    shot = OptionGroup(
        name="샷",
        min_quantity=Quantity(0),
        max_quantity=Quantity(3),
    )
    menu = Menu(
        name="아메리카노",
        price=Money(3000),
        option_groups=[temperature, shot],
    )
    
    assert menu.option_groups == [temperature, shot]

def test_option_groups_must_be_list():
    temperature = OptionGroup(
        name="온도",
        min_quantity=Quantity(1),
        max_quantity=Quantity(1),
    )
    shot = OptionGroup(
        name="샷",
        min_quantity=Quantity(0),
        max_quantity=Quantity(3),
    )

    with pytest.raises(TypeError):
        Menu(
            name="아메리카노",
            price=Money(3000),
            option_groups=(temperature, shot),
        )
        
def test_option_groups_must_be_option_in_list():
    shot = OptionGroup(
        name="샷",
        min_quantity=Quantity(0),
        max_quantity=Quantity(3),
    )

    with pytest.raises(TypeError):
        Menu(
            name="아메리카노",
            price=Money(3000),
            option_groups=("temperature", shot),
        )