from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.menu import Menu
from src.domain.option import Option
from src.domain.quantity import Quantity


class CartService:
    def add_item(
        self,
        cart: Cart,
        menu: Menu,
        quantity: Quantity,
        selected_options: list[Option],
    ) -> None:
        menu.validate_selected_options(selected_options)
        item = CartItem(menu=menu, quantity=quantity, selected_options=selected_options)
        cart.add_item(item)

    def add_item_by_names(
        self,
        cart: Cart,
        available_menus: list[Menu],
        menu_name: str,
        quantity_val: int,
        selected_option_names: list[str],
    ) -> None:
        # 1. 메뉴 찾기
        menu = next((m for m in available_menus if m.name == menu_name), None)
        if not menu:
            raise ValueError(f"존재하지 않는 메뉴입니다: {menu_name}")

        # 2. 옵션 도메인 객체 매핑 (Menu 도메인에 탐색 위임)
        selected_options: list[Option] = []
        for opt_name in selected_option_names:
            matched = menu.find_option_by_name(opt_name)
            if not matched:
                raise ValueError(f"존재하지 않는 옵션입니다: {opt_name}")
            selected_options.append(matched)

        # 3. 도메인 메서드 호출 및 장바구니 추가
        self.add_item(
            cart=cart,
            menu=menu,
            quantity=Quantity(quantity_val),
            selected_options=selected_options,
        )

    def clear_cart(self, cart: Cart) -> None:
        cart.clear()