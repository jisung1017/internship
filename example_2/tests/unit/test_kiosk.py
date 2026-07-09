import pytest

from example_2.interfaces.domain.option import Option
from example_2.services.kiosk import Kiosk
from example_2.services.kiosk_session import KioskSession, StepType


class TestKiosk:
    # 키오스크는 유저의 입력을 각 객체에 명령을 내리는 객체입니다.
    # 키오스크세션에 적절한 명령을 내리는지 확인해야합니다.
    # 1. 키오스크가 생성될 때 키오스크 세션이 있는지 확인
    # 2. 명령에 따라 step이 변하는지
    # 3. 메뉴와 옵션이 골라지는지
    #

    def test_kiosk_has_session_when_created(self):
        kiosk = Kiosk()

        assert isinstance(kiosk.session, KioskSession)
        assert kiosk.get_current_step() == StepType.LOADING

    @pytest.mark.parametrize(
        ("command", "expected_step"),
        [
            ("start_kiosk", StepType.MENU),
            ("go_to_menu", StepType.MENU),
            ("go_to_cart", StepType.CART),
            ("go_to_complete", StepType.COMPLETE),
        ],
    )
    def test_step_changes_by_command(self, command, expected_step):
        kiosk = Kiosk()

        getattr(kiosk, command)()

        assert kiosk.get_current_step() == expected_step

    def test_go_to_payment_changes_step_when_cart_has_item(self, test_menu):
        kiosk = Kiosk()
        kiosk.select_menu(test_menu)
        kiosk.add_selected_menu_to_cart()

        kiosk.go_to_payment()

        assert kiosk.get_current_step() == StepType.PAYMENT

    def test_go_to_payment_raises_error_when_cart_is_empty(self):
        kiosk = Kiosk()

        with pytest.raises(ValueError, match="장바구니가 비어 있어요."):
            kiosk.go_to_payment()

    def test_select_menu_changes_selected_menu_and_step(self, test_menu):
        kiosk = Kiosk()

        kiosk.select_menu(test_menu)

        assert kiosk.get_selected_menu() == test_menu
        assert kiosk.get_current_step() == StepType.OPTION

    def test_select_option_adds_option_to_selected_menu(self, test_menu):
        kiosk = Kiosk()
        option = Option(id=1, name="샷 추가", price=500, amount=1)

        kiosk.select_menu(test_menu)
        kiosk.select_option(option)
        kiosk.add_selected_menu_to_cart()

        cart = kiosk.get_cart()
        assert len(cart.items) == 1
        assert cart.items[0].menu == test_menu
        assert cart.items[0].options == [option]
        assert cart.total_cost() == test_menu.price + option.total_cost()
        assert kiosk.get_selected_menu() is None
        assert kiosk.get_current_step() == StepType.CART

    def test_select_option_raises_error_without_selected_menu(self):
        kiosk = Kiosk()
        option = Option(id=1, name="샷 추가", price=500, amount=1)

        with pytest.raises(ValueError, match="메뉴를 선택해야함"):
            kiosk.select_option(option)
