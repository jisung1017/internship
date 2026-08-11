from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.order import Order
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem
from src.infrastructure.models import Base, OrderModel
from src.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def setup_in_memory_uow():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    return SqlAlchemyUnitOfWork(session_factory=session_factory)


def test_sqlalchemy_uow_commit():
    uow = setup_in_memory_uow()

    ingredient = Ingredient("원두", "g")
    recipe = Recipe(items=[RecipeItem(ingredient, Quantity(18))])
    menu = Menu(name="아메리카노", price=Money(3000), recipe=recipe, option_groups=[])

    cart = Cart()
    cart.add_item(CartItem(menu=menu, quantity=Quantity(1)))
    order = Order.from_cart(cart)

    with uow:
        uow.orders.save(order)
        uow.commit()

    session = uow.session_factory()
    saved_orders = session.query(OrderModel).all()
    assert len(saved_orders) == 1
    assert saved_orders[0].total_price == 3000
    session.close()


def test_sqlalchemy_uow_rollback_on_exception():
    uow = setup_in_memory_uow()

    ingredient = Ingredient("원두", "g")
    recipe = Recipe(items=[RecipeItem(ingredient, Quantity(18))])
    menu = Menu(name="아메리카노", price=Money(3000), recipe=recipe, option_groups=[])

    cart = Cart()
    cart.add_item(CartItem(menu=menu, quantity=Quantity(1)))
    order = Order.from_cart(cart)

    try:
        with uow:
            uow.orders.save(order)
            raise RuntimeError("Intentional error for rollback")
    except RuntimeError:
        pass

    session = uow.session_factory()
    saved_orders = session.query(OrderModel).all()
    assert len(saved_orders) == 0
    session.close()