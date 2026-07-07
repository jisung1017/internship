from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem

def create_menu() -> list[Menu]:
    bean = Ingredient("원두")
    water = Ingredient("물")
    milk = Ingredient("우유")
    cup = Ingredient("컵")

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
        option_groups=[],
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
        option_groups=[],
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
        option_groups=[],
    )

    return [americano, latte, espresso, cappuccino]