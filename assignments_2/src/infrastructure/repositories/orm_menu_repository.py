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
from src.domain.category import Category
from src.domain.menu_tag import MenuTag
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

    def find_all(
        self, category: Category | None = None, tag: MenuTag | None = None
    ) -> list[Menu]:
        query = self._session.query(MenuModel)

        # 1. 카테고리 DB 쿼리 필터링
        if category is not None:
            category_val = (
                category.value if isinstance(category, Category) else category
            )
            query = query.filter(MenuModel.category == category_val)

        models = (
            query.options(
                joinedload(MenuModel.recipes).joinedload(RecipeItemModel.ingredient),
                joinedload(MenuModel.option_groups)
                .joinedload(OptionGroupModel.option)
                .joinedload(OptionModel.items)
                .joinedload(OptionItemModel.recipes)
                .joinedload(OptionRecipeItemModel.ingredient),
            )
            .order_by(MenuModel.id)
            .all()
        )

        domain_menus = [self._to_domain(m) for m in models]

        # 2. 태그 메모리 필터링 (PostgreSQL/SQLite 멀티 DB 호환성 보장)
        if tag is not None:
            domain_menus = [m for m in domain_menus if tag in m.tags]

        return domain_menus

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
                ingredient=Ingredient(
                    name=r.ingredient.name, unit=r.ingredient.unit
                ),
                quantity=Quantity(r.quantity),
            )
            for r in menu_model.recipes
        ]

        option_groups = [
            OptionGroup(
                option=Option(
                    name=og.option.name,
                    default_min=Quantity(og.option.default_min_select),
                    default_max=Quantity(og.option.default_max_select),
                    selection_mode=og.option.selection_mode,
                    default_option_name=og.option.default_option_name,
                    items=[
                        OptionItem(
                            id=oi.id,  # DB PK 주입
                            name=oi.name,
                            additional_price=Money(oi.additional_price),
                            recipe=Recipe(
                                items=[
                                    RecipeItem(
                                        ingredient=Ingredient(
                                            name=ori.ingredient.name,
                                            unit=ori.ingredient.unit,
                                        ),
                                        quantity=Quantity(ori.quantity),
                                    )
                                    for ori in oi.recipes
                                ]
                            ),
                        )
                        for oi in og.option.items
                    ],
                ),
                override_min_quantity=Quantity(og.override_min_select)
                if og.override_min_select is not None
                else None,
                override_max_quantity=Quantity(og.override_max_select)
                if og.override_max_select is not None
                else None,
                override_default_option_name=og.override_default_option_name,
            )
            for og in menu_model.option_groups
        ]

        domain_tags = [MenuTag(tag_str) for tag_str in (menu_model.tags or [])]

        return Menu(
            id=menu_model.id,
            name=menu_model.name,
            price=Money(menu_model.price),
            recipe=Recipe(items=recipe_items),
            category=Category(menu_model.category),
            tags=domain_tags,
            option_groups=option_groups,
            is_sold_out=menu_model.is_sold_out,
        )