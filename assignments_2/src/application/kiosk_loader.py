from dataclasses import dataclass

from src.domain.inventory import Inventory
from src.domain.menu import Menu


@dataclass(frozen=True)
class KioskLoader:
    menus: list[Menu]
    inventory: Inventory