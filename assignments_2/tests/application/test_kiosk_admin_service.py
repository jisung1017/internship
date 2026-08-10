import pytest

from src.application.kiosk_admin_service import KioskAdminService
from src.domain.ingredient import Ingredient
from src.domain.quantity import Quantity
from tests.test_acceptance import FakeUnitOfWork, build_inventory


def test_admin_service_get_inventory():
    inventory = build_inventory(1000)
    fake_uow = FakeUnitOfWork(inventory=inventory)
    admin_service = KioskAdminService(uow=fake_uow)

    result = admin_service.get_inventory()

    assert result.get_quantity(Ingredient("원두")) == Quantity(1000)


def test_admin_service_restock():
    inventory = build_inventory(1000)
    fake_uow = FakeUnitOfWork(inventory=inventory)
    admin_service = KioskAdminService(uow=fake_uow)

    admin_service.restock("원두", Quantity(500))

    assert admin_service.get_inventory().get_quantity(Ingredient("원두")) == Quantity(1500)
    assert fake_uow.committed is True