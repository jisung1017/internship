import pytest
from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_item import OptionItem


class TestOptionValidation:
    def test_create_option(self, make_option_item):
        item = make_option_item(name="HOT", price=0)
        option = Option(
            name="온도",
            items=[item],
        )
        assert option.name == "온도"
        assert option.items == [item]

    def test_create_option_with_default_items(self):
        option = Option(name="온도")
        assert option.name == "온도"
        assert option.items == []

    def test_empty_option_name_raises_value_error(self):
        with pytest.raises(ValueError):
            Option(name="")

    def test_blank_option_name_raises_value_error(self):
        with pytest.raises(ValueError):
            Option(name="   ")

    def test_option_name_must_be_string(self):
        with pytest.raises(TypeError):
            Option(name=1234)

    def test_option_items_must_be_list(self):
        with pytest.raises(TypeError):
            Option(name="온도", items="HOT")

    def test_option_items_must_contain_option_item(self):
        with pytest.raises(TypeError):
            Option(name="온도", items=["HOT"])

    def test_option_name_is_required(self):
        with pytest.raises(TypeError):
            Option()

    def test_option_name_is_trimmed(self):
        option = Option(name="   온도   ")
        assert option.name == "온도"


class TestOptionComparison:
    def test_option_equal(self, make_option_item):
        item1 = make_option_item(name="HOT", price=0)
        item2 = make_option_item(name="HOT", price=0)
        option1 = Option(name="온도", items=[item1])
        option2 = Option(name="온도", items=[item2])
        assert option1 == option2

    def test_option_not_equal_by_name(self, make_option_item):
        item = make_option_item(name="HOT", price=0)
        option1 = Option(name="온도", items=[item])
        option2 = Option(name="사이즈", items=[item])
        assert option1 != option2

    def test_option_not_equal_by_items(self, make_option_item):
        item1 = make_option_item(name="HOT", price=0)
        item2 = make_option_item(name="ICE", price=0)
        option1 = Option(name="온도", items=[item1])
        option2 = Option(name="온도", items=[item2])
        assert option1 != option2