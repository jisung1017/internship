# 리팩터링 실행 가이드 (인턴용)

> 이 문서는 [`OBJECT_ORIENTED_DESIGN_REVIEW.md`](./OBJECT_ORIENTED_DESIGN_REVIEW.md)의 피드백을
> **"무엇을 / 왜 / 지금 코드 → 이렇게 / 완료 기준"** 형태로 다시 정리한 것입니다.
> 리뷰 문서가 "왜 이렇게 생각하는지"라면, 이 문서는 "그래서 뭘 어떤 순서로 손대는지"입니다.

## 먼저 알아둘 딱 하나의 원칙

지금 코드의 문제는 **"클래스를 안 나눈 것"이 아니라, 나눠놓은 객체가 자기 일을 남에게 맡기고 있는 것**입니다.

- 데이터는 `Recipe`, `OptionGroup`, `CartItem`이 들고 있는데
- 그 데이터로 하는 **계산·판단은 `OrderService`, `Menu`, `CLI`가** 하고 있습니다.

> 목표 한 줄: **"데이터를 가진 객체가, 그 데이터로 하는 판단도 직접 하게 만든다."**

그래서 리팩터링의 방향은 매번 같습니다 →
**"이 계산, 지금 하는 곳 말고 데이터를 가진 객체 안으로 옮길 수 있나?"**

---

## 진행 순서 (쉬운 것 → 어려운 것)

아래 순서는 **앞 단계일수록 안전하고 쉽습니다.** 위에서부터 하나씩, 각 단계마다 **기존 테스트가 통과하는지 확인하고 커밋**하세요. 절대 여러 개를 한 번에 바꾸지 마세요.

| 순서 | 무엇을 | 난이도 | 영향 범위 |
|------|--------|--------|-----------|
| 1 | `type(x) is A` → `isinstance(x, A)` 통일 | ⭐ | 넓지만 안전 |
| 2 | `OptionGroup`에 판단 메서드 추가 | ⭐⭐ | `Menu`, `CLI` |
| 3 | `Recipe`에 계산 메서드 추가 | ⭐⭐ | `OrderService`, `Inventory` |
| 4 | `Cart`/`CartItem`이 가격·재료 계산 | ⭐⭐⭐ | `OrderService` |
| 5 | `OrderService.checkout` 얇게 만들기 | ⭐⭐⭐ | (3,4 끝나면 자동으로 줄어듦) |
| 6 | `create_menu` 데이터/생성 분리 | ⭐⭐ | `environment` |
| 7 | (선택) `OptionSelection` 도입 | ⭐⭐⭐⭐ | 거의 전체 |

---

## 1단계 — 타입 검증 스타일 통일 ⭐

**왜:** 지금 `type(self.name) is not str`, `type(self.price) is not Money`처럼 "정확히 그 클래스"만 허용하는 방식과 `isinstance(...)` 방식이 파일마다 섞여 있습니다. 스타일을 하나로 통일하면 읽기 쉽고, 나중에 확장도 막지 않습니다.

**지금 코드** (`menu.py`, `option_group.py` 등):
```python
if type(self.price) is not Money:
    raise TypeError("Menu 가격은 Money 데이터형이어야 합니다.")
```

**이렇게:**
```python
if not isinstance(self.price, Money):
    raise TypeError("Menu 가격은 Money 데이터형이어야 합니다.")
```

**완료 기준:** `type(...) is ...` 검색 결과가 0건. 기존 테스트 전부 통과.

> 이 단계는 동작이 거의 안 바뀌어서 "리팩터링 감 잡기"용으로 딱 좋습니다.

---

## 2단계 — `OptionGroup`이 옵션 규칙을 직접 판단하게 ⭐⭐

**왜:** "이 옵션이 이 그룹에 속하나?", "몇 개 골랐나?", "개수가 유효한가?"는 **옵션 그룹의 규칙**입니다. 그런데 지금은 이 판단을 `Menu`와 `CLI`가 그룹 내부(`group.options`)를 들여다보며 직접 하고 있습니다.

**지금 코드** (`menu.py`의 `validate_selected_options`):
```python
for group in self.option_groups:
    count = sum(1 for option in selected_options if option in group.options)
    if count < group.min_quantity.value:
        raise ValueError(...)
    if count > group.max_quantity.value:
        raise ValueError(...)
```

