
from src.domain.menu import Menu
from src.domain.cart import Cart

class CLI:
    def show_menu(self, menus: list[Menu]) -> None:
        print("===== Cafe Mini Kiosk =====\n")
        print("          [MENU]           ")

        for i, menu in enumerate(menus, start=1):
            print(f"{i}. {menu.name} ({menu.price.amount}원)")
        print(f"{len(self.menu) + 1}. 결제")
        print("0. 종료")

    def input_menu(self) -> int:
        while True:
            try:
                menu = int(input("메뉴 선택: "))

                if 0 <= menu < len(self.menu) + 1:
                    return menu
                
                print("잘못된 입력입니다. 다시 입력해주세요.")
            
            except ValueError:
                print("숫자를 입력해주세요.")
    
    def input_quantity(self) -> int:
        return int(input("수량: "))
    
    def run(self):
        cart = Cart()

        while True:
            self.show_menu(cart)

            menu = self.input_menu()
            if menu == 0:
                print("종료합니다.")
                break

            if menu == len(self.menu) + 1:
                self.checkout(cart)
                continue
            
            quantity = self.input_quantity()

