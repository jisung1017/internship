from dataclasses import dataclass


@dataclass(frozen=True)
class Menu:
    id: int
    name: str
    price: int
    description: str
