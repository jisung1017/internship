from src.domain.exceptions import OutOfStockError
from src.domain.payment import Payment
from src.domain.inventory import Inventory
from src.domain.order import Order
from src.domain.cart import Cart

class OrderService:
    def __init__(
            self,
            payment: Payment,
            inventory: Inventory,
    ):
        self.payment = payment
        self.inventory = inventory

    def checkout(self, cart: Cart) -> Order:
        order = Order.from_cart(cart)

        try:
            # 1. 재고 확인
            for item in order.items:
                if not self.inventory.can_consume(
                    item.menu.recipe,
                    item.quantity
                ):
                    raise OutOfStockError()
            
            # 2. 결제
            self.payment.pay(order)
            
            # 3. 재고 차감
            for item in order.items:
                self.inventory.consume(
                    item.menu.recipe,
                    item.quantity
                )

            return order
        
        finally:
            cart.clear()