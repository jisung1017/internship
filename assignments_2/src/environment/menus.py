from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.option_item import OptionItem
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem


def create_menu() -> list[Menu]:
    bean = Ingredient("원두")
    water = Ingredient("물")
    milk = Ingredient("우유")
    cup = Ingredient("컵")
    syrup = Ingredient("시럽")

    temperature_option = Option(
        name="온도",
        default_min=Quantity(1),
        default_max=Quantity(1),
        selection_mode="choice",
        default_option_name="HOT",
        items=[
            OptionItem(name="HOT", additional_price=Money(0)),
            OptionItem(name="ICE", additional_price=Money(0)),
        ],
    )

    shot_option = Option(
        name="샷 추가",
        default_min=Quantity(0),
        default_max=Quantity(4),
        selection_mode="count",
        items=[
            OptionItem(
                name="샷 추가",
                additional_price=Money(500),
                recipe=Recipe(items=[RecipeItem(bean, Quantity(10))]),
            )
        ],
    )

    syrup_option = Option(
        name="시럽 추가",
        default_min=Quantity(0),
        default_max=Quantity(2),
        selection_mode="count",
        items=[
            OptionItem(
                name="시럽 추가",
                additional_price=Money(200),
                recipe=Recipe(items=[RecipeItem(syrup, Quantity(10))]),
            )
        ],
    )

    americano = Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=Recipe(
            items=[
                RecipeItem(bean, Quantity(18)),
                RecipeItem(water, Quantity(250)),
                RecipeItem(cup, Quantity(1)),
            ]
        ),
        option_groups=[
            OptionGroup(option=temperature_option),
            OptionGroup(option=shot_option),
            OptionGroup(option=syrup_option),
        ],
    )

    latte = Menu(
        name="카페라떼",
        price=Money(4000),
        recipe=Recipe(
            items=[
                RecipeItem(bean, Quantity(18)),
                RecipeItem(water, Quantity(200)),
                RecipeItem(milk, Quantity(150)),
                RecipeItem(cup, Quantity(1)),
            ]
        ),
        option_groups=[
            OptionGroup(option=temperature_option),
            OptionGroup(option=shot_option),
            OptionGroup(option=syrup_option),
        ],
    )

    cappuccino = Menu(
        name="카푸치노",
        price=Money(4500),
        recipe=Recipe(
            items=[
                RecipeItem(bean, Quantity(10)),
                RecipeItem(milk, Quantity(40)),
                RecipeItem(cup, Quantity(1)),
            ]
        ),
        option_groups=[
            OptionGroup(option=temperature_option),
            OptionGroup(option=shot_option),
            OptionGroup(option=syrup_option),
        ],
    )

    return [americano, latte, cappuccino]