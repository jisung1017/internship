import pytest

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


def build_cli(monkeypatch, inputs: list[str], balance: int, bean_quantity: int) -> CLI:
    responses = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    menus = [build_americano()]
    inventory = build_inventory(bean_quantity)
    payment = Payment(balance=Money(balance))
    order_service = OrderService(payment, inventory)

    return CLI(menus, order_service, payment)


class TestSuccessfulCheckout:
    """
    Given: 잔액 10000원, 원두 재고 1000개
    When: 아메리카노(HOT, 샷추가 없음) 1잔을 담고 결제한다
    Then: 잔액이 3000원 차감되고, 원두 재고가 18개 줄어든다
    """

    def test_balance_and_inventory_decrease_correctly(self, monkeypatch):
        cli = build_cli(
            monkeypatch,
            inputs=["1", "HOT", "0", "1", "2", "0"],
            balance=10000,
            bean_quantity=1000,
        )

        cli.run()

        assert cli.payment.balance == Money(7000)
        assert cli.order_service.inventory.items[0].quantity == Quantity(982)
        assert len(cli.cart) == 0


class TestOptionConsumesInventory:
    """
    Given: 잔액 충분, 원두 재고 1000개
    When: 아메리카노(HOT, 샷추가 2개) 1잔을 담고 결제한다
    Then: 원두 재고가 메뉴 소비량(18) + 옵션 소비량(10*2=20) = 38개 줄어든다
    """

    def test_option_recipe_is_consumed_on_checkout(self, monkeypatch):
        cli = build_cli(
            monkeypatch,
            inputs=["1", "HOT", "2", "1", "2", "0"],
            balance=10000,
            bean_quantity=1000,
        )

        cli.run()

        assert cli.order_service.inventory.items[0].quantity == Quantity(962)
        assert cli.payment.balance == Money(10000 - 3000 - 500 * 2)


class TestInsufficientBalance:
    """
    Given: 잔액 100원 (부족), 원두 재고 충분
    When: 아메리카노를 담고 결제를 시도한다
    Then: 결제가 거부되고, 장바구니가 비워지며, 잔액은 그대로 유지된다
    """

    def test_cart_is_cleared_and_balance_untouched(self, monkeypatch, capsys):
        cli = build_cli(
            monkeypatch,
            inputs=["1", "HOT", "0", "1", "2", "0"],
            balance=100,
            bean_quantity=1000,
        )

        cli.run()

        captured = capsys.readouterr()
        assert "잔액이 부족합니다" in captured.out
        assert cli.payment.balance == Money(100)
        assert len(cli.cart) == 0


class TestOutOfStock:
    """
    Given: 잔액 충분, 원두 재고 5개 (아메리카노 1잔=18개 필요, 부족)
    When: 아메리카노를 담고 결제를 시도한다
    Then: 결제가 거부되고, 장바구니가 비워지며, 재고는 차감되지 않는다
    """

    def test_cart_is_cleared_and_inventory_untouched(self, monkeypatch, capsys):
        cli = build_cli(
            monkeypatch,
            inputs=["1", "HOT", "0", "1", "2", "0"],
            balance=10000,
            bean_quantity=5,
        )

        cli.run()

        captured = capsys.readouterr()
        assert "재고가 부족합니다" in captured.out
        assert cli.order_service.inventory.items[0].quantity == Quantity(5)
        assert len(cli.cart) == 0


class TestInvalidMenuAndOptionInput:
    """
    Given: 잔액/재고 충분
    When: 잘못된 메뉴 번호(9)와 잘못된 옵션 인덱스(COLD)를 먼저 입력한 뒤 올바르게 재입력한다
    Then: 재입력 유도 후 정상적으로 장바구니에 담기고 결제까지 성공한다
    """

    def test_retries_after_invalid_input_and_completes_order(self, monkeypatch):
        cli = build_cli(
            monkeypatch,
            inputs=["9", "1", "COLD", "HOT", "0", "1", "2", "0"],
            balance=10000,
            bean_quantity=1000,
        )

        cli.run()

        assert cli.payment.balance == Money(7000)
        assert len(cli.cart) == 0


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