**이렇게 —** `OptionGroup`에 메서드를 추가:
```python
class OptionGroup:
    def contains(self, option: Option) -> bool:
        return option in self.options

    def count_selected(self, selected_options: list[Option]) -> int:
        return sum(1 for o in selected_options if self.contains(o))

    def validate(self, selected_options: list[Option]) -> None:
        count = self.count_selected(selected_options)
        if count < self.min_quantity.value:
            raise ValueError(f"{self.name}은(는) 최소 {self.min_quantity.value}개 선택해야 합니다.")
        if count > self.max_quantity.value:
            raise ValueError(f"{self.name}은(는) 최대 {self.max_quantity.value}개까지 선택 가능합니다.")
```

그러면 `Menu`는 각 그룹에게 **위임**만 합니다:
```python
def validate_selected_options(self, selected_options: list[Option]) -> None:
    for option in selected_options:
        if not any(g.contains(option) for g in self.option_groups):
            raise ValueError(f"{option.name} 옵션은 이 메뉴에서 선택할 수 없습니다.")
    for group in self.option_groups:
        group.validate(selected_options)
```

**완료 기준:** `Menu`와 `CLI`에서 `group.options`를 직접 뒤지는 코드가 사라짐. 옵션 검증 테스트 통과.

---

## 3단계 — `Recipe`가 재료 계산을 직접 하게 ⭐⭐

**왜:** `Recipe`는 지금 "재료 목록을 담고 중복만 막는" 상자에 가깝습니다. "주문 수량만큼 재료 곱하기", "레시피끼리 합치기"는 `OrderService`와 `Inventory`에 흩어져 있는데, 이건 원래 **레시피가 할 줄 알아야 하는 계산**입니다.

**지금 코드** (`order_service.py`의 `checkout`) — 서비스가 재료 구조를 직접 조립:
```python
requirements = [(item.menu.recipe, item.quantity) for item in order.items]
requirements += [
    (option.recipe, item.quantity)
    for item in order.items
    for option in item.selected_options
]
```

**이렇게 —** `Recipe`에 계산 메서드를 추가:
```python
class Recipe:
    def multiply(self, quantity: Quantity) -> "Recipe":
        """레시피를 주문 수량만큼 확장한다."""
        ...

    def merge(self, other: "Recipe") -> "Recipe":
        """다른 레시피와 합치면서 같은 재료 수량을 합산한다."""
        ...

    def required_items(self) -> list[RecipeItem]:
        """외부에서 안전하게 쓸 수 있는 필요 재료 목록."""
        ...
```

그러면 서비스는 "재료가 어떻게 생겼는지" 몰라도 되고, 계산은 도메인 안에서 일어납니다.

**완료 기준:** `checkout` 안의 `requirements` 조립 로직이 도메인 객체 호출로 대체됨. 재고 차감 테스트 통과.

---

## 4단계 — `CartItem`/`Cart`가 가격·재료를 계산하게 ⭐⭐⭐

**왜:** "이 장바구니 항목의 총 가격", "필요 재료"는 그 항목이 가진 정보(메뉴·옵션·수량)로 계산됩니다. 즉 **`CartItem` 자신이 계산 주인**입니다. 또 지금 `OrderService.add_to_cart`가 `CartItem`을 직접 만들어 넣는데, 이건 "장바구니에 담는다"는 `Cart`의 일에 가깝습니다.

**지금 코드** (`order_service.py`):
```python
def add_to_cart(self, cart, menu, quantity, selected_options):
    menu.validate_selected_options(selected_options)
    item = CartItem(menu=menu, quantity=quantity, selected_options=selected_options)
    cart.add_item(item)
```

**이렇게 —** `Cart`가 항목 생성까지 책임:
```python
# Cart
def add_menu(self, menu, quantity, selected_options):
    menu.validate_selected_options(selected_options)
    self.items.append(CartItem(menu, quantity, selected_options))

# CartItem  (3단계의 Recipe 메서드를 활용)
def total_price(self) -> Money: ...
def required_recipe(self) -> Recipe: ...   # 메뉴 레시피 + 옵션 레시피 합산 × 수량
```

**완료 기준:** `OrderService`가 `CartItem`을 직접 생성하지 않음. 가격·재료 계산이 `CartItem` 안에 있음.

---

## 5단계 — `OrderService.checkout`를 "조율자"로 얇게 ⭐⭐⭐

