from dataclasses import dataclass

@dataclass
class Ingredient:
    name: str

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise TypeError("Ingredient 이름은 문자열이여야 합니다.")
    
        self.name = self.name.strip()
        if not self.name:
            raise  ValueError("Ingredient 이름은 빈칸일 수 없습니다.")
