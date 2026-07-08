from src.domain.cart import Cart
from src.domain.exceptions import InsufficientBalanceError, OutOfStockError
from src.domain.menu import Menu
from src.domain.option import Option
from src.domain.payment import Payment
from src.domain.quantity import Quantity
from src.application.order_service import OrderService


def parse_menu_choice(raw_input: str, menu_count: int) -> int:
    value = int(raw_input)

    if not 0 <= value <= menu_count + 1:
        raise ValueError("잘못된 메뉴 번호입니다.")

    return value

def parse_option_selection(raw_input: str, options: list[Option]) -> list[Option]:
    raw_input = raw_input.strip()

    if not raw_input:
        return []

    try:
        return [options[int(option) - 1] for option in raw_input.split()]
    except (ValueError, IndexError):
        raise ValueError("잘못된 옵션 번호입니다.")

def parse_quantity(raw_input: str) -> Quantity:
    value = int(raw_input)

    if not 1 <= value <= 10:
        raise ValueError("수량은 1~10 사이여야 합니다.")

    return Quantity(value)


class CLI:
    def __init__(self, menus: list[Menu], order_service: OrderService, payment=Payment):
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

    def _input_options(self, menu: Menu, options: list[Option]) -> list[Option]:
        if not options:
            return []
        
        print(f"\n옵션 ({menu.name})")
        for i, option in enumerate(options, start=1):
            tab = "\t\t\t" if len(option.name) <= 5 else "\t\t" 
            print(f"{i}. {option.name}{tab}(+{option.additional_price.amount}원)")

        while True:
            try:
                return parse_option_selection(input(">> 옵션 선택: "), options)
            except ValueError:
                print("잘못된 입력입니다. 다시 입력해주세요.")

    def _input_quantity(self) -> Quantity:
        while True:
            try:
                return parse_quantity(input(">> 수량 선택 (1~10): "))
            except ValueError:
                print("잘못된 입력입니다. 다시 입력해주세요.")

    def _order_menu(self, menu: Menu) -> None:
        options = [option for group in menu.option_groups for option in group.options]
        selected_options = self._input_options(menu, options)
        quantity = self._input_quantity()

        try:
            self.order_service.add_to_cart(self.cart, menu, quantity, selected_options)
        except ValueError as e:
            print(f"잘못된 입력입니다. {e}")
            return

        print("장바구니에 상품이 담겼습니다.\n")

    def _checkout(self) -> None:
        if len(self.cart) == 0:
            print("장바구니가 비어있습니다.")
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

    

