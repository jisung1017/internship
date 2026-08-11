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

    # 1. 옵션 마스터 생성 
    temperature_option = Option(
        name="온도",
        items=[
            OptionItem(name="HOT", additional_price=Money(0)),
            OptionItem(name="ICE", additional_price=Money(0)),
        ],
    )
    
    shot_option = Option(
        name="샷 추가",
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
        items=[
            OptionItem(
                name="시럽 추가",
                additional_price=Money(200),
                recipe=Recipe(items=[RecipeItem(syrup, Quantity(10))]),
            )
        ],
    )

    # 2. 메뉴에 OptionGroup(매핑 테이블)을 통해 마스터 옵션 할당
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
            OptionGroup(option=temperature_option, min_quantity=Quantity(1), max_quantity=Quantity(1)),
            OptionGroup(option=shot_option, min_quantity=Quantity(0), max_quantity=Quantity(4), selection_mode="count"),
            OptionGroup(option=syrup_option, min_quantity=Quantity(0), max_quantity=Quantity(2), selection_mode="count"),
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
            OptionGroup(option=temperature_option, min_quantity=Quantity(1), max_quantity=Quantity(1)),
            OptionGroup(option=shot_option, min_quantity=Quantity(0), max_quantity=Quantity(4), selection_mode="count"),
            OptionGroup(option=syrup_option, min_quantity=Quantity(0), max_quantity=Quantity(2), selection_mode="count"),
        ],
    )

    return [americano, latte]