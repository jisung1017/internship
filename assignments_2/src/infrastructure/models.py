import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, Text, Uuid, UniqueConstraint, ARRAY, JSON
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import BigInteger

Base = declarative_base()


class IngredientModel(Base):
    __tablename__ = "ingredient"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)
    unit = Column(Text, nullable=False, default="")


class MenuModel(Base):
    __tablename__ = "menu"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)
    price = Column(BigInteger, nullable=False)
    category = Column(Text, nullable=False, default='COFFEE')
    tags = Column(
        ARRAY(Text).with_variant(JSON, "sqlite"),
        nullable=False,
        default=list,
    )
    is_sold_out = Column(Boolean, nullable=False, default=False)

    recipes = relationship(
        "RecipeItemModel", back_populates="menu", cascade="all, delete-orphan"
    )
    option_groups = relationship(
        "OptionGroupModel",
        back_populates="menu",
        cascade="all, delete-orphan",
        order_by="OptionGroupModel.id",
    )


class RecipeItemModel(Base):
    __tablename__ = "recipe_item"

    menu_id = Column(
        BigInteger, ForeignKey("menu.id", ondelete="CASCADE"), primary_key=True
    )
    ingredient_id = Column(
        BigInteger, ForeignKey("ingredient.id", ondelete="RESTRICT"), primary_key=True
    )
    quantity = Column(BigInteger, nullable=False)

    menu = relationship("MenuModel", back_populates="recipes")
    ingredient = relationship("IngredientModel")


class OptionModel(Base):
    __tablename__ = "option_master"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    default_min_select = Column(BigInteger, nullable=False, default=0)
    default_max_select = Column(BigInteger, nullable=False, default=1)
    selection_mode = Column(Text, nullable=False, default="choice")
    default_option_name = Column(Text, nullable=True)

    items = relationship(
        "OptionItemModel",
        back_populates="option",
        cascade="all, delete-orphan",
        order_by="OptionItemModel.id",
    )


class OptionItemModel(Base):
    __tablename__ = "option_item"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    option_id = Column(
        BigInteger, ForeignKey("option_master.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(Text, nullable=False)
    additional_price = Column(BigInteger, nullable=False, default=0)

    option = relationship("OptionModel", back_populates="items")
    recipes = relationship(
        "OptionRecipeItemModel",
        back_populates="option_item",
        cascade="all, delete-orphan",
    )


class OptionRecipeItemModel(Base):
    __tablename__ = "option_recipe_item"

    option_item_id = Column(
        BigInteger, ForeignKey("option_item.id", ondelete="CASCADE"), primary_key=True
    )
    ingredient_id = Column(
        BigInteger, ForeignKey("ingredient.id", ondelete="RESTRICT"), primary_key=True
    )
    quantity = Column(BigInteger, nullable=False)

    option_item = relationship("OptionItemModel", back_populates="recipes")
    ingredient = relationship("IngredientModel")


class OptionGroupModel(Base):
    __tablename__ = "option_group"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    menu_id = Column(
        BigInteger, ForeignKey("menu.id", ondelete="CASCADE"), nullable=False
    )
    option_id = Column(
        BigInteger, ForeignKey("option_master.id", ondelete="RESTRICT"), nullable=False
    )

    override_min_select = Column(BigInteger, nullable=True)
    override_max_select = Column(BigInteger, nullable=True)
    override_default_option_name = Column(Text, nullable=True)

    menu = relationship("MenuModel", back_populates="option_groups")
    option = relationship("OptionModel")

    __table_args__ = (
        UniqueConstraint("menu_id", "option_id", name="uq_menu_option"),
    )

class InventoryItemModel(Base):
    __tablename__ = "inventory"

    ingredient_id = Column(
        BigInteger, ForeignKey("ingredient.id", ondelete="RESTRICT"), primary_key=True
    )
    quantity = Column(BigInteger, nullable=False)

    ingredient = relationship("IngredientModel")


class OrderModel(Base):
    __tablename__ = "customer_order"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_uuid = Column(
        Uuid(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False
    )
    total_price = Column(BigInteger, nullable=False)
    status = Column(Text, nullable=False, default="ORDERED")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    items = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderItemModel.id",
    )


class OrderItemModel(Base):
    __tablename__ = "order_item"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(
        BigInteger, ForeignKey("customer_order.id", ondelete="CASCADE"), nullable=False
    )
    menu_id = Column(BigInteger, nullable=True)
    menu_name = Column(Text, nullable=False)
    menu_price = Column(BigInteger, nullable=False)
    quantity = Column(BigInteger, nullable=False)

    order = relationship("OrderModel", back_populates="items")
    options = relationship(
        "OrderItemOptionModel",
        back_populates="order_item",
        cascade="all, delete-orphan",
        order_by="OrderItemOptionModel.id",
    )


class OrderItemOptionModel(Base):
    __tablename__ = "order_item_option"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_item_id = Column(
        BigInteger, ForeignKey("order_item.id", ondelete="CASCADE"), nullable=False
    )
    option_item_id = Column(BigInteger, nullable=True)
    option_name = Column(Text, nullable=False)
    additional_price = Column(BigInteger, nullable=False, default=0)

    order_item = relationship("OrderItemModel", back_populates="options")