import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.application.cart_service import CartService
from src.application.kiosk_admin_service import KioskAdminService
from src.application.order_application_service import OrderApplicationService
from src.domain.payment import Payment
from src.infrastructure.db import DEFAULT_DATABASE_URL
from src.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from src.interface.cli import CLI


def main() -> None:
    db_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    if db_url.startswith("postgresql://"):
        sqlalchemy_url = db_url.replace("postgresql://", "postgresql+psycopg://")
    else:
        sqlalchemy_url = db_url

    engine = create_engine(sqlalchemy_url, pool_pre_ping=True)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    uow = SqlAlchemyUnitOfWork(session_factory=session_factory)

    order_app_service = OrderApplicationService(uow=uow)
    admin_service = KioskAdminService(uow=uow)
    cart_service = CartService()
    payment = Payment(is_approved=True)

    menus = order_app_service.get_all_menus()
    inventory = admin_service.get_inventory()

    cli = CLI(
        menus=menus,
        payment=payment,
        inventory=inventory,
        cart_service=cart_service,
        order_app_service=order_app_service,
        admin_service=admin_service,
    )
    cli.run()


if __name__ == "__main__":
    main()