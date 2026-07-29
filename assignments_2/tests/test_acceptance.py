import pytest

from src.application.kiosk_session import KioskSession
from src.application.order_service import OrderService
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.payment import Payment
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem
from src.interface.cli import CLI
from src.application.checkout_service import CheckoutService
from src.application.kiosk_admin_service import KioskAdminService


def build_americano() -> Menu:
    bean = Ingredient("원두")

    temperature_group = OptionGroup(
        name="온도",
        min_quantity=Quantity(1),
        max_quantity=Quantity(1),
        options=[
            Option(name="HOT", additional_price=Money(0)),
            Option(name="ICE", additional_price=Money(0)),
        ],
    )

    shot_group = OptionGroup(
        name="샷추가",
        min_quantity=Quantity(0),
        max_quantity=Quantity(4),
        selection_mode="count",
        options=[
            Option(
                name="샷추가",
                additional_price=Money(500),
                recipe=Recipe(items=[RecipeItem(bean, Quantity(10))]),
            )
        ],
    )

    return Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=Recipe(items=[RecipeItem(bean, Quantity(18))]),
        option_groups=[temperature_group, shot_group],
    )


def build_inventory(bean_quantity: int) -> Inventory:
    return Inventory(items=[InventoryItem(Ingredient("원두"), Quantity(bean_quantity))])


def get_quantity(inventory: Inventory, ingredient: Ingredient) -> Quantity:
    for item in inventory.items:
        if item.ingredient == ingredient:
            return item.quantity

    raise AssertionError(f"{ingredient.name} 재고를 찾을 수 없습니다.")


def build_cli(monkeypatch, inputs: list[str], balance: int, bean_quantity: int) -> CLI:
    responses = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    menus = [build_americano()]
    inventory = build_inventory(bean_quantity)
    payment = Payment(balance=Money(balance))
    order_service = OrderService(payment, inventory)
    checkout_service = CheckoutService(order_service)
    admin_service = KioskAdminService(order_service)
    session = KioskSession(
        menus=menus,
        order_service=order_service,
        checkout_service=checkout_service,
    )

    return CLI(session, admin_service)


class TestSuccessfulCheckout:
    """
    Given: 잔액 10000원, 원두 재고 1000개
    When: 아메리카노(HOT, 샷추가 없음) 1잔을 담고 결제한다
    Then: 잔액이 3000원 차감되고, 원두 재고가 18개 줄어든다
    """

    def test_balance_and_inventory_decrease_correctly(self, monkeypatch):
        cli = build_cli(
            monkeypatch,
            inputs=["1", "HOT", "0", "1", "2", "2", "1", "0"],
            balance=10000,
            bean_quantity=1000,
        )

        cli.run()

        assert cli.session.get_balance() == Money(7000)
        assert get_quantity(cli.session.order_service.inventory, Ingredient("원두")) == Quantity(982)
        assert len(cli.session.cart) == 0


class TestOptionConsumesInventory:
    """
    Given: 잔액 충분, 원두 재고 1000개
    When: 아메리카노(HOT, 샷추가 2개) 1잔을 담고 결제한다
    Then: 원두 재고가 메뉴 소비량(18) + 옵션 소비량(10*2=20) = 38개 줄어든다
    """

    def test_option_recipe_is_consumed_on_checkout(self, monkeypatch):
        cli = build_cli(
            monkeypatch,
            inputs=["1", "HOT", "2", "1", "2", "2", "1", "0"],
            balance=10000,
            bean_quantity=1000,
        )

        cli.run()

        assert get_quantity(cli.session.order_service.inventory, Ingredient("원두")) == Quantity(962)
        assert cli.session.get_balance() == Money(10000 - 3000 - 500 * 2)


class TestInsufficientBalance:
    """
    Given: 잔액 100원 (부족), 원두 재고 충분
    When: 아메리카노를 담고 결제를 시도한다
    Then: 결제가 거부되고, 장바구니가 비워지며, 잔액은 그대로 유지된다
    """

    def test_cart_is_cleared_and_balance_untouched(self, monkeypatch, capsys):
        cli = build_cli(
            monkeypatch,
            inputs=["1", "HOT", "0", "1", "2", "2", "1", "0"],
            balance=100,
            bean_quantity=1000,
        )

        cli.run()

        captured = capsys.readouterr()
        assert "잔액이 부족합니다" in captured.out
        assert cli.session.get_balance() == Money(100)
        assert len(cli.session.cart) == 0


