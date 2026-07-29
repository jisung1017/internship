from enum import Enum, auto
import time

from src.application.cart_service import CartService
from src.application.kiosk_admin_service import KioskAdminService
from src.application.order_application_service import OrderApplicationService
from src.application.pending_order import PendingOrder
from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.exceptions import InsufficientBalanceError, OutOfStockError
from src.domain.inventory import Inventory
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.payment import Payment
from src.domain.quantity import Quantity


class StepType(Enum):
    """CLI 화면 흐름 관리를 위한 전용 상태 Enum입니다."""
    MENU = auto()
    OPTION = auto()
    QUANTITY = auto()
    CART = auto()
    PAYMENT = auto()
    COMPLETE = auto()
    END = auto()


def parse_menu_choice(raw_input: str, menu_count: int) -> int:
    value = int(raw_input)

    if not 0 <= value <= menu_count + 1:
        raise ValueError("잘못된 메뉴 번호입니다.")

    return value


def parse_quantity(raw_input: str) -> Quantity:
    value = int(raw_input)

    if not 1 <= value <= 10:
        raise ValueError("수량은 1~10 사이여야 합니다.")

    return Quantity(value)


class CLI:
    def __init__(
        self,
        menus: list[Menu],
        payment: Payment,
        inventory: Inventory,
        cart_service: CartService,
        order_app_service: OrderApplicationService,
        admin_service: KioskAdminService,
    ):
        self.menus = menus
        self.payment = payment
        self.inventory = inventory
        self.cart_service = cart_service
        self.order_app_service = order_app_service
        self.admin_service = admin_service

        # CLI 어댑터 내부에서 관리하는 UI 전이 상태
        self.cart = Cart()
        self.step = StepType.MENU
        self.pending_order: PendingOrder | None = None

        self.handlers = {
            StepType.MENU: self._show_menu_screen,
            StepType.OPTION: self._show_option_screen,
            StepType.QUANTITY: self._show_quantity_screen,
            StepType.CART: self._show_cart_screen,
            StepType.PAYMENT: self._show_payment_screen,
            StepType.COMPLETE: self._show_complete_screen,
        }

    def run(self) -> None:
        while self.step != StepType.END:
            self.handlers[self.step]()

        print("종료합니다.")

    # ---------- MENU ----------

    def _show_menu_screen(self) -> None:
        time.sleep(0.7)
        self._print_menu(self.menus)

        choice = self._input_menu_choice(len(self.menus))

        if choice is None:  # 개발자 모드 진입시
            return

        if choice == 0:
            self.step = StepType.END
            return

        if choice == len(self.menus) + 1:
            self.step = StepType.CART
            return

        menu = self.menus[choice - 1]
        self.pending_order = PendingOrder(menu=menu)
        self.step = StepType.OPTION if menu.option_groups else StepType.QUANTITY

    def _print_menu(self, menus: list[Menu]) -> None:
        print("=========== Cafe Mini Kiosk ===========\n")
        print("                [MENU]                 ")
        print("---------------------------------------")

        for i, menu in enumerate(menus, start=1):
            tab = "\t\t\t" if len(menu.name) <= 5 else "\t\t"
            print(f"{i}. {menu.name}{tab}{menu.price.amount}원")

        print("---------------------------------------")
        print(f"{len(menus) + 1}. 장바구니\t\t(잔액: {self.payment.balance.amount}원)")
        print("0. 종료")

    def _input_menu_choice(self, menu_count: int) -> int | None:
        while True:
            raw = input(">> 메뉴 선택: ")

            if raw == "77":
                self._run_developer_mode()
                return None

            try:
                return parse_menu_choice(raw, menu_count)
            except ValueError:
                print("잘못된 입력입니다. 다시 입력해주세요.")

    # ---------- 개발자 모드 ----------

    def _run_developer_mode(self) -> None:
        print("\n=========== [개발자 모드] ===========")

        while True:
            self._print_inventory_status()
            print("\n1. 재고 추가")
            print("2. 판매 내역")
            print("0. 종료")
            raw = input(">> 선택: ")

            if raw == "0":
                print("개발자 모드를 종료합니다.\n")
                return

            if raw == "2":
                self._print_today_sales()
                continue

            if raw == "1":
                raw_ingredient = input(">> 입고할 재료명 입력: ")
                quantity = self._input_restock_quantity()

                try:
                    self.admin_service.restock(raw_ingredient, quantity)
                except (ValueError, OutOfStockError):
                    print("등록되지 않은 재료이거나 잘못된 입력입니다.\n")
                    continue

                print(f"{raw_ingredient.strip()} {quantity.value}개 입고 완료.\n")

    def _print_today_sales(self) -> None:
        records = self.admin_service.get_today_orders()

        print("\n[오늘 판매 내역]")
        if not records:
            print("  (오늘 판매 내역이 없습니다)")

        for record in records:
            items_text = ", ".join(
                f"{item.menu_name} x{item.quantity}" for item in record.items
            )
            print(
                f"  #{record.id} {record.created_at:%H:%M:%S} "
                f"{items_text} = {record.total_price.amount}원"
            )

        print(f"\n총 매출: {self.admin_service.get_today_sales_total().amount}원\n")

    def _print_inventory_status(self) -> None:
        inventory = self.admin_service.get_inventory()

        print("\n[재고 현황]")
        for item in inventory.items:
            print(f"- {item.ingredient.name}: {item.quantity.value}{item.ingredient.unit}")

        print("\n[최근 이력]")
        for record in inventory.history[-5:]:
            sign = "+" if record.change > 0 else ""
            print(f"  {record.timestamp:%H:%M:%S} {record.ingredient.name} {sign}{record.change} ({record.reason})")

    def _input_restock_quantity(self) -> Quantity:
        while True:
            raw = input(">> 입고 수량: ")
            try:
                return Quantity(int(raw))
            except ValueError:
                print("잘못된 입력입니다. 다시 입력해주세요.")

    # ---------- OPTION ----------

    def _show_option_screen(self) -> None:
        if self.pending_order is None:
            self.step = StepType.MENU
            return

        menu = self.pending_order.menu
        group = self.pending_order.current_option_group()

        if group is None:
            self.step = StepType.QUANTITY
            return

        group_index = self.pending_order.group_index
        self._print_option_header(menu, group_index)
        raw = input(f"{self._group_label(group, group_index)}: ")
        self._handle_option_input(group, raw)

    def _print_option_header(self, menu: Menu, group_index: int) -> None:
        if group_index != 0:
            return
        print(f"\n옵션({menu.name})")

    def _group_label(self, group: OptionGroup, group_index: int) -> str:
        index = group_index + 1

        if len(group.options) == 1:
            option = group.options[0]
            return f"{index}. {option.name} (+{option.additional_price.amount}원)"

        names = "/".join(option.name for option in group.options)
        return f"{index}. {names}"

    def _handle_option_input(self, group: OptionGroup, raw: str) -> None:
        if self.pending_order is None:
            return

        try:
            selected = group.parse_selection(raw)
        except ValueError as e:
            print(f"잘못된 입력입니다. {e}")
            return

        self.pending_order.select_current_option_group(selected)
        self.step = StepType.QUANTITY if self.pending_order.is_option_selection_done() else StepType.OPTION

    # ---------- QUANTITY ----------

    def _show_quantity_screen(self) -> None:
        raw = input(">> 수량 선택 (1~10): ")

        try:
            quantity = parse_quantity(raw)
        except ValueError:
            print("잘못된 입력입니다. 다시 입력해주세요.")
            return

        if self.pending_order is None:
            self.step = StepType.MENU
            return

        try:
            self.pending_order.set_quantity(quantity)
            self.cart_service.add_item(
                self.cart,
                self.pending_order.menu,
                self.pending_order.quantity,
                self.pending_order.selected_options,
            )
        except ValueError as e:
            print(f"잘못된 입력입니다. {e}")
            self.pending_order = None
            self.step = StepType.MENU
            return

        self.pending_order = None
        self.step = StepType.MENU
        print("장바구니에 상품이 담겼습니다.\n")

    # ---------- CART ----------

    def _show_cart_screen(self) -> None:
        if len(self.cart) == 0:
            print("장바구니가 비어있습니다.\n")
            self.step = StepType.MENU
            return

        self._print_cart(self.cart)
        choice = self._input_binary_choice()

        if choice == 1:
            self.step = StepType.MENU
            return

        self.step = StepType.PAYMENT

    def _print_cart(self, cart: Cart) -> None:
        print("\n[장바구니]")
        for item in cart.items:
            print(self._format_cart_item(item))

        print(f"\n총 금액: {cart.total_price().amount}원")
        print("1. 메뉴 더 담기")
        print("2. 결제하기")

    def _format_cart_item(self, item: CartItem) -> str:
        options_text = self._format_options(item.selected_options)
        options_suffix = f" ({options_text})" if options_text else ""

        return f"- {item.menu.name}{options_suffix}x{item.quantity.value} : {item.total_price().amount}원"

    def _format_options(self, options: list[Option]) -> str:
        counts: dict[str, int] = {}
        order: list[str] = []

        for option in options:
            if option.name not in counts:
                order.append(option.name)
            counts[option.name] = counts.get(option.name, 0) + 1

        return ", ".join(self._format_option_count(name, counts[name]) for name in order)

    def _format_option_count(self, name: str, count: int) -> str:
        if count == 1:
            return name
        return f"{name} x{count}"

    def _input_binary_choice(self) -> int:
        while True:
            raw = input(">> 선택: ")
            if raw in ("1", "2"):
                return int(raw)
            print("잘못된 입력입니다. 다시 입력해주세요.")

    # ---------- PAYMENT ----------

    def _show_payment_screen(self) -> None:
        print(f"\n총 금액: {self.cart.total_price().amount}원")
        print("1. 결제 승인")
        print("2. 취소")

        choice = self._input_binary_choice()

        if choice == 2:
            self.step = StepType.CART
            return

        self._checkout()

    def _checkout(self) -> None:
        try:
            self.order_app_service.place_order(self.cart, self.payment, self.inventory)
        except OutOfStockError:
            print("재고가 부족합니다. 장바구니를 초기화 합니다.\n")
            self.step = StepType.MENU
            return
        except InsufficientBalanceError:
            print("잔액이 부족합니다. 장바구니를 초기화 합니다.\n")
            self.step = StepType.MENU
            return

        self.step = StepType.COMPLETE

    # ---------- COMPLETE ----------

    def _show_complete_screen(self) -> None:
        print(f"결제에 성공했습니다! 남은 잔액: {self.payment.balance.amount}원\n")
        self.step = StepType.MENU