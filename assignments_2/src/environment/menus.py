from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem
from src.domain.option_group import OptionGroup
from src.domain.option import Option

def create_menu() -> list[Menu]:
    bean = Ingredient("원두")
    water = Ingredient("물")
    milk = Ingredient("우유")
    cup = Ingredient("컵")
    syrup = Ingredient("시럽")

    temperature_group = OptionGroup(
        name="온도",
        min_quantity=Quantity(1),
        max_quantity=Quantity(1),
        options=[
            Option(name="HOT", additional_price=Money(0)),
            Option(name="ICE", additional_price=Money(0)),
        ],
    )

    shot_group = OptionGroup(
        name="샷추가",
        min_quantity=Quantity(0),
        max_quantity=Quantity(4),
        options=[Option(name="샷추가", additional_price=Money(500), recipe=Recipe(items=[RecipeItem(bean, Quantity(10))]))],
        selection_mode="count",
    )

    syrup_group = OptionGroup(
        name="시럽추가",
        min_quantity=Quantity(0),
        max_quantity=Quantity(2),
        options=[Option(name="시럽추가", additional_price=Money(200), recipe=Recipe(items=[RecipeItem(syrup, Quantity(10))]))],
        selection_mode="count",
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
        option_groups=[temperature_group, shot_group, syrup_group],
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
        option_groups=[temperature_group, shot_group, syrup_group],
    )

    espresso = Menu(
        name="에스프레소",
        price=Money(3500),
        recipe=Recipe(
            items=[
                RecipeItem(bean, Quantity(10)),
                RecipeItem(cup, Quantity(1)),
            ]
        ),
        option_groups=[shot_group],
    )

    cappuccino = Menu(
        name="카푸치노",
        price=Money(4500),
        recipe=Recipe(
            items=[
                RecipeItem(bean,Quantity(10)),
                RecipeItem(milk, Quantity(40)),
                RecipeItem(cup, Quantity(1)),
            ]
        ),
        option_groups=[shot_group, syrup_group],
    )

    caramel_macchiato = Menu(
        name="카라멜마키아토",
        price=Money(5500),
        recipe=Recipe(
            items=[
                RecipeItem(bean, Quantity(10)),
                RecipeItem(milk, Quantity(30)),
                RecipeItem(cup, Quantity(1)),
                RecipeItem(syrup, Quantity(10)),
            ]
        ),
        option_groups=[temperature_group, shot_group, syrup_group],
    )

    return [americano, latte, espresso, cappuccino, caramel_macchiato]