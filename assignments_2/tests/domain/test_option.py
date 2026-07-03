import pytest

from src.domain.money import Money
from src.domain.option import Option

def test_create_option():
    option = Option(
        name = "샷 추가",
        additional_price = Money(500),
    )

    assert option.name == "샷 추가"
    assert option.additional_price == Money(500)

def test_empty_option_name_raises_value_error():
    with pytest.raises(ValueError):
        Option(
            name= "",
            additional_price = Money(500),
        )

def test_blank_option_name_raises_value_error():
    with pytest.raises(ValueError):
        Option(
            name= "   ",
            additional_price = Money(500),
        )

def test_option_name_must_be_string():
    with pytest.raises(TypeError):
        Option(
            name= 1234,
            additional_price = Money(500),
        )

def test_additional_price_must_be_Money():
    with pytest.raises(TypeError):
        Option(
            name= "샷 추가",
            additional_price = 500,
        )

def test_option_name_is_required():
    with pytest.raises(TypeError):
        Option(
            additional_price = Money(500),
        )
    
def test_option_additional_price_is_required():
    with pytest.raises(TypeError):
        Option(
            name = "샷 추가",
        )
    
def test_option_name_is_trimmed():
    option = Option(
        name="  샷 추가  ",
        additional_price=Money(500),
    )

    assert option.name == "샷 추가"