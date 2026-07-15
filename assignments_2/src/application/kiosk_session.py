from dataclasses import dataclass, field
from enum import Enum, auto

from src.application.order_service import OrderService
from src.application.pending_order import PendingOrder
from src.domain.cart import Cart
from src.domain.exceptions import InsufficientBalanceError, OutOfStockError
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.quantity import Quantity


class StepType(Enum):
    MENU = auto()
    OPTION = auto()
    QUANTITY = auto()
    CART = auto()
    PAYMENT = auto()
    COMPLETE = auto()
    END = auto()


@dataclass
class KioskSession:
    menus: list[Menu]
    order_service: OrderService
    cart: Cart = field(default_factory=Cart)
    step: StepType = StepType.MENU
    pending_order: PendingOrder | None = None

    def get_balance(self) -> Money:
        return self.order_service.payment.balance

    def get_selected_menu(self) -> Menu | None:
        if self.pending_order is None:
            return None

        return self.pending_order.menu

    def current_option_group(self) -> OptionGroup | None:
        if self.pending_order is None:
            return None

        return self.pending_order.current_option_group()

    def current_option_group_index(self) -> int | None:
        if self.pending_order is None:
            return None

        if self.pending_order.is_option_selection_done():
            return None

        return self.pending_order.group_index

    def get_menu(self, index: int) -> Menu:
        if not 1 <= index <= len(self.menus):
            raise ValueError("잘못된 메뉴 번호입니다.")

        return self.menus[index - 1]

    def select_menu(self, index: int) -> None:
        menu = self.get_menu(index)

        self.pending_order = PendingOrder(menu=menu)
        self.step = StepType.OPTION if menu.option_groups else StepType.QUANTITY

    def select_option_group(self, selected: list[Option]) -> None:
        if self.pending_order is None:
            raise ValueError("선택 중인 메뉴가 없습니다.")

        self.pending_order.select_current_option_group(selected)
        self.step = StepType.QUANTITY if self.pending_order.is_option_selection_done() else StepType.OPTION

    def select_quantity(self, quantity: Quantity) -> None:
        if self.pending_order is None:
            raise ValueError("선택 중인 메뉴가 없습니다.")

        try:
            self.pending_order.set_quantity(quantity)
            self.order_service.add_to_cart(
                self.cart,
                self.pending_order.menu,
                self.pending_order.quantity,
                self.pending_order.selected_options,
            )
        except ValueError:
            self.pending_order = None
            self.go_to_menu()
            raise

        self.pending_order = None
        self.step = StepType.MENU

    def go_to_menu(self) -> None:
        self.step = StepType.MENU

    def go_to_cart(self) -> None:
        self.step = StepType.CART

    def go_to_payment(self) -> None:
        if len(self.cart) == 0:
            raise ValueError("장바구니가 비어있습니다.")

        self.step = StepType.PAYMENT

    def checkout(self) -> None:
        try:
            self.order_service.checkout(self.cart)
        except (OutOfStockError, InsufficientBalanceError):
            self.go_to_menu()
            raise

        self.step = StepType.COMPLETE

    def end(self) -> None:
        self.step = StepType.END