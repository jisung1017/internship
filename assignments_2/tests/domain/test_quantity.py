import pytest

from src.domain.quantity import Quantity

def test_create_quantity():
    quantity = Quantity(10)

    assert quantity.value == 10

def test_float_quantity_raises_type_error():
    with pytest.raises(TypeError):
        Quantity(1.7)

def test_string_quantity_raises_type_error():
    with pytest.raises(TypeError):
        Quantity("1000")

def test_bool_quantity_raises_type_error():
    with pytest.raises(TypeError):
        Quantity(True)


def test_negative_quantity_raises_value_error():
    with pytest.raises(ValueError):
        Quantity(-9999)
        
def test_quantity_add():
    quantity1 = Quantity(1000)
    quantity2 = Quantity(400)

    result = quantity1.add(quantity2)

    assert result == Quantity(1400)

def test_quantity_subtract():
    quantity1 = Quantity(1000)
    quantity2 = Quantity(400)

    result = quantity1.subtract(quantity2)

    assert result == Quantity(600)    

def test_quantity_subtract_negative_result_raises_value_error():
    quantity1 = Quantity(300)
    quantity2 = Quantity(500)

    with pytest.raises(ValueError):
        quantity1.subtract(quantity2)

def test_quantity_multiply():
    quantity = Quantity(1000)
    
    result = quantity.multiply(3)

    assert result == Quantity(3000)

def test_quantity_multiply_negative_result_raises_value_error():
    quantity = Quantity(300)

    with pytest.raises(ValueError):
        quantity.multiply(-1)

def test_quantity_equal():
    assert Quantity(1000) == Quantity(1000)

def test_quantity_not_equal():
    assert Quantity(1000) != Quantity(3000)

def test_zero_quantity():
    quantity = Quantity(0)

    assert quantity.value == 0

def test_quantity_is_immutable_after_add():
    quantity1 = Quantity(300)
    quantity2 = Quantity(500)

    _ = quantity1.add(quantity2)

    assert quantity1 == Quantity(300)
    assert quantity2 == Quantity(500)

def test_quantity_add_zero():
    quantity = Quantity(5)

    result = quantity.add(Quantity(0))

    assert result == Quantity(5)

def test_quantity_subtract_zero():
    quantity = Quantity(5)

    result = quantity.subtract(Quantity(0))

    assert result == Quantity(5)

def test_quantity_multiply_zero():
    quantity = Quantity(5)

    result = quantity.multiply(0)

    assert result == Quantity(0)