**왜:** 3·4단계가 끝나면 `checkout`이 하던 계산이 도메인으로 옮겨가 **자동으로 얇아집니다.** 이 단계는 새 코드를 많이 짜는 게 아니라, checkout에 남은 계산을 도메인 호출로 바꿔주는 "정리"입니다.

**목표 모습:** `checkout`은 아래 흐름만 남깁니다.
1. 주문 만들기 (`Order.from_cart`)
2. 재고 되나 물어보기 (`inventory.can_consume_all`)
3. 결제 (`payment.pay`)
4. 재고 차감 (`inventory.consume_all`)
5. 장바구니 비우기

각 줄이 **"누구에게 시킨다"**로만 읽히고, 계산식(`for ... for ...`)이 안 보이면 성공입니다.

> ⚠️ `OrderService`를 **없애는 게 아닙니다.** 순서를 조율하는 역할은 그대로 필요합니다. "계산을 직접 하지 않게" 줄이는 것뿐입니다.

---

## 6단계 — `create_menu` 데이터/생성 분리 ⭐⭐

**왜 (오해 주의):** `create_menu`의 하드코딩은 **나쁜 게 아닙니다.** DB가 없는 과제에서 시작 시점에 메뉴 데이터를 메모리에 구성하는 건 자연스러운 역할(composition root)입니다. 목표는 **"하드코딩 제거"가 아니라 "데이터 정의와 객체 생성 분리"**입니다. 메뉴를 추가할 때 코드가 아니라 데이터만 손대면 되게요.

**이렇게 —** 정의는 데이터로, 조립은 작은 함수로:
```python
MENU_DEFINITIONS = [
    {
        "name": "아메리카노",
        "price": 3000,
        "recipe": {"원두": 18, "물": 250, "컵": 1},
        "option_groups": ["temperature", "shot", "syrup"],
    },
]
```
그리고 `create_recipe`, `create_option_group`, `create_menu_item` 같은 변환 함수가 이 데이터를 객체로 바꿉니다.

**완료 기준:** 메뉴 추가가 "데이터 한 줄 추가"로 가능. 기존 메뉴 이름·가격·레시피·옵션 구성이 **그대로** 유지됨(테스트로 확인).

---

## 7단계 (선택) — `OptionSelection`으로 옵션 수량 명시 ⭐⭐⭐⭐

**왜:** 지금 "샷 2개"는 `[shot, shot]`처럼 같은 객체를 리스트에 두 번 넣어 표현합니다. 동작은 하지만 "옵션 하나를 몇 개"라는 의미가 중복으로 흐릿하게 표현됩니다.

**이렇게:**
```python
@dataclass(frozen=True)
class OptionSelection:
    option: Option
    quantity: Quantity
```

**주의:** 이건 `Menu`, `CartItem`, `OrderService`, `CLI`, 테스트 **전부에 영향**을 줍니다. 앞 단계를 다 끝내 구조가 정리된 **맨 마지막에**, 별도 브랜치에서 하세요. 급하지 않으면 안 해도 됩니다.

---

## 곁다리로 같이 챙기면 좋은 것

### 공개 list 방어 (틈틈이)
`Recipe.items`, `OptionGroup.options`, `Cart.items`가 전부 공개 list라서, 생성 후 외부에서 직접 수정하면 `__post_init__`의 검증을 우회할 수 있습니다.
예) `Recipe` 만든 뒤 `recipe.items.append(중복재료)` → 중복 검증 무력화.
→ 내부는 tuple로 저장하거나, 외부엔 복사본/읽기 전용 접근자만 제공. **한 번에 다 바꾸지 말고** 변경 위험이 큰 `Recipe.items`, `OptionGroup.options`, `Cart.items`부터.

---

## 매 단계 체크리스트 (복붙용)

- [ ] 이 단계에서 **딱 하나**만 바꿨다
- [ ] 옮긴 계산이 "데이터를 가진 객체" 안으로 들어갔다
- [ ] `python -m pytest` (또는 프로젝트 테스트 명령) 전부 통과
- [ ] 커밋 메시지에 "무엇을 왜" 남겼다
- [ ] 그다음 단계로 넘어간다

> 핵심 감각: 리팩터링 후 각 객체가 **"데이터 상자"가 아니라 "스스로 판단하고 협력하는 존재"**로 보이면 잘 가고 있는 것입니다.
