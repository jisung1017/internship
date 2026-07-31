from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class IngredientModel(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    unit = Column(String(10), nullable=False, default="개")


class MenuModel(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    price = Column(Integer, nullable=False)

    recipes = relationship("RecipeItemModel", back_populates="menu", cascade="all, delete-orphan")
    option_groups = relationship("OptionGroupModel", back_populates="menu", cascade="all, delete-orphan")


class RecipeItemModel(Base):
    __tablename__ = "recipe_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    menu = relationship("MenuModel", back_populates="recipes")
    ingredient = relationship("IngredientModel")


class OptionGroupModel(Base):
    __tablename__ = "option_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    name = Column(String(50), nullable=False)
    min_quantity = Column(Integer, nullable=False, default=0)
    max_quantity = Column(Integer, nullable=False, default=1)
    selection_mode = Column(String(20), nullable=False, default="choice")

    menu = relationship("MenuModel", back_populates="option_groups")
    options = relationship("OptionModel", back_populates="option_group", cascade="all, delete-orphan")


class OptionModel(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    option_group_id = Column(Integer, ForeignKey("option_groups.id"), nullable=False)
    name = Column(String(50), nullable=False)
    additional_price = Column(Integer, nullable=False, default=0)

    option_group = relationship("OptionGroupModel", back_populates="options")


class InventoryItemModel(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False, unique=True)
    quantity = Column(Integer, nullable=False)

    ingredient = relationship("IngredientModel")


class InventoryHistoryModel(Base):
    __tablename__ = "inventory_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    change = Column(Integer, nullable=False)
    reason = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)

    ingredient = relationship("IngredientModel")


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_price = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    line_total = Column(Integer, nullable=False)

    order = relationship("OrderModel", back_populates="items")