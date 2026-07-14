from dataclasses import dataclass

from example_2.interfaces.domain.cart import Cart


@dataclass(frozen=True)
class PaymentResult:
    amount: int


@dataclass
class PaymentService:
    def pay(self, cart: Cart):
        if cart.is_empty():
            raise ValueError("결제할 상품이 없어요.")
        return PaymentResult(amount=cart.total_cost())
