from dataclasses import dataclass, field

from src.domain.option import Option

@dataclass
class OptionGroup:
    name: str
    required: bool
    multiple: bool
    options: list[Option] = field(default_factory=list)

    def __post_init__(self):
        if type(self.name) is not str:
            raise TypeError("OptionGroup 이름은 문자열이여야 합니다.")
    
        self.name = self.name.strip()
        if not self.name:
            raise  ValueError("OptionGroup 이름은 빈칸일 수 없습니다.")

        if type(self.required) is not bool:
            raise TypeError("OptionGroup required 은 boolean 형 이여야 합니다.")

        if type(self.multiple) is not bool:
            raise TypeError("OptionGroup multiple 은 boolean 형 이여야 합니다.")

        