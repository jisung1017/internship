from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Ingredient:
    id: int
    name: str
    unit: str


@dataclass(frozen=True)
class RecipeIngredient:
    ingredient: Ingredient
    amount: int


@dataclass(frozen=True)
class Recipe:
    id: int
    menu_id: int
    name: str
    ingredients: List[RecipeIngredient]
