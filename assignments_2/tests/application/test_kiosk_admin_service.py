from datetime import datetime
from unittest.mock import MagicMock

from src.application.kiosk_admin_service import KioskAdminService
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory, InventoryItem
from src.domain.money import Money
from src.domain.order_record import OrderRecord, OrderRecordItem
from src.domain.payment import Payment
from src.domain.quantity import Quantity


class TestKioskAdminService:
    def test_restock_updates_inventory_and_triggers_persister(self):
        """재고 입고 시 메모리 재고가 증가하고 InventoryPersister가 호출된다."""
        # Given
        inventory = Inventory(items=[InventoryItem(Ingredient("원두"), Quantity(100))])

        mock_persister = MagicMock()
        admin_service = KioskAdminService(
            inventory=inventory,
            inventory_persister=mock_persister,
        )

        # When
        admin_service.restock("원두", Quantity(50))

        # Then
        assert inventory.get_quantity(Ingredient("원두")) == Quantity(150)
        mock_persister.persist.assert_called_once_with(inventory)

    def test_get_today_sales_total_calculates_sum_from_history_reader(self):
        """오늘의 주문 기록 목록을 기반으로 총매출 금액을 올바르게 계산한다."""
        # Given
        inventory = Inventory(items=[])

        mock_reader = MagicMock()
        mock_reader.find_today.return_value = [
            OrderRecord(
                id=1,
                created_at=datetime.now(),
                total_price=Money(3000),
                items=[OrderRecordItem(menu_name="아메리카노", quantity=1, line_total=Money(3000))],
            ),
            OrderRecord(
                id=2,
                created_at=datetime.now(),
                total_price=Money(4500),
                items=[OrderRecordItem(menu_name="카푸치노", quantity=1, line_total=Money(4500))],
            ),
        ]

        admin_service = KioskAdminService(
            inventory=inventory,
            order_history_reader=mock_reader,
        )

        # When
        sales_total = admin_service.get_today_sales_total()

        # Then
        assert sales_total == Money(7500)