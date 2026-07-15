from datetime import datetime, timedelta
import pytest

from src.domain.ingredient import Ingredient
from src.domain.inventory_history import InventoryHistory


class TestInventoryHistoryValidation:

    @pytest.mark.parametrize(
        "ingredient, change, reason, expected_exception",
        [
            ("원두", 100, "RESTOCK", TypeError),        # ingredient 타입 오류
            (Ingredient("원두"), "100", "RESTOCK", TypeError),  # change 타입 오류 (문자열)
            (Ingredient("원두"), True, "RESTOCK", TypeError),   # change 타입 오류 (불리언)
            (Ingredient("원두"), 0, "RESTOCK", ValueError),     # change 값 오류 (0)
            (Ingredient("원두"), 100, "너뭐야", ValueError),    # reason 값 오류
        ],
    )
    def test_invalid_arguments_raise_exception(
        self, ingredient, change, reason, expected_exception
    ):
        with pytest.raises(expected_exception):
            InventoryHistory(ingredient=ingredient, change=change, reason=reason)

    def test_reason_is_required(self, make_ingredient):
        with pytest.raises(TypeError):
            InventoryHistory(ingredient=make_ingredient, change=100)


class TestInventoryHistoryTimestamp:

    def test_timestamp_defaults_to_now(self, make_ingredient):
        before = datetime.now()
        history = InventoryHistory(ingredient=make_ingredient, change=100, reason="RESTOCK")
        after = datetime.now()

        assert before - timedelta(seconds=1) <= history.timestamp <= after + timedelta(seconds=1)

    def test_timestamp_can_be_explicitly_set(self, make_ingredient):
        fixed_time = datetime(2026, 1, 1, 12, 0, 0)

        history = InventoryHistory(
            ingredient=make_ingredient,
            change=100,
            reason="RESTOCK",
            timestamp=fixed_time,
        )

        assert history.timestamp == fixed_time


class TestInventoryHistoryImmutability:

    def test_cannot_mutate_fields_after_creation(self, make_ingredient):
        history = InventoryHistory(ingredient=make_ingredient, change=100, reason="RESTOCK")

        with pytest.raises(AttributeError):
            history.change = 200
