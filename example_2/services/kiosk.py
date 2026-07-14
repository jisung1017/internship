from dataclasses import dataclass, field

from example_2.services.kiosk_session import KioskSession
from example_2.interfaces.domain.menu import Menu
from example_2.interfaces.domain.option import Option


@dataclass
class Kiosk:
    session: KioskSession = field(default_factory=KioskSession)

    def _get_session(self):
        if self.session is None:
            raise RuntimeError("키오스크가 시작되지 않았어요.")
        return self.session

    def start_kiosk(self):
        self._get_session().start()
        # 필요한 정보 로드 ex) 메뉴, 재료 등

    def get_current_step(self):
        return self._get_session().get_step()

    def get_cart(self):
        return self._get_session().get_cart()

    def get_selected_menu(self):
        return self._get_session().get_selected_menu()

    def select_menu(self, menu: Menu):
        self._get_session().select_menu(menu)

    def select_option(self, option: Option):
        self._get_session().select_option(option)

    def add_selected_menu_to_cart(self):
        self._get_session().add_to_cart()

    def go_to_menu(self):
        self._get_session().go_to_menu()

    def go_to_cart(self):
        self._get_session().go_to_cart()

    def go_to_payment(self):
        self._get_session().go_to_payment()

    def go_to_complete(self):
        self._get_session().go_to_complete()
