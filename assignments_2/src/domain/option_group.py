from dataclasses import dataclass, field
from src.domain.option import Option
from src.domain.option_item import OptionItem
from src.domain.quantity import Quantity

SELECTION_MODES = {"choice", "count"}


@dataclass
class OptionGroup:
    """메뉴와 옵션을 연결하는 매핑 객체 - 기본 선택값 자동 적용 기능 보유"""
    option: Option
    override_min_quantity: Quantity | None = None
    override_max_quantity: Quantity | None = None
    override_selection_mode: str | None = None
    override_default_option_name: str | None = None

    def __post_init__(self):
        if not isinstance(self.option, Option):
            raise TypeError("OptionGroup option은 Option 타입이어야 합니다.")
        if self.override_min_quantity is not None and not isinstance(self.override_min_quantity, Quantity):
            raise TypeError("OptionGroup override_min_quantity는 Quantity 타입이어야 합니다.")
        if self.override_max_quantity is not None and not isinstance(self.override_max_quantity, Quantity):
            raise TypeError("OptionGroup override_max_quantity는 Quantity 타입이어야 합니다.")
        if self.min_quantity.is_greater_than(self.max_quantity):
            raise ValueError("최소 선택 수량이 최대 선택 수량보다 클 수 없습니다.")
        if self.selection_mode not in SELECTION_MODES:
            raise ValueError(f"selection_mode는 {SELECTION_MODES} 중 하나여야 합니다.")
        if self.override_default_option_name is not None:
            if not isinstance(self.override_default_option_name, str):
                raise TypeError("override_default_option_name은 str 타입이어야 합니다.")
            self.override_default_option_name = self.override_default_option_name.strip()

    @property
    def name(self) -> str:
        return self.option.name

    @property
    def min_quantity(self) -> Quantity:
        return self.override_min_quantity if self.override_min_quantity is not None else self.option.default_min

    @property
    def max_quantity(self) -> Quantity:
        return self.override_max_quantity if self.override_max_quantity is not None else self.option.default_max

    @property
    def selection_mode(self) -> str:
        return self.override_selection_mode if self.override_selection_mode is not None else self.option.selection_mode

    @property
    def default_option_name(self) -> str | None:
        return self.override_default_option_name if self.override_default_option_name is not None else self.option.default_option_name

    @property
    def default_option(self) -> OptionItem | None:
        if not self.default_option_name:
            return None
        return self.find_option_by_name(self.default_option_name)

    @property
    def options(self) -> list[OptionItem]:
        return self.option.items

    def contains(self, option_item: OptionItem) -> bool:
        return option_item in self.options

    def count_selected(self, selected_options: list[OptionItem]) -> int:
        return sum(1 for item in selected_options if self.contains(item))

    def validate(self, selected_options: list[OptionItem]) -> None:
        count = self.count_selected(selected_options)
        option_names = "/".join(item.name for item in self.options)

        if count < self.min_quantity.value:
            if option_names:
                raise ValueError(f"{self.name} 옵션에서 최소 {self.min_quantity.value}개를 선택해야 합니다. ({option_names})")
            raise ValueError(f"{self.name} 옵션에서 최소 {self.min_quantity.value}개를 선택해야 합니다.")

        if count > self.max_quantity.value:
            raise ValueError(f"{self.name} 옵션에서 최대 {self.max_quantity.value}개까지만 선택할 수 있습니다.")

    def find_option_by_name(self, name: str) -> OptionItem | None:
        return next((item for item in self.options if item.name.upper() == name.upper()), None)

    def parse_selection(self, raw: str) -> list[OptionItem]:
        raw = raw.strip()
        if not raw and self.default_option is not None:
            return [self.default_option]

        if self.selection_mode == "count":
            selected = self._parse_count_selection(raw)
        else:
            selected = self._parse_choice_selection(raw)
        self.validate(selected)
        return selected

    def _parse_count_selection(self, raw: str) -> list[OptionItem]:
        count = self._parse_count(raw)
        if not self.options:
            return []
        return [self.options[0]] * count

    def _parse_count(self, raw: str) -> int:
        try:
            value = int(raw) if raw else 0
        except ValueError:
            raise ValueError("숫자를 입력해주세요.")
        if value < 0:
            raise ValueError("0 이상의 숫자를 입력해주세요.")
        return value

    def _parse_choice_selection(self, raw: str) -> list[OptionItem]:
        if not raw:
            return []
        return [self._match_option_or_raise(name) for name in raw.split()]

    def _match_option_or_raise(self, name: str) -> OptionItem:
        matched = self.find_option_by_name(name)
        if matched is not None:
            return matched
        option_names = "/".join(item.name for item in self.options)
        raise ValueError(f"'{name}'은(는) 유효한 옵션이 아닙니다. ({option_names} 중 선택)")