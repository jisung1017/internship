# 키오스크 과제 진행 평가

> 평가 기준일: 2026-07-29 · 대상 커밋: `43f3f4a` (main)
> 평가 항목: TDD / 객체지향 이해도 / 계층 규칙 준수 / 객체 간 메시지 설계

---

## 종합 요약

| 항목                | 점수         | 한 줄 평                                                                                                        |
| ------------------- | ------------ | --------------------------------------------------------------------------------------------------------------- |
| TDD                 | ★★★★★ (9/10) | 커밋 단위로 test→feat→refactor가 일관되게 관찰됨. 교과서적 사이클.                                              |
| 객체지향 이해도     | ★★★★☆ (8/10) | VO/엔티티/서비스 구분이 명확하고 행위 중심 설계. 방어적 타입검사 과다.                                          |
| 계층 규칙 준수      | ★★★★☆ (8/10) | domain→application→infrastructure/interface 의존 방향 준수. Protocol로 역전. 다만 domain에 파싱 책임 일부 누수. |
| 객체 간 메시지 설계 | ★★★★☆ (7/10) | 책임 분리와 위임이 훌륭. 단, `checkout` 3중 계층·재고 소비/영속화 경계에 개선 여지.                             |

특히 "빈약한 도메인 모델(anemic model)"에 빠지지 않고 객체에 행위를 부여했다는 점, 그리고 TDD 리듬을 커밋으로 잘 드러났다.

---

## 1. TDD — ★★★★★ (9/10)

### 근거 (커밋 로그)

초기 도메인 구축 구간의 커밋 순서가 Red-Green-Refactor를 그대로 보여줌.

```
6439e5d test: Quantity value object 테스트 케이스 구현
b056132 feature: Quantity value object 데이터 클래스 구현 및 테스트 통과
...
0181363 test: Money Value Object 예외 및 동작 테스트 정의
2f3cc22 feat: Money value object 데이터 클래스 구현
8ed486a refactor: Money test case 리팩터링
...
b83191c test: CartItem 테스트 케이스 작성
b2d5537 feat: CartItem 기본 필드 구현
1feb780 test: CartItem.total_price() 계산 함수 테스트 케이스 작성
113ea8c feat: CartItem 에서의 total_price 메소드 구현
```

- **test 커밋이 feat 커밋보다 먼저 오는 패턴이 거의 모든 도메인 객체에서 반복**된다 (Quantity, Money, Ingredient, RecipeItem, Recipe, InventoryItem, Option, OptionGroup, Menu, Cart, Order, Payment, OrderService...).
- test:22 / feat:38 / refactor:6 — 구현마다 테스트가 짝을 이루며, refactor 커밋이 별도로 존재해 **초록 상태에서 리팩터링하는 습관**이 확인된다.
- 테스트 커버리지가 도메인에 그치지 않고 `application`(OrderService), `infrastructure`(동시성·원자성 `test_order_persister_atomicity.py`, `test_inventory_concurrency.py`), `interface`(CLI), 인수테스트(`test_acceptance.py`)까지 계층별로 존재한다.

### 잘한 점

- 테스트 명이 행위를 서술한다: `test_checkout_raises_out_of_stock_error_and_clears_cart`, `test_checkout_does_not_charge_when_is_out_of_stock` — **의도(원자성 보장)를 테스트가 문서화**한다.
- Given/When/Then 주석으로 시나리오를 구조화. 경계값 테스트(`test_checkout_boundary_payment_and_inventory`: 잔액 6000/재고 36으로 정확히 0이 되는 케이스) 존재.
- 테스트 픽스처/팩토리 헬퍼(`create_menu`, `create_cart_item`)로 중복을 제어.

### 개선 여지

- `test_order_service.py`와 `test_cart.py`에 **동일한 `create_menu`/`create_cart_item` 헬퍼가 복붙**되어 있다. `tests/conftest.py`나 공용 빌더로 승격하면 테스트 유지보수 비용이 줄어든다.
- CLI(`interface`) 테스트는 도메인 대비 얇다. 입력 파싱 분기(개발자 모드 `77`, 잘못된 입력 재시도 루프)가 늘어난 만큼 상태 전이 테스트를 보강할 여지가 있다.

---

## 2. 객체지향 이해도 — ★★★★☆ (8/10)

### 잘한 점

