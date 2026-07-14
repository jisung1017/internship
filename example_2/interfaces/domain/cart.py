from dataclasses import dataclass, field
from typing import List

from example_2.interfaces.domain.menu import Menu
from example_2.interfaces.domain.option import Option


@dataclass(frozen=True)
class CartItem:
    menu: Menu
    options: List[Option]

    def total_cost(self):
        return self.menu.price + sum(option.total_cost() for option in self.options)


@dataclass
class Cart:
    items: List[CartItem] = field(default_factory=list)

    def init(self):
        self.items.clear()

    def add(self, item: CartItem):
        self.items.append(item)

    def is_empty(self):
        return len(self.items) == 0

    def total_cost(self):
        return sum(item.total_cost() for item in self.items)
