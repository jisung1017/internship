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

    with database.transaction() as connection:
        menus = PostgresMenuRepository(connection).find_all()
        inventory = PostgresInventoryRepository(connection).load()

    payment = Payment(balance=Money(10000))
    order_service = OrderService(payment, inventory)
    session = KioskSession(
        menus=menus,
        order_service=order_service,
        inventory_persister=PostgresInventoryPersister(database),
        order_persister=PostgresOrderPersister(database),
        order_history_reader=PostgresOrderHistoryReader(database),
    )

    CLI(session).run()


if __name__ == "__main__":
    main()