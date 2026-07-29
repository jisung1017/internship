from src.application.checkout_service import CheckoutService
from src.application.kiosk_admin_service import KioskAdminService
from src.application.kiosk_loader import KioskLoaderService
from src.application.kiosk_session import KioskSession
from src.application.order_service import OrderService
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

    # Application 계층의 KioskLoaderService가 단일 책임 Repository들을 조합하여 초기 상태를 로드합니다.
    kiosk_loader = KioskLoaderService(
        database=database,
        menu_repository_factory=PostgresMenuRepository,
        inventory_repository_factory=PostgresInventoryRepository,
    )
    state = kiosk_loader.load()

    payment = Payment(balance=Money(100000000))
    order_service = OrderService(payment, state.inventory)

    checkout_service = CheckoutService(
        order_service=order_service,
        order_persister=PostgresOrderPersister(database),
    )
    admin_service = KioskAdminService(
        order_service=order_service,
        inventory_persister=PostgresInventoryPersister(database),
        order_history_reader=PostgresOrderHistoryReader(database),
    )

    session = KioskSession(
        menus=state.menus,
        order_service=order_service,
        checkout_service=checkout_service,
    )

    CLI(session, admin_service).run()


if __name__ == "__main__":
    main()