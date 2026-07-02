import pytest

from src.domain.money import Money

def test_create_money():
    money = Money(2026)

    assert money.amount == 2026

def test_float_money_raises_type_error():
    with pytest.raises(TypeError):
        Money(1.7)

def test_string_money_raises_type_error():
    with pytest.raises(TypeError):
        Money("1000")

def test_bool_money_raises_type_error():
    with pytest.raises(TypeError):
        Money(True)


def test_negative_money_raises_value_error():
    with pytest.raises(ValueError):
        Money(-9999)
        
def test_money_add():
    money1 = Money(1000)
    money2 = Money(400)

    result = money1.add(money2)

    assert result == Money(1400)

def test_money_subtract():
    money1 = Money(1000)
    money2 = Money(400)

    result = money1.subtract(money2)

    assert result == Money(600)    

def test_money_subtract_negative_result_raises_value_error():
    money1 = Money(300)
    money2 = Money(500)

    with pytest.raises(ValueError):
        money1.subtract(money2)

def test_money_multiply():
    money = Money(1000)
    
    result = money.multiply(3)

    assert result == Money(3000)

def test_money_multiply_negative_result_raises_value_error():
    money = Money(300)

    with pytest.raises(ValueError):
        money.multiply(-1)

def test_money_equal():
    assert Money(1000) == Money(1000)

def test_money_not_equal():
    assert Money(1000) != Money(3000)

def test_zero_money():
    money = Money(0)

    assert money.amount == 0

def test_money_is_immutable_after_add():
    money1 = Money(300)
    money2 = Money(500)

    _ = money1.add(money2)

    assert money1 == Money(300)
    assert money2 == Money(500)

def test_money_add_zero():
    money = Money(5)

    result = money.add(Money(0))

    assert result == Money(5)

def test_money_subtract_zero():
    money = Money(5)

    result = money.subtract(Money(0))

    assert result == Money(5)

def test_money_multiply_zero():
    money = Money(5)

    result = money.multiply(0)

    assert result == Money(0)