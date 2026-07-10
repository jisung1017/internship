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

    def test_option_group_name_is_trimmed(self, make_option_group):
        group = make_option_group(name="  온도  ")

        assert group.name == "온도"

    def test_min_quantity_must_be_quantity(self):
        with pytest.raises(TypeError):
            OptionGroup(name="온도", min_quantity=1, max_quantity=Quantity(1))

    def test_max_quantity_must_be_quantity(self):
        with pytest.raises(TypeError):
            OptionGroup(name="온도", min_quantity=Quantity(1), max_quantity=1)

    def test_min_quantity_lower_than_max_quantity(self):
        with pytest.raises(ValueError):
            OptionGroup(name="온도", min_quantity=Quantity(4), max_quantity=Quantity(1))

    def test_options_must_be_list(self, make_option):
        hot = make_option(name="HOT", price=0)
        ice = make_option(name="ICE", price=0)

        with pytest.raises(TypeError):
            OptionGroup(name="온도", options=(hot, ice))

    def test_options_must_be_option_in_list(self, make_option):
        hot = make_option(name="HOT", price=0)

        with pytest.raises(TypeError):
            OptionGroup(name="온도", options=[hot, "ice"])


class TestOptionGroupContains:

    def test_contains_returns_true_when_option_belongs_to_group(self, make_option_group, make_option):
        hot = make_option(name="HOT", price=0)
        group = make_option_group(name="온도", min_quantity=1, max_quantity=1, options=[hot])

        assert group.contains(hot) is True

    def test_contains_returns_false_when_option_does_not_belong_to_group(self, make_option_group, make_option):
        hot = make_option(name="HOT", price=0)
        other = make_option(name="샷추가", price=500)
        group = make_option_group(name="온도", min_quantity=1, max_quantity=1, options=[hot])

        assert group.contains(other) is False


class TestOptionGroupCountSelected:

    def test_count_selected_counts_matching_option(self, make_option_group, make_option):
        hot = make_option(name="HOT", price=0)
        shot = make_option(name="샷추가", price=500)
        group = make_option_group(name="온도", min_quantity=1, max_quantity=1, options=[hot])

        assert group.count_selected([hot, shot]) == 1

    def test_count_selected_returns_zero_when_no_match(self, make_option_group, make_option):
        hot = make_option(name="HOT", price=0)
        shot = make_option(name="샷추가", price=500)
        group = make_option_group(name="온도", min_quantity=1, max_quantity=1, options=[hot])

        assert group.count_selected([shot]) == 0

    def test_count_selected_counts_duplicated_option(self, make_option_group, make_option):
        shot = make_option(name="샷추가", price=500)
        group = make_option_group(name="샷", min_quantity=0, max_quantity=3, options=[shot])

        assert group.count_selected([shot, shot, shot]) == 3


class TestOptionGroupValidateSelection:

    def test_validate_passes_within_range(self, make_option_group, make_option):
        hot = make_option(name="HOT", price=0)
        group = make_option_group(name="온도", min_quantity=1, max_quantity=1, options=[hot])

        group.validate([hot])

    def test_validate_passes_with_zero_when_min_is_zero(self, make_option_group):
        group = make_option_group(name="샷", min_quantity=0, max_quantity=3)

        group.validate([])

    def test_validate_raises_when_below_min(self, make_option_group, make_option):
        hot = make_option(name="HOT", price=0)
        group = make_option_group(name="온도", min_quantity=1, max_quantity=1, options=[hot])

        with pytest.raises(ValueError):
            group.validate([])

    def test_validate_raises_when_above_max(self, make_option_group, make_option):
        shot = make_option(name="샷추가", price=500)
        group = make_option_group(name="샷", min_quantity=0, max_quantity=3, options=[shot])

        with pytest.raises(ValueError):
            group.validate([shot] * 4)

    def test_validate_ignores_options_not_in_group(self, make_option_group, make_option):
        hot = make_option(name="HOT", price=0)
        shot = make_option(name="샷추가", price=500)
        group = make_option_group(name="온도", min_quantity=1, max_quantity=1, options=[hot])

        group.validate([hot, shot])