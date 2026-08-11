import pytest

from src.domain.money import Money
from src.domain.option_item import OptionItem

class TestOptionItemValidation:
    
    def test_create_option(self):
        option = OptionItem(
            name = "샷 추가",
            additional_price = Money(500),
        )

        assert option.name == "샷 추가"
        assert option.additional_price == Money(500)

    def test_empty_option_name_raises_value_error(self):
        with pytest.raises(ValueError):
            OptionItem(
                name= "",
                additional_price = Money(500),
            )

    def test_blank_option_name_raises_value_error(self):
        with pytest.raises(ValueError):
            OptionItem(
                name= "   ",
                additional_price = Money(500),
            )

    def test_option_name_must_be_string(self):
        with pytest.raises(TypeError):
            OptionItem(
                name= 1234,
                additional_price = Money(500),
            )

    def test_additional_price_must_be_Money(self):
        with pytest.raises(TypeError):
            OptionItem(
                name= "샷 추가",
                additional_price = 500,
            )

    def test_option_name_is_required(self):
        with pytest.raises(TypeError):
            OptionItem(
                additional_price = Money(500),
            )
        
    def test_option_additional_price_is_required(self):
        with pytest.raises(TypeError):
            OptionItem(
                name = "샷 추가",
            )
        
    def test_option_name_is_trimmed(self):
        option = OptionItem(
            name="  샷 추가  ",
            additional_price=Money(500),
        )

        assert option.name == "샷 추가"

class TestOptionItemComparison:

    def test_option_equal(self):
        option1 = OptionItem(name="샷 추가", additional_price=Money(500))
        option2 = OptionItem(name="샷 추가", additional_price=Money(500))
        assert option1 == option2

    def test_option_not_equal_by_name(self):
        option1 = OptionItem(name="샷 추가", additional_price=Money(500))
        option2 = OptionItem(name="시럽 추가", additional_price=Money(500))
        assert option1 != option2

    def test_option_not_equal_by_price(self):
        option1 = OptionItem(name="샷 추가", additional_price=Money(500))
        option2 = OptionItem(name="샷 추가", additional_price=Money(1000))
        assert option1 != option2

    def test_option_additional_price_can_be_zero(self):
        option = OptionItem(name="얼음 많이", additional_price=Money(0))
        assert option.additional_price == Money(0)