class TestOutOfStock:
    """
    Given: 잔액 충분, 원두 재고 5개 (아메리카노 1잔=18개 필요, 부족)
    When: 아메리카노를 담고 결제를 시도한다
    Then: 결제가 거부되고, 장바구니가 비워지며, 재고는 차감되지 않는다
    """

    def test_cart_is_cleared_and_inventory_untouched(self, monkeypatch, capsys):
        cli = build_cli(
            monkeypatch,
            inputs=["1", "HOT", "0", "1", "2", "2", "1", "0"],
            balance=10000,
            bean_quantity=5,
        )

        cli.run()

        captured = capsys.readouterr()
        assert "재고가 부족합니다" in captured.out
        assert get_quantity(cli.session.order_service.inventory, Ingredient("원두")) == Quantity(5)
        assert len(cli.session.cart) == 0


class TestInvalidMenuAndOptionInput:
    """
    Given: 잔액/재고 충분
    When: 잘못된 메뉴 번호(9)와 잘못된 옵션 입력(COLD)을 먼저 입력한 뒤 올바르게 재입력한다
    Then: 재입력 유도 후 정상적으로 장바구니에 담기고 결제까지 성공한다
    """

    def test_retries_after_invalid_input_and_completes_order(self, monkeypatch):
        cli = build_cli(
            monkeypatch,
            inputs=["9", "1", "COLD", "HOT", "0", "1", "2", "2", "1", "0"],
            balance=10000,
            bean_quantity=1000,
        )

        cli.run()

        assert cli.session.get_balance() == Money(7000)
        assert len(cli.session.cart) == 0


class TestOptionValidationDefenseInDepth:
    """
    CLI 입력 흐름에서는 그룹별로 즉시 검증되어 잘못된 조합이 만들어질 수 없지만,
    OrderService.add_to_cart 자체도 독립적으로 옵션 조합을 거부해야 한다 (방어적 설계 검증).
    """

    def test_add_to_cart_rejects_option_missing_required_group(self):
        menu = build_americano()
        inventory = build_inventory(1000)
        payment = Payment(balance=Money(10000))
        service = OrderService(payment, inventory)

        from src.domain.cart import Cart
        cart = Cart()

        with pytest.raises(ValueError):
            service.add_to_cart(cart, menu, Quantity(1), [])

        assert len(cart) == 0


class TestDevelopmentModeValidation:
    """
    개발자 모드: 메뉴 화면에서 '77'를 입력하면 진입하며,
    재고 입고(restock)와 이력 기록을 담당한다.
    """

    def test_restock_increases_inventory_and_records_history(self, monkeypatch):
        """
        Given: 원두 재고 1000개
        When: 개발자 모드에 진입해 원두 100개를 입고하고 종료한다
        Then: 원두 재고가 1100개로 증가하고, 입고 이력이 남는다
        """
        cli = build_cli(
            monkeypatch,
            inputs=["77", "1", "원두", "100", "0", "0"],
            balance=10000,
            bean_quantity=1000,
        )

        cli.run()

        inventory = cli.admin_service.get_inventory()
        assert inventory.get_quantity(Ingredient("원두")) == Quantity(1100)
        assert len(inventory.history) == 1
        assert inventory.history[0].change == 100
        assert inventory.history[0].reason == "RESTOCK"

    def test_restock_unregistered_ingredient_shows_error_and_does_not_change_state(self, monkeypatch, capsys):
        """
        Given: 원두만 등록된 재고
        When: 개발자 모드에서 등록되지 않은 '우유'를 입고 시도한다
        Then: 에러 메시지가 출력되고, 재고와 이력은 변하지 않는다
        """
        cli = build_cli(
            monkeypatch,
            inputs=["77", "1", "우유", "50", "0", "0"],
            balance=10000,
            bean_quantity=1000,
        )

        cli.run()

        captured = capsys.readouterr()
        assert "등록되지 않은 재료" in captured.out

        inventory = cli.admin_service.get_inventory()
        assert inventory.get_quantity(Ingredient("원두")) == Quantity(1000)
        assert len(inventory.history) == 0

    def test_multiple_restocks_accumulate_history_in_order(self, monkeypatch):
        """
        Given: 원두 재고 1000개
        When: 개발자 모드에서 원두를 두 번(50개, 30개) 입고한다
        Then: 재고는 두 번 모두 반영되고, 이력이 입고 순서대로 2건 쌓인다
        """
        cli = build_cli(
            monkeypatch,
            inputs=["77", "1", "원두", "50", "1", "원두", "30", "0", "0"],
            balance=10000,
            bean_quantity=1000,
        )

        cli.run()

        inventory = cli.admin_service.get_inventory()
        assert inventory.get_quantity(Ingredient("원두")) == Quantity(1080)
        assert [h.change for h in inventory.history] == [50, 30]