- **값 객체(VO)와 엔티티 구분이 명확**하다. `Money`, `Quantity`는 `@dataclass(frozen=True)` 불변 VO로 만들고 `add/subtract/multiply/__lt__` 등 연산을 객체 안에 캡슐화했다. 원시값(int) 대신 도메인 타입을 흐르게 해 **원시 타입 집착(Primitive Obsession)을 회피**했다.
- **행위 중심 설계**: `OptionGroup`이 `validate`, `count_selected`, `contains`, `parse_selection`을 스스로 책임진다. `Inventory`가 `can_consume_all`/`consume_all`을 통해 재고 규칙을 소유한다. 데이터만 든 빈약한 모델이 아니다.
- **불변식을 생성자(`__post_init__`)에 모아** 항상 유효한 객체만 존재하도록 보장한다(예: `Inventory`의 재료 중복 금지, `OptionGroup`의 min>max 금지).
- `Money.subtract`가 음수 결과를 막고, `Payment.pay`가 잔액 규칙을 소유하는 등 **책임이 데이터를 가진 객체에 붙어 있다**(Tell, Don't Ask).
- `can_consume_all`을 `copy.deepcopy`로 시뮬레이션해 원본을 오염시키지 않고 검사하는 접근은 부작용 격리 감각이 좋다.

### 개선 여지

- **방어적 `isinstance` 검사가 과도**하다. `Order.__init__`, `Menu.__post_init__`, `Cart.add_item` 등에서 타입 체크가 반복된다. 타입힌트+mypy를 쓰는 프로젝트이므로, 런타임 타입검사는 **신뢰 경계(외부 입력이 들어오는 곳)로 국한**하고 내부 협력 객체 간에는 걷어내는 편이 응집도를 높인다. 지금은 도메인 로직보다 가드코드가 더 길어 보이는 파일이 있다.
- `can_consume_all`의 `deepcopy`는 정확하지만 재고/이력이 커지면 비용이 크다. 나중에는 "필요량 합산 후 비교"하는 순수 계산으로 대체할 수 있다(현 단계에선 과한 최적화이므로 지금 방식이 합리적).
- `Cart.total_price()`와 `Order.total_price()`가 사실상 동일 로직이다. `Order`가 `items`를 갖는 이상 계산 책임의 단일 출처를 고민해볼 만하다.

---

## 3. 계층 간 규칙 준수 — ★★★★☆ (8/10)

### 계층 구조

```
interface (CLI)         ── 입출력, 화면
   ↓
application              ── 유스케이스 조율 (KioskSession, OrderService,
   ↓                        CheckoutService, KioskAdminService, *Persister Protocol)
domain                   ── 순수 비즈니스 규칙 (Money, Inventory, Order ...)
   ↑ (의존 역전)
infrastructure           ── Postgres 구현체 (Protocol 구현)
```

### 잘한 점

- **의존 방향이 안쪽(domain)을 향한다.** `domain/*`는 다른 계층을 import하지 않는 순수 모듈이다(확인됨). `main.py`가 조립(Composition Root) 역할을 하며 infrastructure 구현체를 application에 주입한다.
- **의존성 역전이 Protocol로 구현**되어 있다. `OrderPersister`, `InventoryPersister`, `OrderHistoryReader`가 application 계층의 `Protocol`이고, `infrastructure/repositories/Postgres*`가 이를 구현한다. 덕분에 `OrderService`/`KioskAdminService`는 DB를 전혀 모른다(`order_persister: OrderPersister | None = None`으로 DB 없이도 동작·테스트 가능).
- **원자성 경계를 infrastructure에 캡슐화**: `PostgresOrderPersister.persist`가 하나의 `transaction()` 안에서 주문+재고를 함께 커밋/롤백한다. 트랜잭션 지식이 도메인으로 새지 않는다.
- 최근 `refactor: kiosk_session 책임 분리` 커밋에서 `KioskSession`이 "화면 흐름"만 맡고 결제는 `CheckoutService`, 관리자 모드는 `KioskAdminService`로 위임하도록 정리한 것은 **계층 내 책임 분해**로도 훌륭하다(주석에 "이 클래스는 그 둘을 전혀 모른다"고 의도를 명시).

### 개선 여지 (감점 지점)

- **domain에 입력 파싱 책임이 누수**되어 있다. `OptionGroup.parse_selection(raw: str)` / `_parse_count` / `find_option_by_name`은 **CLI 문자열 입력을 해석**하는 로직이다. 이는 본질적으로 interface(또는 application) 관심사다. 도메인은 "무엇이 유효한 선택인가(`validate`)"만 알고, "사용자가 친 문자열을 Option으로 바꾸는 일"은 바깥 계층이 하는 편이 계층 순수성에 맞다. 지금은 domain이 `raw.split()`, 대소문자 무시 같은 UI 규칙을 알고 있다.
- **검증 규칙이 계층에 중복**된다. 수량 한도가 `cli.parse_quantity`의 `1..10`과 `pending_order.MIN/MAX_ORDER_QUANTITY` 두 곳에 하드코딩되어 있다. 단일 출처(도메인 상수)로 모으고 interface는 그 값을 참조하는 게 안전하다.

---

## 4. 객체 간 메시지 설계 — ★★★★☆ (7/10)

### 잘한 점

- **메시지가 명령형이고 의도가 드러난다**: `cart.add_item`, `inventory.can_consume_all` / `consume_all`, `payment.pay(order)`, `pending_order.select_current_option_group`. 게터로 데이터를 꺼내 바깥에서 조작하지 않고 **객체에게 일을 시킨다**.
- **협력 흐름이 자연스럽다**: `KioskSession.select_quantity` → `PendingOrder.set_quantity` → `OrderService.add_to_cart` → `Menu.validate_selected_options` → `Cart.add_item`. 각 객체가 자기 몫만 검증하고 다음으로 위임한다.
- `PendingOrder`라는 **"조립 중 주문" 개념을 객체로 승격**한 것이 좋다. 세션이 흩어진 선택 상태(menu/options/quantity/group_index)를 들고 있는 대신, 진행 중 상태와 규칙(`is_option_selection_done`, `is_ready`)을 한 객체가 소유한다.
- 실패 경로 메시지 설계가 일관적: 예외를 던지고(`OutOfStockError`, `InsufficientBalanceError`) 세션이 잡아 화면을 되돌린다. 부작용(장바구니 clear)이 도메인 규칙과 함께 묶여 있다.

### 개선 여지 (감점 지점)

- **`checkout` 메시지가 3계층에 동명으로 존재**한다: `KioskSession.checkout` → `CheckoutService.checkout` → `OrderService.checkout`. 위임 체인 자체는 나쁘지 않으나, 같은 이름이 층마다 미묘하게 다른 일을 해서 "어느 checkout이 진짜 결제냐"를 읽는 사람이 추적해야 한다. 예: application 내부는 `place_order`/`persist_order`처럼 **층별로 다른 동사**를 쓰면 메시지 의도가 선명해진다.
- **재고 소비(메모리)와 영속화(DB) 사이에 원자성 틈**이 있다. `OrderService.checkout`이 이미 `inventory.consume_all`로 **메모리 상태를 차감**하고 `cart.clear()`까지 한 뒤, 그 다음에 `CheckoutService`가 `order_persister.persist`로 DB 커밋을 시도한다. 만약 persist가 실패하면 **메모리 재고는 이미 줄었는데 DB는 롤백**되어 두 상태가 어긋난다. 지금은 단일 프로세스라 치명적이지 않지만, "결제 유스케이스 전체가 하나의 원자적 단위"라는 의도를 메시지 설계가 아직 완전히 보장하지 못한다. 소비를 persist 성공 이후로 미루거나, 실패 시 보상(재적재)하는 흐름을 고려할 것.
- `OrderService.checkout`이 `cart.clear()`를 **성공/실패 양쪽에서 호출**한다. "결제 서비스가 남의 장바구니를 비우는" 부작용이 여러 분기에 흩어져 있어, 소유권(누가 cart 생명주기를 책임지는가)이 흐릿하다. 세션이 cart를 소유한다면 clear도 세션 쪽 책임으로 올리는 편이 메시지 방향과 일치한다.
- `KioskAdminService.restock`이 `self.order_service.inventory`를 **꿰뚫어 접근**(`order_service.inventory.restock(...)`)한다. Law of Demeter 관점에서 inventory를 직접 주입받거나 order_service가 restock 메시지를 중계하는 편이 결합을 낮춘다.

---

## 다음 스텝 제안 (우선순위)

1. **결제 원자성 재설계**: 재고 차감을 DB 커밋 성공 이후로 옮기거나, `CheckoutService`가 전체를 한 단위로 감싸도록. (실서비스 신뢰성 직결)
2. **domain 파싱 책임 이관**: `OptionGroup.parse_selection`의 문자열 해석을 interface/application으로 올리고, 도메인은 `validate`만 남기기.
3. **검증 상수 단일화**: 수량 한도 등 중복된 규칙을 도메인 상수로 통일.
4. **방어적 타입검사 정리**: 신뢰 경계 밖만 남기고 내부 협력 코드의 `isinstance` 축소.
5. **테스트 헬퍼 공용화**: `create_menu`류 팩토리를 `conftest.py`로 승격.
6. **계층별 동사 분리**: `checkout` 3중 명명을 층별로 구분.
