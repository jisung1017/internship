import pytest

from src.domain.money import Money
from src.domain.quantity import Quantity


class TestMoneyValidation:

    def test_money_must_be_integer(self):
        with pytest.raises(TypeError):
            Money(1.7)

        with pytest.raises(TypeError):
            Money("1000")

        with pytest.raises(TypeError):
            Money(True)

    def test_money_cannot_be_negative(self):
        with pytest.raises(ValueError):
            Money(-1)


class TestMoneyBehavior:

    def test_add(self):
        assert Money(1000).add(Money(400)) == Money(1400)

    def test_add_zero(self):
        assert Money(1000).add(Money(0)) == Money(1000)

    def test_subtract(self):
        assert Money(1000).subtract(Money(400)) == Money(600)

    def test_subtract_zero(self):
        assert Money(1000).subtract(Money(0)) == Money(1000)

    def test_subtract_same_amount_returns_zero(self):
        assert Money(1000).subtract(Money(1000)) == Money(0)

    def test_subtract_result_cannot_be_negative(self):
        with pytest.raises(ValueError):
            Money(300).subtract(Money(500))

    def test_multiply(self):
        assert Money(3000).multiply(Quantity(2)) == Money(6000)

    def test_multiply_by_zero(self):
        assert Money(3000).multiply(Quantity(0)) == Money(0)

    def test_multiplier_must_be_quantity(self):
        with pytest.raises(TypeError):
            Money(3000).multiply(2)


class TestMoneyComparison:

    def test_equal(self):
        assert Money(1000) == Money(1000)

    def test_not_equal(self):
        assert Money(1000) != Money(3000)

    def test_less_than(self):
        assert Money(1000) < Money(2000)

    def test_less_than_or_equal(self):
        assert Money(1000) <= Money(1000)
        assert Money(1000) <= Money(2000)

    def test_greater_than(self):
        assert Money(3000) > Money(2000)

    def test_greater_than_or_equal(self):
        assert Money(3000) >= Money(3000)
        assert Money(3000) >= Money(2000)

    def test_equal_values_are_not_less_than(self):
        assert not Money(1000) < Money(1000)

    def test_equal_values_are_not_greater_than(self):
        assert not Money(1000) > Money(1000)


class TestMoneyImmutability:

    def test_add_returns_new_instance(self):
        money = Money(1000)

        result = money.add(Money(500))

        assert result == Money(1500)
        assert result is not money

    def test_subtract_returns_new_instance(self):
        money = Money(1000)

        result = money.subtract(Money(500))

        assert result == Money(500)
        assert result is not money

    def test_multiply_returns_new_instance(self):
        money = Money(3000)

        result = money.multiply(Quantity(2))

        assert result == Money(6000)
        assert result is not money