import pytest

from src.domain.money import Money
from src.domain.option import Option
from src.domain.quantity import Quantity
from src.interface.cli import parse_menu_choice, parse_quantity


class TestParseMenuChoice:

    def test_out_of_range_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_menu_choice("17", menu_count=4)

    def test_string_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_menu_choice("abc", menu_count=4)

    def test_float_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_menu_choice("2.3", menu_count=2)




class TestParseQuantity:

    def test_below_range_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_quantity("0")

    def test_above_range_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_quantity("11")

    def test_string_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_quantity("abc")

    def test_float_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_quantity("1.1")