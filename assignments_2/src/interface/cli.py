import time

from src.domain.cart import Cart
from src.domain.exceptions import InsufficientBalanceError, OutOfStockError
from src.domain.menu import Menu
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.payment import Payment
from src.domain.quantity import Quantity
from src.application.order_service import OrderService


def parse_menu_choice(raw_input: str, menu_count: int) -> int:
    value = int(raw_input)

    if not 0 <= value <= menu_count + 1:
        raise ValueError("잘못된 메뉴 번호입니다.")

    return value

def parse_group_selection(raw: str, group: OptionGroup) -> list[Option]:
    raw = raw.strip()

    if len(group.options) == 1:
        try:
            count = int(raw) if raw else 0
        except ValueError:
            raise ValueError("숫자를 입력해주세요.")

        if count < 0:
            raise ValueError("수량은 0 이상이어야 합니다.")

        selected = [group.options[0]] * count
    else:
        selected = []
        for name in raw.split():
            matched = next((option for option in group.options if option.name.upper() == name.upper()), None)
            if matched is None:
                raise ValueError("HOT 또는 COLD 입력해주세요 (대소구분X)")
            selected.append(matched)

    if not group.min_quantity.value <= len(selected) <= group.max_quantity.value:
        raise ValueError(
            f"{group.name}은(는) {group.min_quantity.value}~{group.max_quantity.value}개 선택해야 합니다."
        )

    return selected

def parse_quantity(raw_input: str) -> Quantity:
    value = int(raw_input)

    if not 1 <= value <= 10:
        raise ValueError("수량은 1~10 사이여야 합니다.")

    return Quantity(value)


class CLI:
    def __init__(self, menus: list[Menu], order_service: OrderService, payment: Payment):
        self.menus = menus
        self.order_service = order_service
        self.payment = payment
        self.cart = Cart()
    
    def run(self) -> None:
        while True:
            self._show_menu()
            choice = self._input_menu_choice()

            if choice == 0:
                print("종료합니다.")
                break

            if choice == len(self.menus) + 1:
                self._checkout()
                continue
                
            self._order_menu(self.menus[choice-1])

    def _show_menu(self) -> None:
        time.sleep(0.7)
        print("=========== Cafe Mini Kiosk ===========\n")
        print("                [MENU]                 ")
        print("---------------------------------------")

        for i, menu in enumerate(self.menus, start=1):
            tab = "\t\t\t" if len(menu.name) <= 5 else "\t\t" 
            print(f"{i}. {menu.name}{tab}{menu.price.amount}원")

        print("---------------------------------------")
        print(f"{len(self.menus) + 1}. 결제\t\t\t(잔액: {self.payment.balance.amount}원)")
        print("0. 종료")

    def _input_menu_choice(self) -> int:
        while True:
            try:
                return parse_menu_choice(input(">> 메뉴 선택: "), len(self.menus))
            
            except ValueError:
                print("잘못된 입력입니다. 다시 입력해주세요.")

    def _input_options(self, menu: Menu) -> list[Option]:
        if not menu.option_groups:
            return []

        print(f"\n옵션({menu.name})")

        selected_options: list[Option] = []
        for i, group in enumerate(menu.option_groups, start=1):
            selected_options += self._input_group(i, group)

        return selected_options

    def _input_group(self, index: int, group: OptionGroup) -> list[Option]:
        if len(group.options) == 1:
            option = group.options[0]
            label = f"{option.name} (+{option.additional_price.amount}원)"
        else:
            label = "/".join(option.name for option in group.options)

        while True:
            try:
                return parse_group_selection(input(f"{index}. {label}: "), group)
            except ValueError as e:
                print(f"잘못된 입력입니다. {e}")

    def _input_quantity(self) -> Quantity:
        while True:
            try:
                return parse_quantity(input(">> 수량 선택 (1~10): "))
            except ValueError:
                print("잘못된 입력입니다. 다시 입력해주세요.")

    def _order_menu(self, menu: Menu) -> None:
        selected_options = self._input_options(menu)
        quantity = self._input_quantity()

        try:
            self.order_service.add_to_cart(self.cart, menu, quantity, selected_options)
        except ValueError as e:
            print(f"잘못된 입력입니다. {e}")
            return

        print("장바구니에 상품이 담겼습니다.\n")

    def _checkout(self) -> None:
        if len(self.cart) == 0:
            print("장바구니가 비어있습니다.\n")
            return

        print(f"총 금액: {self.cart.total_price().amount}원")

        try:
            self.order_service.checkout(self.cart)
        except OutOfStockError:
            print("재고가 부족합니다. 장바구니를 초기화 합니다.\n")
            return
        except InsufficientBalanceError:
            print("잔액이 부족합니다. 장바구니를 초기화 합니다.\n")
            return

        print(f"결제에 성공했습니다! 남은 잔액: {self.payment.balance.amount}원\n")