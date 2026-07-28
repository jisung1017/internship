from src.application.checkout_service import CheckoutService
from src.application.kiosk_admin_service import KioskAdminService
from src.application.kiosk_session import KioskSession
from src.application.order_service import OrderService
from src.domain.money import Money
from src.domain.payment import Payment
from src.infrastructure.db import Database
from src.infrastructure.repositories.postgres_inventory_persister import (
    PostgresInventoryPersister,
)
from src.infrastructure.repositories.postgres_kiosk_loader import (
    PostgresKioskStateLoader,
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

    state = PostgresKioskStateLoader(database).load()

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