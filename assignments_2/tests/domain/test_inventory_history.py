from datetime import datetime, timedelta
import pytest

from src.domain.ingredient import Ingredient
from src.domain.inventory_history import InventoryHistory


class TestInventoryHistoryValidation:

    def test_ingredient_must_be_ingredient(self):
        with pytest.raises(TypeError):
            InventoryHistory(ingredient="원두", change=100, reason="RESTOCK")

    def test_change_must_be_int(self):
        with pytest.raises(TypeError):
            InventoryHistory(ingredient=Ingredient("원두"), change="100", reason="RESTOCK")

    def test_change_must_not_be_bool(self):
        with pytest.raises(TypeError):
            InventoryHistory(ingredient=Ingredient("원두"), change=True, reason="RESTOCK")

    def test_change_cannot_be_zero(self):
        with pytest.raises(ValueError):
            InventoryHistory(ingredient=Ingredient("원두"), change=0, reason="RESTOCK")

    def test_reason_must_be_known_value(self):
        with pytest.raises(ValueError):
            InventoryHistory(ingredient=Ingredient("원두"), change=100, reason="너 뭐야")

    def test_reason_is_required(self):
        with pytest.raises(TypeError):
            InventoryHistory(ingredient=Ingredient("원두"), change=100)


class TestInventoryHistoryTimestamp:

    def test_timestamp_defaults_to_now(self, make_ingredient):
        before = datetime.now()
        history = InventoryHistory(ingredient=make_ingredient(), change=100, reason="RESTOCK") 
        after = datetime.now()

        assert before - timedelta(seconds=1) <= history.timestamp <= after + timedelta(seconds=1)

    def test_timestamp_can_be_explicitly_set(self, make_ingredient):
        fixed_time = datetime(2026, 1, 1, 12, 0, 0)

        history = InventoryHistory(
            ingredient=make_ingredient(), 
            change=100,
            reason="RESTOCK",
            timestamp=fixed_time,
        )

        assert history.timestamp == fixed_time


class TestInventoryHistoryImmutability:

    def test_cannot_mutate_fields_after_creation(self, make_ingredient):
        history = InventoryHistory(ingredient=make_ingredient(), change=100, reason="RESTOCK") 

        with pytest.raises(AttributeError):
            history.change = 200
