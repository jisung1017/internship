from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from example_2.interfaces.domain.cart import Cart, CartItem
from example_2.interfaces.domain.menu import Menu
from example_2.interfaces.domain.option import Option


class StepType(Enum):
    LOADING = "loading"
    MENU = "menu"
    OPTION = "option"
    CART = "cart"
    PAYMENT = "payment"
    COMPLETE = "complete"


@dataclass
class KioskSession:
    cart: Cart = field(default_factory=Cart)
    selected_menu: Optional[Menu] = None
    selected_options: List[Option] = field(default_factory=list)
    step: StepType = StepType.LOADING

    def start(self):
        self.init_all()
        self.change_step(StepType.MENU)

    def init_all(self):
        self.cart.init()
        self.selected_menu = None
        self.selected_options = []
        self.step = StepType.LOADING

    def change_step(self, step: StepType):
        self.step = step

    def get_step(self):
        return self.step

    def get_cart(self):
        return self.cart

    def get_selected_menu(self):
        return self.selected_menu

    def select_menu(self, menu: Menu):
        self.selected_menu = menu
        self.selected_options = []
        self.change_step(StepType.OPTION)

    def is_selected_menu(self):
        return self.selected_menu is not None

    def select_option(self, option: Option):
        if not self.selected_menu:
            raise ValueError("메뉴를 선택해야함")
        self.selected_options.append(option)

    def add_to_cart(self):
        if self.selected_menu is None:
            raise ValueError("메뉴를 선택해야함")
        item = CartItem(
            menu=self.selected_menu,
            options=list(self.selected_options),
        )
        self.cart.add(item)
        self.selected_menu = None
        self.selected_options = []
        self.change_step(StepType.CART)

    def go_to_menu(self):
        self.change_step(StepType.MENU)

    def go_to_cart(self):
        self.change_step(StepType.CART)

    def go_to_payment(self):
        if self.cart.is_empty():
            raise ValueError("장바구니가 비어 있어요.")
        self.change_step(StepType.PAYMENT)

    def go_to_complete(self):
        self.change_step(StepType.COMPLETE)
