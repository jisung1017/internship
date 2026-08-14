import json
from pathlib import Path
from sqlalchemy.orm import Session
from src.infrastructure.models import (
    IngredientModel,
    InventoryItemModel,
    MenuModel,
    OptionGroupModel,
    OptionItemModel,
    OptionModel,
    OptionRecipeItemModel,
    RecipeItemModel,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def seed_initial_data_from_json(session: Session) -> None:
    """JSON 설정 파일을 읽어 DB에 기초 데이터(재고, 옵션, 메뉴)를 주입하는 시더"""
    # 이미 메뉴가 존재하면 시딩 스킵
    if session.query(MenuModel).first() is not None:
        return

    # 1. 재고 & 원재료 시딩
    inventory_path = BASE_DIR / "inventory.json"
    ingredients_map: dict[str, IngredientModel] = {}

    if inventory_path.exists():
        with open(inventory_path, "r", encoding="utf-8") as f:
            inventory_data = json.load(f)

        for item in inventory_data:
            ing = IngredientModel(name=item["name"], unit=item["unit"])
            session.add(ing)
            session.flush()
            ingredients_map[ing.name] = ing

            inv = InventoryItemModel(
                ingredient_id=ing.id, quantity=item["quantity"]
            )
            session.add(inv)

    # 2. 옵션 마스터 & 세부 아이템 시딩
    options_path = BASE_DIR / "options.json"
    options_map: dict[str, OptionModel] = {}

    if options_path.exists():
        with open(options_path, "r", encoding="utf-8") as f:
            options_data = json.load(f)

        for opt_data in options_data:
            option_master = OptionModel(
                name=opt_data["name"],
                default_min_select=opt_data["default_min_select"],
                default_max_select=opt_data["default_max_select"],
                selection_mode=opt_data["selection_mode"],
                default_option_name=opt_data.get("default_option_name"),
            )
            session.add(option_master)
            session.flush()
            options_map[option_master.name] = option_master

            # 세부 아이템 등록
            for item_data in opt_data.get("items", []):
                opt_item = OptionItemModel(
                    option_id=option_master.id,
                    name=item_data["name"],
                    additional_price=item_data["additional_price"],
                )
                session.add(opt_item)
                session.flush()

                # 옵션 레시피 등록 (예: 샷 추가 시 원두 10g 차감)
                if "recipe" in item_data:
                    for ing_name, qty in item_data["recipe"].items():
                        if ing_name in ingredients_map:
                            opt_recipe = OptionRecipeItemModel(
                                option_item_id=opt_item.id,
                                ingredient_id=ingredients_map[ing_name].id,
                                quantity=qty,
                            )
                            session.add(opt_recipe)

    # 3. 메뉴 & 레시피 & 옵션 그룹 연결 시딩
    menus_path = BASE_DIR / "menus.json"
    if menus_path.exists():
        with open(menus_path, "r", encoding="utf-8") as f:
            menus_data = json.load(f)

        for menu_data in menus_data:
            menu = MenuModel(
                name=menu_data["name"],
                price=menu_data["price"],
                category=menu_data["category"],
                tags=menu_data.get("tags", []),
            )
            session.add(menu)
            session.flush()

            # 메뉴 레시피 연결
            for ing_name, qty in menu_data.get("recipe", {}).items():
                if ing_name in ingredients_map:
                    recipe_item = RecipeItemModel(
                        menu_id=menu.id,
                        ingredient_id=ingredients_map[ing_name].id,
                        quantity=qty,
                    )
                    session.add(recipe_item)

            # 메뉴 옵션 그룹 연결
            for opt_config in menu_data.get("options", []):
                opt_name = opt_config["option_name"]
                if opt_name in options_map:
                    opt_group = OptionGroupModel(
                        menu_id=menu.id,
                        option_id=options_map[opt_name].id,
                        override_min_select=opt_config.get("override_min_select"),
                        override_max_select=opt_config.get("override_max_select"),
                        override_default_option_name=opt_config.get(
                            "override_default_option_name"
                        ),
                    )
                    session.add(opt_group)

    session.commit()