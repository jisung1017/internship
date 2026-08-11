from dataclasses import dataclass, field

from src.domain.option import Option
from src.domain.quantity import Quantity

SELECTION_MODES = {"choice", "count"}


@dataclass
class OptionGroup:
    name: str

    min_quantity: Quantity = field(default_factory=lambda: Quantity(1))
    max_quantity: Quantity = field(default_factory=lambda: Quantity(1))
    options: list[Option] = field(default_factory=list)
    selection_mode: str = "choice"

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise TypeError("OptionGroup 이름은 문자열이여야 합니다.")

        self.name = self.name.strip()
        if not self.name:
            raise ValueError("OptionGroup 이름은 빈칸일 수 없습니다.")

        if not isinstance(self.options, list):
            raise TypeError("OptionGroup options 는 list 여야 합니다.")

        for option in self.options:
            if not isinstance(option, Option):
                raise TypeError("OptionGroup options 는 Option 타입으로만 이루어져야 합니다.")

        if not isinstance(self.min_quantity, Quantity):
            raise TypeError("OptionGroup min_quantity 는 Quantity 자료형 이여야 합니다.")

        if not isinstance(self.max_quantity, Quantity):
            raise TypeError("OptionGroup max_quantity 는 Quantity 자료형 이여야 합니다.")

        if self.min_quantity.is_greater_than(self.max_quantity):
            raise ValueError("최소 수량은 최대 수량보다 많을 수 없습니다.")

        if self.selection_mode not in SELECTION_MODES:
            raise ValueError(f"selection_mode 는 {SELECTION_MODES} 중 하나여야 합니다.")

    def contains(self, option: Option) -> bool:
        return option in self.options

    def count_selected(self, selected_options: list[Option]) -> int:
        return sum(1 for option in selected_options if self.contains(option))

    def validate(self, selected_options: list[Option]) -> None:
        count = self.count_selected(selected_options)

        option_names = "/".join(option.name for option in self.options)
        
        if count < self.min_quantity.value:
            if option_names:
                raise ValueError(
                    f"{self.name}은(는) 필수 선택 항목입니다. ({option_names})"
                )
            raise ValueError(
                f"{self.name}은(는) 최소 {self.min_quantity.value}개 선택해야 합니다."
            )

        if count > self.max_quantity.value:
            raise ValueError(
                f"{self.name}은(는) 최대 {self.max_quantity.value}개 선택해야 합니다."
        )

    def find_option_by_name(self, name: str) -> Option | None:
        return next((option for option in self.options if option.name.upper() == name.upper()), None)

    def parse_selection(self, raw: str) -> list[Option]:
        raw = raw.strip()

        if self.selection_mode == "count":
            selected = self._parse_count_selection(raw)
        else:
            selected = self._parse_choice_selection(raw)

        self.validate(selected)

        return selected

    def _parse_count_selection(self, raw: str) -> list[Option]:
        count = self._parse_count(raw)

        return [self.options[0]] * count

    def _parse_count(self, raw: str) -> int:
        try:
            value = int(raw) if raw else 0
        except ValueError:
            raise ValueError("숫자를 입력해주세요.")

        if value < 0:
            raise ValueError("수량은 0 이상이어야 합니다.")

        return value

    def _parse_choice_selection(self, raw: str) -> list[Option]:
        if not raw:
            return []

        return [self._match_option_or_raise(name) for name in raw.split()]

    def _match_option_or_raise(self, name: str) -> Option:
        matched = self.find_option_by_name(name)

        if matched is not None:
            return matched

        option_names = "/".join(option.name for option in self.options)
        raise ValueError(f"{option_names} 입력해주세요 (대소구분X)")