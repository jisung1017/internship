import pytest

from src.domain.option_group import OptionGroup
from src.domain.option import Option
from src.domain.money import Money
from src.domain.quantity import Quantity


class TestOptionGroupValidation:
    
    def test_option_group_name_must_be_string(self):
        with pytest.raises(TypeError):
            OptionGroup(name=1234)

    def test_empty_option_group_name_raises_value_error(self):
        with pytest.raises(ValueError):
            OptionGroup(name="")

    def test_blank_option_group_name_raises_value_error(self):
        with pytest.raises(ValueError):
            OptionGroup(name="   ")

    def test_option_group_name_is_trimmed(self):
        option_group = OptionGroup(name="  온도  ")

        assert option_group.name == "온도"

    def test_min_quantity_must_be_quantity(self):
        with pytest.raises(TypeError):
            OptionGroup(
                name="온도",
                min_quantity=1,
                max_quantity=Quantity(1),
            )

    def test_max_quantity_must_be_quantity(self):
        with pytest.raises(TypeError):
            OptionGroup(
                name="온도",
                min_quantity=Quantity(1),
                max_quantity=1,
            )

    def test_min_quantity_lower_than_max_quantity(self):
        with pytest.raises(ValueError):
            OptionGroup(
                name="온도",
                min_quantity=Quantity(4),
                max_quantity=Quantity(1),
            )       

    def test_options_must_be_list(self):
        hot = Option(
            name="HOT",
            additional_price=Money(0),
        )

        ice = Option(
            name="ICE",
            additional_price=Money(0),
        )

        with pytest.raises(TypeError):
            OptionGroup(
                name="온도",
                options = (hot, ice),
            )
            
    def test_options_must_be_option_in_list(self):
        hot = Option(
            name="HOT",
            additional_price=Money(0),
        )

        with pytest.raises(TypeError):
            OptionGroup(
                name="온도",
                options = [hot, "ice"],
            )