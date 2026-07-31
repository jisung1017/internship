from sqlalchemy.orm import Session, joinedload

from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe  
from src.domain.recipe_item import RecipeItem
from src.infrastructure.models import (
    MenuModel,
    OptionGroupModel,
    RecipeItemModel,
)


class OrmMenuRepository:
    """SQLAlchemy ORM 기반 메뉴 레포지토리 구현체"""

    def __init__(self, session: Session):
        self._session = session

    def get_all(self) -> list[Menu]:
        models = (
            self._session.query(MenuModel)
            .options(
                joinedload(MenuModel.recipes).joinedload(RecipeItemModel.ingredient),
                joinedload(MenuModel.option_groups).joinedload(OptionGroupModel.options),
            )
            .all()
        )

        menus: list[Menu] = []
        for menu_model in models:
            recipe_items = [
                RecipeItem(
                    ingredient=Ingredient(
                        name=r.ingredient.name, unit=r.ingredient.unit
                    ),
                    quantity=Quantity(r.quantity),
                )
                for r in menu_model.recipes
            ]

            option_groups = [
                OptionGroup(
                    name=og.name,
                    options=[
                        Option(name=o.name, additional_price=Money(o.additional_price))
                        for o in og.options
                    ],
                    min_quantity=og.min_quantity,
                    max_quantity=og.max_quantity,
                )
                for og in menu_model.option_groups
            ]

            recipe = Recipe(items=recipe_items) if hasattr(Recipe, '__init__') else Recipe(recipe_items)

            menus.append(
                Menu(
                    name=menu_model.name,
                    price=Money(menu_model.price),
                    recipe=recipe,
                    option_groups=option_groups,
                )
            )

        return menus