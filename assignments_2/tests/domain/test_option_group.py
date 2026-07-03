import pytest

from src.domain.option_group import OptionGroup
from src.domain.option import Option
from src.domain.money import Money


def test_create_option_group():
    hot = Option(
        name="HOT",
        additional_price=Money(0),
    )
    
    ice = Option(
        name="ICE",
        additional_price=Money(0)
    )

    option_group = OptionGroup(
        name="온도",
        required=True,
        multiple=False,
        options = [hot, ice],
    )

    assert option_group.name == "온도"
    assert option_group.required is True
    assert option_group.multiple is False
    assert option_group.options == [hot, ice]

def test_option_group_name_must_be_string():
    with pytest.raises(TypeError):
        OptionGroup(
            name=1234,
            required=True,
            multiple=False,
        )

def test_empty_option_group_name_raises_value_error():
    with pytest.raises(ValueError):
        OptionGroup(
            name="",
            required=True,
            multiple=False,
        )

def test_blank_option_group_name_raises_value_error():
    with pytest.raises(ValueError):
        OptionGroup(
            name="   ",
            required=True,
            multiple=False,
        )

def test_option_group_name_is_trimmed():
    option_group = OptionGroup(
        name="  온도  ",
        required=True,
        multiple=False,
    )

    assert option_group.name == "온도"

def test_required_must_be_boolean():
    with pytest.raises(TypeError):
        OptionGroup(
            name="온도",
            required="True",
            multiple=False,
        )

def test_multiple_must_be_boolean():
    with pytest.raises(TypeError):
        OptionGroup(
            name="온도",
            required=True,
            multiple="False",
        )

def test_options_must_be_list():
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
            required=True,
            multiple=False,
            options = (hot, ice),
        )
        
def test_options_must_be_option_in_list():
    hot = Option(
        name="HOT",
        additional_price=Money(0),
    )

    with pytest.raises(TypeError):
        OptionGroup(
            name="온도",
            required=True,
            multiple=False,
            options = [hot, "ice"],
        )
