from enum import Enum


class Category(str, Enum):
    COFFEE = "COFFEE"
    TEA = "TEA"
    BEVERAGE = "BEVERAGE"
    DESSERT = "DESSERT"