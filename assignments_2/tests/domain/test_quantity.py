import pytest

from src.domain.quantity import Quantity


class TestQuantityValidation:

    def test_create_quantity(self): 
        quantity = Quantity(10)
        assert quantity.value == 10

    def test_float_quantity_raises_type_error(self):
        with pytest.raises(TypeError):
            Quantity(1.7)

    def test_string_quantity_raises_type_error(self):
        with pytest.raises(TypeError):
            Quantity("1000")

    def test_bool_quantity_raises_type_error(self):
        with pytest.raises(TypeError):
            Quantity(True)

    def test_negative_quantity_raises_value_error(self):
        with pytest.raises(ValueError):
            Quantity(-9999)

    def test_zero_quantity(self):
        quantity = Quantity(0)
        assert quantity.value == 0


class TestQuantityBehavior:
           
    def test_quantity_add(self):
        quantity1 = Quantity(1000)
        quantity2 = Quantity(400)
        assert quantity1.add(quantity2) == Quantity(1400)

    def test_quantity_add_zero(self):
        quantity = Quantity(5)
        assert quantity.add(Quantity(0)) == Quantity(5)

    def test_quantity_subtract(self):
        quantity1 = Quantity(1000)
        quantity2 = Quantity(400)
        assert quantity1.subtract(quantity2) == Quantity(600)    

    def test_quantity_subtract_zero(self):
        quantity = Quantity(5)
        assert quantity.subtract(Quantity(0)) == Quantity(5)

    def test_quantity_subtract_negative_result_raises_value_error(self):
        quantity1 = Quantity(300)
        quantity2 = Quantity(500)
        with pytest.raises(ValueError):
            quantity1.subtract(quantity2)

    def test_quantity_multiply(self):
        quantity = Quantity(1000)
        assert quantity.multiply(3) == Quantity(3000)

    def test_quantity_multiply_zero(self):
        quantity = Quantity(5)
        assert quantity.multiply(0) == Quantity(0)

    def test_quantity_multiply_negative_result_raises_value_error(self):
        quantity = Quantity(300)
        with pytest.raises(ValueError):
            quantity.multiply(-1)


class TestQuantityComparison: 
    
    def test_quantity_equal(self):
        assert Quantity(1000) == Quantity(1000)

    def test_quantity_not_equal(self):
        assert Quantity(1000) != Quantity(3000)

    @pytest.mark.parametrize("left, right, expected", [
        (Quantity(1000), Quantity(2000), False),
        (Quantity(1000), Quantity(1000), False),
        (Quantity(2000), Quantity(1000), True),
    ])
    def test_quantity_greater_than(self, left, right, expected):
        assert left.is_greater_than(right) is expected

class TestQuantityImmutability: 

    def test_quantity_is_immutable_after_add(self):
        quantity1 = Quantity(300)
        quantity2 = Quantity(500)
        
        result = quantity1.add(quantity2)

        assert result == Quantity(800)
        assert result is not quantity1 