import pytest

from src.domain.money import Money

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
    