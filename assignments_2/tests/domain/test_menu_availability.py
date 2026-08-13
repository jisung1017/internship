import pytest
from src.domain.category import Category
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.menu import Menu
from src.domain.menu_tag import MenuTag
from src.domain.money import Money
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem


@pytest.fixture
def coffee_bean():
    return Ingredient("원두", "g")


@pytest.fixture
def americano_menu(coffee_bean):
    # 원두 15g이 필요한 아메리카노 메뉴 (태그: BEST, NEW)
    recipe = Recipe(items=[RecipeItem(ingredient=coffee_bean, quantity=Quantity(15))])
    return Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=recipe,
        category=Category.COFFEE,
        tags=[MenuTag.BEST, MenuTag.NEW],
    )


def test_menu_tags_initialization(americano_menu):
    """메뉴 생성 시 태그가 올바르게 설정되는지 검증"""
    assert americano_menu.category == Category.COFFEE
    assert americano_menu.tags == [MenuTag.BEST, MenuTag.NEW]
    assert MenuTag.BEST in americano_menu.tags


def test_menu_availability_with_sufficient_inventory(americano_menu, coffee_bean):
    """재고가 충분할 때 is_available()은 True를 반환해야 함"""
    inventory = Inventory(
        items=[InventoryItem(ingredient=coffee_bean, quantity=Quantity(100))]
    )
    
    assert americano_menu.is_available(inventory) is True


def test_menu_availability_with_insufficient_inventory(americano_menu, coffee_bean):
    """재고가 부족할 때(필요량 15g > 보유량 10g) is_available()은 False를 반환해야 함"""
    inventory = Inventory(
        items=[InventoryItem(ingredient=coffee_bean, quantity=Quantity(10))]
    )
    
    assert americano_menu.is_available(inventory) is False


def test_menu_availability_when_manually_sold_out(americano_menu, coffee_bean):
    """관리자가 수동으로 품절(is_sold_out=True) 처리하면 재고가 충분해도 is_available()은 False여야 함"""
    inventory = Inventory(
        items=[InventoryItem(ingredient=coffee_bean, quantity=Quantity(100))]
    )
    
    # 관리자 품절 처리
    americano_menu.set_available(False)
    
    assert americano_menu.is_sold_out is True
    assert americano_menu.is_available(inventory) is False