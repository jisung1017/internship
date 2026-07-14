import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from example_2.services.kiosk_session import StepType
from example_2.interfaces.domain.inventory import Inventory
from example_2.interfaces.domain.menu import Menu
from example_2.interfaces.domain.option import Option
from example_2.interfaces.domain.recipe import Ingredient, Recipe, RecipeIngredient
from example_2.services.kiosk import Kiosk
from example_2.services.inventory import InventoryService
from example_2.services.order import OrderService
from example_2.services.payment import PaymentService


MENUS = [
    Menu(id=1, name="아메리카노", price=3000, description="고소한 기본 커피"),
    Menu(id=2, name="카페라떼", price=4000, description="우유가 들어간 부드러운 커피"),
    Menu(id=3, name="바닐라라떼", price=4500, description="바닐라 시럽이 들어간 라떼"),
]

OPTIONS = [
    Option(id=1, name="샷 추가", price=500, amount=1),
    Option(id=2, name="시럽 추가", price=300, amount=1),
    Option(id=3, name="얼음 적게", price=0, amount=1),
]

COFFEE_BEAN = Ingredient(id=1, name="원두", unit="g")
MILK = Ingredient(id=2, name="우유", unit="ml")
VANILLA_SYRUP = Ingredient(id=3, name="바닐라 시럽", unit="ml")

RECIPES = [
    Recipe(
        id=1,
        menu_id=1,
        name="아메리카노 레시피",
        ingredients=[RecipeIngredient(ingredient=COFFEE_BEAN, amount=18)],
    ),
    Recipe(
        id=2,
        menu_id=2,
        name="카페라떼 레시피",
        ingredients=[
            RecipeIngredient(ingredient=COFFEE_BEAN, amount=18),
            RecipeIngredient(ingredient=MILK, amount=180),
        ],
    ),
    Recipe(
        id=3,
        menu_id=3,
        name="바닐라라떼 레시피",
        ingredients=[
            RecipeIngredient(ingredient=COFFEE_BEAN, amount=18),
            RecipeIngredient(ingredient=MILK, amount=180),
            RecipeIngredient(ingredient=VANILLA_SYRUP, amount=20),
        ],
    ),
]

INVENTORIES = [
    Inventory(id=1, ingredient_id=COFFEE_BEAN.id, amount=500),
    Inventory(id=2, ingredient_id=MILK.id, amount=3000),
    Inventory(id=3, ingredient_id=VANILLA_SYRUP.id, amount=300),
]


def read_number(message: str, min_value: int, max_value: int):
    while True:
        raw_value = input(message).strip()
        if raw_value.isdigit():
            value = int(raw_value)
            if min_value <= value <= max_value:
                return value
        print(f"{min_value}부터 {max_value} 사이의 숫자를 입력해주세요.")


def read_option_ids():
    raw_value = input("추가할 옵션 번호를 쉼표로 입력하세요. 없으면 엔터: ").strip()
    if raw_value == "":
        return []

    option_ids = []
    for value in raw_value.split(","):
        value = value.strip()
        if value.isdigit():
            option_ids.append(int(value))
    return option_ids


def show_menu_screen(kiosk: Kiosk):
    print("\n[메뉴 선택]")
    for index, menu in enumerate(MENUS, start=1):
        print(f"{index}. {menu.name} - {menu.price}원 / {menu.description}")
    print("0. 장바구니 보기")

    selected_index = read_number("선택: ", 0, len(MENUS))
    if selected_index == 0:
        kiosk.go_to_cart()
        return

    kiosk.select_menu(MENUS[selected_index - 1])


def show_option_screen(kiosk: Kiosk):
    selected_menu = kiosk.get_selected_menu()
    print(f"\n[옵션 선택] {selected_menu.name}")
    for option in OPTIONS:
        print(f"{option.id}. {option.name} - {option.total_cost()}원")

    selected_option_ids = read_option_ids()
    for option in OPTIONS:
        if option.id in selected_option_ids:
            kiosk.select_option(option)

    kiosk.add_selected_menu_to_cart()


def show_cart_screen(kiosk: Kiosk):
    cart = kiosk.get_cart()
    print("\n[장바구니]")
    if cart.is_empty():
        print("장바구니가 비어 있습니다.")
    else:
        for index, item in enumerate(cart.items, start=1):
            option_names = (
                ", ".join(option.name for option in item.options) or "옵션 없음"
            )
            print(f"{index}. {item.menu.name} ({option_names}) - {item.total_cost()}원")
        print(f"총 금액: {cart.total_cost()}원")

    print("1. 메뉴 더 담기")
    print("2. 결제하기")
    selected_index = read_number("선택: ", 1, 2)

    if selected_index == 1:
        kiosk.go_to_menu()
        return

    try:
        kiosk.go_to_payment()
    except ValueError as error:
        print(error)
        kiosk.go_to_menu()


def show_payment_screen(kiosk: Kiosk, order_service: OrderService):
    print("\n[결제]")
    print(f"결제 금액: {kiosk.get_cart().total_cost()}원")
    print("1. 결제 승인")
    print("2. 장바구니로 돌아가기")
    selected_index = read_number("선택: ", 1, 2)

    if selected_index == 1:
        try:
            order_service.checkout(kiosk.get_cart(), RECIPES, INVENTORIES)
            kiosk.go_to_complete()
        except ValueError as error:
            print(error)
            kiosk.go_to_cart()
        return

    kiosk.go_to_cart()


def show_complete_screen(kiosk: Kiosk):
    print("\n[주문 완료]")
    print(f"주문이 접수되었습니다. 결제 금액: {kiosk.get_cart().total_cost()}원")


SCREEN_HANDLERS = {
    StepType.MENU: show_menu_screen,
    StepType.OPTION: show_option_screen,
    StepType.CART: show_cart_screen,
    StepType.PAYMENT: show_payment_screen,
}


def main():
    kiosk = Kiosk()
    order_service = OrderService(
        inventory_service=InventoryService(),
        payment_service=PaymentService(),
    )
    kiosk.start_kiosk()

    while kiosk.get_current_step() != StepType.COMPLETE:
        current_step = kiosk.get_current_step()
        screen_handler = SCREEN_HANDLERS[current_step]
        if current_step == StepType.PAYMENT:
            screen_handler(kiosk, order_service)
        else:
            screen_handler(kiosk)

    show_complete_screen(kiosk)


if __name__ == "__main__":
    main()
