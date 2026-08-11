import pytest
from src.domain.ingredient import Ingredient
from src.domain.quantity import Quantity
from tests.test_acceptance import FakeUnitOfWork, build_inventory


def test_unit_of_work_commit():
    inventory = build_inventory(1000)
    uow = FakeUnitOfWork(inventory=inventory)

    with uow:
        current_inv = uow.inventories.load()
        current_inv.restock(Ingredient("원두"), Quantity(200))
        uow.inventories.save(current_inv)
        uow.commit()

    assert uow.committed is True
    assert uow.inventories.load().get_quantity(Ingredient("원두")) == Quantity(1200)


def test_unit_of_work_rollback_on_exception():
    inventory = build_inventory(1000)
    uow = FakeUnitOfWork(inventory=inventory)

    try:
        with uow:
            current_inv = uow.inventories.load()
            current_inv.restock(Ingredient("원두"), Quantity(200))
            raise RuntimeError("Test Exception")
    except RuntimeError:
        pass

    assert uow.rolled_back is True