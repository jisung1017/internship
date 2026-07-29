from src.application.cart_service import CartService
from src.application.kiosk_admin_service import KioskAdminService
from src.application.kiosk_loader import KioskLoaderService
from src.application.order_application_service import OrderApplicationService
from src.domain.money import Money
from src.domain.payment import Payment
from src.infrastructure.db import Database
from src.infrastructure.repositories.postgres_inventory_persister import (
    PostgresInventoryPersister,
)
from src.infrastructure.repositories.postgres_inventory_repository import (
    PostgresInventoryRepository,
)
from src.infrastructure.repositories.postgres_menu_repository import (
    PostgresMenuRepository,
)
from src.infrastructure.repositories.postgres_order_history_reader import (
    PostgresOrderHistoryReader,
)
from src.infrastructure.repositories.postgres_order_persister import (
    PostgresOrderPersister,
)
from src.interface.cli import CLI


def main() -> None:
    database = Database()

    kiosk_loader = KioskLoaderService(
        database=database,
        menu_repository_factory=PostgresMenuRepository,
        inventory_repository_factory=PostgresInventoryRepository,
    )
    state = kiosk_loader.load()

    payment = Payment(balance=Money(100000000))

    # 무상태 애플리케이션 서비스 인스턴스화
    cart_service = CartService()
    order_app_service = OrderApplicationService(
        order_persister=PostgresOrderPersister(database)
    )
    admin_service = KioskAdminService(
        inventory=state.inventory,
        inventory_persister=PostgresInventoryPersister(database),
        order_history_reader=PostgresOrderHistoryReader(database),
    )

    cli = CLI(
        menus=state.menus,
        payment=payment,
        inventory=state.inventory,
        cart_service=cart_service,
        order_app_service=order_app_service,
        admin_service=admin_service,
    )
    cli.run()


if __name__ == "__main__":
    main()