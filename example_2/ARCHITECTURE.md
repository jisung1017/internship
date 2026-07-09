# 키오스크 구조 참고 가이드

이 디렉터리(`example_2`)는 완성된 구현이 아니라, **키오스크 애플리케이션을 어떤 구조로 나눌 것인가**를 보여주기 위한 골격(skeleton) 코드다. 도메인 세부 로직보다 **계층 분리 · 상태 관리 · 조립 지점**에 초점을 맞춰 읽으면 된다.

기능적 완결성(값 객체, 옵션의 재고 반영 등)은 의도적으로 비워 두었다. 그 부분은 `assignments_2`의 리치 도메인 모델을 참고한다.

## 무엇을 참고해야 하나

이 코드에서 따라 할 핵심은 네 가지다.

1. **계층 분리** — 데이터/규칙(`interfaces/domain`) ↔ 유스케이스(`services`) ↔ 조립·입출력(`index.py`)
2. **상태머신** — 화면 흐름을 `KioskSession`이 상태(`StepType`)와 전이 규칙으로 명시한다
3. **파사드** — `Kiosk`가 세션을 감싸 외부에 조작 API만 노출한다
4. **조립 지점(Composition Root)** — `index.py`가 데이터 상수 정의 + 의존성 주입을 한곳에서 담당한다

## 디렉터리 구조

```
example_2/
├── index.py                    # 조립 지점 + 입출력(콘솔) + 화면 디스패치
├── conftest.py                 # 테스트 공용 fixture
├── interfaces/
│   └── domain/                 # 순수 데이터 모델 계층 (규칙만, IO/서비스 의존 없음)
│       ├── menu.py             #   Menu
│       ├── option.py           #   Option
│       ├── cart.py             #   Cart, CartItem
│       ├── recipe.py           #   Ingredient, RecipeIngredient, Recipe
│       └── inventory.py        #   Inventory
├── services/                   # 유스케이스 계층 (도메인을 조합해 흐름을 수행)
│   ├── kiosk_session.py        #   KioskSession: 화면 상태머신  ★핵심
│   ├── kiosk.py                #   Kiosk: 세션 파사드
│   ├── order.py                #   OrderService: 결제+재고 흐름 조율
│   ├── inventory.py            #   InventoryService: 재고 확인/차감
│   └── payment.py              #   PaymentService: 결제
└── tests/
    └── unit/test_kiosk.py      # Kiosk/세션 상태 전이 검증
```

의존 방향은 항상 **바깥(index) → 안(services) → 더 안(domain)** 한 방향이다. `interfaces/domain`은 어떤 서비스나 IO도 import 하지 않는다. 이 방향이 깨지지 않게 유지하는 것이 계층 분리의 핵심이다.

## 핵심 1: 화면 흐름을 상태머신으로 (`KioskSession`)

키오스크의 화면 전환은 `if`문을 여기저기 흩뿌리는 대신, **상태 + 전이 규칙**을 가진 하나의 객체로 모은다.

```
LOADING ──start()──▶ MENU ──select_menu()──▶ OPTION ──add_to_cart()──▶ CART
                       ▲                                                  │
                       └────────────── go_to_menu() ──────────────────────┤
                                                                          │
                                          go_to_payment() ──▶ PAYMENT ──▶ COMPLETE
                                          (장바구니 비면 거부)
```

- 상태: `step`(현재 화면), `selected_menu` / `selected_options`(선택 중인 컨텍스트), `cart`
- 전이: `select_menu`, `select_option`, `add_to_cart`, `go_to_*` 메서드가 상태를 다음으로 옮긴다
- **불변식은 전이 안에서 지킨다** — 예: `go_to_payment()`는 장바구니가 비어 있으면 `ValueError`로 전이를 막는다. "지금 이 화면으로 갈 수 있는가"의 판단이 세션 한곳에 모인다.

> 배울 점: 화면/단계가 있는 UI는 상태를 각 화면 코드에 흩기보다, 이렇게 상태 객체로 모으면 흐름이 코드로 읽힌다.

## 핵심 2: 파사드 (`Kiosk`)

`Kiosk`는 `KioskSession`을 감싸 외부(=`index.py`의 화면 함수들)에 조작 API만 노출하는 얇은 층이다.

