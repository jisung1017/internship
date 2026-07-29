from unittest.mock import MagicMock

from src.application.kiosk_loader import KioskLoaderService
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory, InventoryItem
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe


class TestKioskLoaderService:
    def test_load_assembles_menus_and_inventory_from_repositories(self):
        """KioskLoaderService는 트랜잭션 내에서 두 Repository를 생성하여 초기 상태를 로드한다."""
        # Given
        dummy_menu = Menu(name="아메리카노", price=Money(3000), recipe=Recipe(items=[]))
        dummy_inventory = Inventory(items=[InventoryItem(Ingredient("원두"), Quantity(100))])

        mock_menu_repo = MagicMock()
        mock_menu_repo.find_all.return_value = [dummy_menu]

        mock_inventory_repo = MagicMock()
        mock_inventory_repo.load.return_value = dummy_inventory

        mock_db = MagicMock()

        # When
        loader_service = KioskLoaderService(
            database=mock_db,
            menu_repository_factory=lambda conn: mock_menu_repo,
            inventory_repository_factory=lambda conn: mock_inventory_repo,
        )
        state = loader_service.load()

        # Then
        assert state.menus == [dummy_menu]
        assert state.inventory == dummy_inventory
        mock_db.transaction.assert_called_once()
        mock_menu_repo.find_all.assert_called_once()
        mock_inventory_repo.load.assert_called_once()