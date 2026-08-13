import pytest
from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.option_item import OptionItem
from src.domain.quantity import Quantity


class TestOptionGroupValidation:
    def test_fallback_to_option_defaults(self, make_option, make_option_item):
        item = make_option_item(name="HOT", price=0)
        option = Option(
            name="온도",
            default_min=Quantity(1),
            default_max=Quantity(1),
            selection_mode="choice",
            items=[item],
        )
        group = OptionGroup(option=option)

        assert group.min_quantity == Quantity(1)
        assert group.max_quantity == Quantity(1)
        assert group.selection_mode == "choice"

    def test_override_option_defaults(self, make_option, make_option_item):
        item = make_option_item(name="샷 추가", price=500)
        option = Option(
            name="샷 추가",
            default_min=Quantity(0),
            default_max=Quantity(4),
            selection_mode="count",
            items=[item],
        )
        group = OptionGroup(
            option=option,
            override_max_quantity=Quantity(2),
        )

        assert group.min_quantity == Quantity(0)
        assert group.max_quantity == Quantity(2)  # Override 적용 확인
        assert group.selection_mode == "count"


class TestOptionGroupValidateSelection:
    def test_validate_passes_within_range(self, make_option_group, make_option_item):
        hot = make_option_item(name="HOT", price=0)
        group = make_option_group(
            override_min=1,
            override_max=1,
        )
        group.option.items = [hot]
        group.validate([hot])

    def test_validate_raises_when_below_min(self, make_option_group, make_option_item):
        hot = make_option_item(name="HOT", price=0)
        group = make_option_group(
            override_min=1,
            override_max=1,
        )
        group.option.items = [hot]
        with pytest.raises(ValueError):
            group.validate([])