```python
def select_menu(self, menu: Menu):
    self._get_session().select_menu(menu)
```

지금은 대부분 단순 위임이지만, 이 층이 있는 이유는 **"외부가 세션 내부 구조에 직접 손대지 않게 하는 경계"** 를 만들기 위해서다. 인증, 다중 세션, 관리자 모드 같은 관심사가 생기면 그 판단이 붙을 자리가 바로 여기다. (이번 골격에서는 최소화를 위해 그런 확장 코드는 비워 두었다.)

## 핵심 3: 조립 지점 (`index.py`)

`index.py` 한 파일이 세 가지를 담당한다.

1. **데이터 정의** — `MENUS`, `OPTIONS`, `RECIPES`, `INVENTORIES` 상수. 메뉴 추가는 여기 데이터만 바꾸면 된다(도메인/서비스 코드 수정이 아님).
2. **의존성 주입** — 서비스 조립을 한곳에서:
   ```python
   order_service = OrderService(
       inventory_service=InventoryService(),
       payment_service=PaymentService(),
   )
   ```
3. **입출력 격리** — `input()` / `print()`는 **오직 `index.py`에만** 있다. `services`와 `domain`은 콘솔을 모른다. 그래서 테스트에서 콘솔 없이 흐름을 검증할 수 있다.

화면 디스패치도 분기문 대신 매핑 테이블로 표현한다.

```python
SCREEN_HANDLERS = {
    StepType.MENU: show_menu_screen,
    StepType.OPTION: show_option_screen,
    StepType.CART: show_cart_screen,
    StepType.PAYMENT: show_payment_screen,
}
```

## 핵심 4: 서비스 계층 (`order` / `inventory` / `payment`)

유스케이스(결제 흐름)는 도메인이 아니라 서비스가 조율한다. `OrderService.checkout`이 좋은 예다.

```python
def checkout(self, cart, recipes, inventories):
    self.inventory_service.check_available(cart, recipes, inventories)  # 1) 가능한지 먼저 확인
    payment_result = self.payment_service.pay(cart)                     # 2) 결제
    self.inventory_service.decrease_stock(cart, recipes, inventories)   # 3) 재고 차감
    return payment_result
```

재고 확인 → 결제 → 차감 순서로, 재고가 부족하면 결제 전에 막는다. 서비스는 "무엇을 어떤 순서로" 만 알고, "어떻게"는 각 서비스/도메인에 위임한다.

## 이 골격을 확장하는 법

| 하고 싶은 것 | 바꾸는 곳 |
|---|---|
| 메뉴/옵션/레시피/재고 추가 | `index.py`의 데이터 상수 |
| 새 화면/단계 추가 | `StepType`에 상태 추가 → `KioskSession`에 전이 메서드 → `index.py`에 화면 함수 + `SCREEN_HANDLERS` 등록 |
| 새 유스케이스(예: 취소) | `services`에 서비스 추가, `index.py`에서 조립·주입 |
| 새 도메인 규칙 | `interfaces/domain`의 해당 모델에 메서드로 (IO/서비스 의존 없이) |

## 의도적으로 비워 둔 부분 (이 골격의 범위 밖)

구조를 드러내는 데 집중하기 위해 다음은 넣지 않았다. 실제 구현으로 갈 때 `assignments_2`를 참고해 채운다.

- **값 객체(원시값 포장)** — 금액이 아직 `int`다. `Money` 같은 값 객체로 감싸면 음수 방지·연산 규칙을 캡슐화할 수 있다.
- **옵션의 재고 반영** — `Option`이 가격만 갖고 레시피(재료 소모)를 갖지 않는다.
- **ID 기반 조회 vs 객체 합성** — 지금은 `recipe.menu_id`로 서비스에서 join한다. 도메인을 더 리치하게 가면 `Menu`가 `Recipe`를 직접 소유하는 합성으로 바꿀 수 있다.

## 한 줄 요약

- `KioskSession` = 화면 상태머신 (**따라 할 1순위**)
- `Kiosk` = 세션 파사드(경계)
- `index.py` = 데이터 정의 + 조립 + 입출력 (한곳에)
- `services` = 유스케이스 조율, `interfaces/domain` = 순수 데이터/규칙
- 의존은 항상 바깥 → 안 한 방향, 입출력은 `index.py`에만
