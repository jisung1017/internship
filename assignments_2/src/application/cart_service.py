from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.menu import Menu
from src.domain.option_item import OptionItem
from src.domain.quantity import Quantity


class CartService:
    def add_item(
        self,
        cart: Cart,
        menu: Menu,
        quantity: Quantity,
        selected_options: list[OptionItem],
    ) -> None:
        menu.validate_selected_options(selected_options)
        item = CartItem(menu=menu, quantity=quantity, selected_options=selected_options)
        cart.add_item(item)

    def add_item_by_ids(
        self,
        cart: Cart,
        available_menus: list[Menu],
        menu_name: str,
        quantity_val: int,
        selected_option_ids: list[int],
    ) -> None:
        """옵션 PK ID 목록으로 장바구니 항목을 추가합니다."""
        menu = next((m for m in available_menus if m.name == menu_name), None)
        if not menu:
            raise ValueError(f"존재하지 않는 메뉴입니다: {menu_name}")

        selected_options: list[OptionItem] = []
        for opt_id in selected_option_ids:
            matched = menu.find_option_item_by_id(opt_id)
            if not matched:
                raise ValueError(f"유효하지 않은 옵션 ID입니다: {opt_id}")
            selected_options.append(matched)

        self.add_item(
            cart=cart,
            menu=menu,
            quantity=Quantity(quantity_val),
            selected_options=selected_options,
        )

    def add_item_by_names(
        self,
        cart: Cart,
        available_menus: list[Menu],
        menu_name: str,
        quantity_val: int,
        selected_option_names: list[str],
    ) -> None:
        """옵션 이름 목록으로 장바구니 항목을 추가합니다 (CLI 지원용)."""
        menu = next((m for m in available_menus if m.name == menu_name), None)
        if not menu:
            raise ValueError(f"존재하지 않는 메뉴입니다: {menu_name}")

        selected_options: list[OptionItem] = []
        for opt_name in selected_option_names:
            matched = menu.find_option_by_name(opt_name)
            if not matched:
                raise ValueError(f"유효하지 않은 옵션입니다: {opt_name}")
            selected_options.append(matched)

        self.add_item(
            cart=cart,
            menu=menu,
            quantity=Quantity(quantity_val),
            selected_options=selected_options,
        )

    def clear_cart(self, cart: Cart) -> None:
        cart.clear()