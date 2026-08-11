from sqlalchemy.orm import Session, joinedload
from src.application.menu_repository import MenuRepository
from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.option_item import OptionItem
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem
from src.infrastructure.models import (
    MenuModel,
    OptionGroupModel,
    OptionItemModel,
    OptionModel,
    OptionRecipeItemModel,
    RecipeItemModel,
)

class OrmMenuRepository(MenuRepository):
    def __init__(self, session: Session):
        self._session = session

    def find_all(self) -> list[Menu]:
        models = (
            self._session.query(MenuModel)
            .options(
                joinedload(MenuModel.recipes).joinedload(RecipeItemModel.ingredient),
                joinedload(MenuModel.option_groups)
                .joinedload(OptionGroupModel.option)
                .joinedload(OptionModel.items)
                .joinedload(OptionItemModel.recipes)
                .joinedload(OptionRecipeItemModel.ingredient),
            )
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_by_name(self, name: str) -> Menu | None:
        model = (
            self._session.query(MenuModel)
            .filter(MenuModel.name == name)
            .options(
                joinedload(MenuModel.recipes).joinedload(RecipeItemModel.ingredient),
                joinedload(MenuModel.option_groups)
                .joinedload(OptionGroupModel.option)
                .joinedload(OptionModel.items)
                .joinedload(OptionItemModel.recipes)
                .joinedload(OptionRecipeItemModel.ingredient),
            )
            .first()
        )
        return self._to_domain(model) if model else None

    def _to_domain(self, menu_model: MenuModel) -> Menu:
        recipe_items = [
            RecipeItem(
                ingredient=Ingredient(name=r.ingredient.name, unit=r.ingredient.unit),
                quantity=Quantity(r.quantity),
            ) for r in menu_model.recipes
        ]
        
        option_groups = [
            OptionGroup(
                option=Option(
                    name=og.option.name,
                    items=[
                        OptionItem(
                            name=oi.name,
                            additional_price=Money(oi.additional_price),
                            recipe=Recipe(
                                items=[
                                    RecipeItem(
                                        ingredient=Ingredient(
                                            name=ori.ingredient.name, unit=ori.ingredient.unit
                                        ),
                                        quantity=Quantity(ori.quantity),
                                    ) for ori in oi.recipes
                                ]
                            ),
                        ) for oi in og.option.items
                    ],
                ),
                min_quantity=Quantity(og.min_select),
                max_quantity=Quantity(og.max_select),
                selection_mode=og.selection_mode,
            ) for og in menu_model.option_groups
        ]
        
        return Menu(
            name=menu_model.name,
            price=Money(menu_model.price),
            recipe=Recipe(items=recipe_items),
            option_groups=option_groups,
        )