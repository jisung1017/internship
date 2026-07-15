from src.application.kiosk_session import KioskSession
from src.application.order_service import OrderService
from src.domain.money import Money
from src.domain.payment import Payment
from src.environment.inventory_data import create_inventory
from src.environment.menus import create_menu
from src.interface.cli import CLI


def main() -> None:
    menus = create_menu()
    inventory = create_inventory()
    payment = Payment(balance=Money(10000))
    order_service = OrderService(payment, inventory)
    session = KioskSession(menus=menus, order_service=order_service)

    CLI(session).run()


if __name__ == "__main__":
    main()