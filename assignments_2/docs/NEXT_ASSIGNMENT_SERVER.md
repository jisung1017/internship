# 다음 과제: 키오스크 서버화 (FastAPI + ORM)

> 선행 문서: [PROGRESS_EVALUATION.md](./PROGRESS_EVALUATION.md)
> 대상: 인턴 · 형태: 기존 코어 위에 서버 계층 추가 (재작성 아님)

---

## 0. 한 줄 목표

견고하게 만든 **domain을 그대로 재사용**하면서, **꼬여 있는 application 레이어를 먼저 펴고**, 전달 계층을 CLI에서 **HTTP 서버(FastAPI)로 교체**한다. 더불어 raw SQL을 **ORM**으로 바꾸고 **Entity ↔ DTO ↔ ORM** 경계를 명확히 설계한다.

> **중요:** domain은 손대지 않는다. 하지만 **application은 손댄다** — route를 얹으려면 application부터 재정렬해야 한다(§1). "코어 재사용"이란 *도메인 규칙*을 재사용한다는 뜻이지, 지금의 application 구조를 그대로 둔다는 뜻이 아니다.

---

## 1. 선행 작업 ⭐: application 레이어 분해 (`KioskSession` 해체)

> **이 단계를 끝내기 전에는 FastAPI를 시작하지 말 것.** 지금 route가 안 들어가는 건 route 문제가 아니라 application이 CLI 전용으로 꼬여 있어서다. 여기가 이번 과제의 진짜 관문이다.

### 1.1 문제 진단 — `KioskSession`이 두 고도(altitude)를 한 몸에 담고 있다

`KioskSession`은 잘못 만든 게 **아니다.** 단일 사용자 CLI에서는 "1 프로세스 = 1 세션 = 인메모리 상태"가 완벽히 맞는 모델이었다. 문제는 **서로 다른 성격의 두 가지를 한 객체에 섞었다**는 점이고, 이게 전달수단을 무상태 HTTP로 바꾸는 순간 드러난다.

| `KioskSession`이 하는 일 | 정체 | 서버화하면 |
|--------------------------|------|------------|
| `add_to_cart`, `checkout` 등 조율 | **유스케이스** (application 핵심) | ✅ 살린다 → 무상태 서비스로 승격 |
| `step`(StepType), 화면 전이 | **화면 흐름** (CLI 전용 상태) | ❌ 버린다 → 흐름은 클라이언트가 주도 |
| `cart`, `pending_order` 인메모리 보관 | **상호작용 상태** (조립 중 워크플로우) | 🔄 외부화 → DB/세션스토어로 이전 |

즉 `KioskSession`을 **삭제**하는 게 아니라 **분해**한다: **재사용 가능한 유스케이스**는 위로 추출하고, **전달수단에 묶인 상태**는 밖으로 뺀다.

### 1.2 목표 구조 — 무상태 유스케이스 서비스

`KioskSession`에 route를 얹으려 하지 말고, **무상태 application 서비스**를 만들어 **CLI와 route가 둘 다 그것을 호출**하게 한다.

```
[현재]  CLI → KioskSession(상태ful: 화면흐름 + 유스케이스 + 상태 뒤섞임) → OrderService/CheckoutService

[목표]  CLI  ─┐
              ├→  application 유스케이스 서비스(무상태) → domain + repository
        Route ─┘        add_item() / view_cart() / checkout() / restock()
```

- 유스케이스 서비스의 각 메서드는 **"입력 → 로드 → 도메인 호출 → 저장 → 결과 반환"** 형태의 **무상태 함수**다. 인스턴스 필드에 cart/step을 들고 있지 않는다.
- cart 같은 상호작용 상태는 **`cart_id`로 저장소에서 매 요청 로드**한다. 전역/인메모리 단일 상태 금지.
- `step`(화면 전이)은 **CLI 어댑터 안으로 격리**하거나 버린다. route는 리소스 지향(`POST /carts/{id}/items`)이라 step 머신이 필요 없다.

**Before / After 스케치:**
```python
# ❌ 현재: 상태와 유스케이스가 세션에 묶여 있어 route가 붙을 진입점이 없음
class KioskSession:
    cart: Cart              # 인메모리 단일 상태
    step: StepType          # 화면 흐름 (CLI 전용)
    pending_order: PendingOrder | None
    def select_quantity(self, q): ...   # 유스케이스 + 화면전이 + 상태변경이 뒤섞임

# ✅ 목표: 무상태 유스케이스. cart를 밖에서 로드해 넘기고, 결과만 돌려줌
class CartService:
    def __init__(self, carts: CartRepository, ...): ...
    def add_item(self, cart_id, menu_id, quantity, options) -> CartView:
        cart = self.carts.load(cart_id)     # 저장소에서 로드
        ...                                  # 도메인 규칙 호출 (조율 = 여기서)
        self.carts.save(cart)                # 저장
        return CartView.from_domain(cart)    # 결과 반환
```

### 1.3 `pending_order`는 버리지 말고 승격시킨다

평가에서 칭찬한 `PendingOrder`("조립 중 주문") 개념은 좋은 설계다. 서버에서는 이게 **draft cart / 미확정 주문 리소스**로 자연스럽게 승격된다 — **개념은 그대로 살리고, 저장 위치만 메모리 → DB로** 바꾼다.

### 1.4 이번 분해로 함께 해소되는 것 (이전 평가 연계)

유스케이스를 한 군데로 모으면 아래가 **자동으로 정리**된다:
- `checkout` 3중 동명 메서드(session/service/orderservice) → 유스케이스 하나로 수렴, 층별로 다른 동사(`place_order` 등)로 명명.
- `cart.clear()` 부작용이 성공/실패 분기에 흩어진 문제 → 유스케이스가 cart 생명주기를 단일 소유.
- 결제 원자성 틈(메모리 재고 차감 후 DB 커밋 실패 시 불일치) → 소비·영속화를 하나의 원자적 유스케이스로.
- `KioskAdminService.restock`의 `order_service.inventory.restock(...)` 데메터 위반 → application에서 올바르게 중계.

---

## 2. 요구사항 (서버 계층)

### 2.1 FastAPI 서버
- 기존 `interface/cli.py`는 **삭제하지 말고 유지**한다. 같은 application 유스케이스가 CLI와 HTTP 두 어댑터를 동시에 지탱한다는 걸 증명하는 대조군이다. (§1을 제대로 했다면 CLI는 얇은 어댑터로 살아남는다.)
- 새 어댑터를 `interface/api/` 아래에 추가한다.
  ```
  interface/
    cli.py                  # 유지 (§1 이후 얇아진 형태)
    api/
      main.py               # FastAPI app 인스턴스, DI 조립(Composition Root)
      routers/              # cart, order, admin 등 리소스별 라우터
      schemas.py            # 요청/응답 DTO (Pydantic)
      dependencies.py       # 유스케이스 서비스 주입
  ```
- 라우터는 **얇게**: HTTP 파싱 → DTO 변환 → application 유스케이스 호출 → 응답 DTO 반환. **라우터 안에 비즈니스 로직·조율 금지.**

### 2.2 무상태 + 리소스 지향
- §1.2에서 만든 무상태 유스케이스 위에 리소스 엔드포인트를 얹는다.
  - 예: `POST /carts` → `POST /carts/{id}/items` → `POST /orders`
- 상태는 서버 저장소(DB 또는 세션 테이블)에 두고 **요청마다 재구성**한다. 전역 인메모리 상태 금지.

### 2.3 raw SQL → ORM
- 현재 `infrastructure/repositories/Postgres*`의 raw SQL을 **ORM(SQLAlchemy 2.0 권장)** 으로 교체한다.
- 단, **repository의 공개 인터페이스(application의 `Protocol`)는 바뀌지 않아야 한다.** ORM은 infra 내부 구현 세부사항이다. application은 ORM을 몰라야 한다.
- **ORM 모델 클래스가 도메인 객체를 대체하지 않는다.** ORM 모델(테이블 매핑)과 도메인 엔티티는 별개다(2.4 참고).

### 2.4 Entity ↔ DTO ↔ ORM 모델 3층 분리
세 종류의 "데이터 모양"을 의도적으로 구분한다:

| 종류 | 위치 | 역할 | 예 |
|------|------|------|-----|
| **도메인 엔티티/VO** | `domain/` | 비즈니스 규칙·불변식 소유 | `Order`, `Money`, `Inventory` |
| **DTO (스키마)** | `interface/api/schemas.py` | HTTP 요청/응답 직렬화 계약 | `AddCartItemRequest`, `OrderResponse` |
| **ORM 모델** | `infrastructure/` | DB 테이블 매핑 | `OrderTable`, `InventoryItemTable` |

**데이터 흐름 (조회):**
```
DB → [infra] ORM 모델 로드 → 도메인 Entity 변환 → [application] 유스케이스 → DTO 변환 → [route] 반환
```
**데이터 흐름 (쓰기): 거울상**
```
[route] DTO 파싱 → [application] Entity 재구성·규칙 → [infra] ORM 모델 변환 → DB 저장
```
- **경계에서 명시적으로 변환**한다. 도메인 객체를 그대로 JSON으로 내보내거나 ORM 모델을 라우터까지 흘려보내지 않는다.
- 변환 책임 위치: **DTO ↔ 도메인 = application** / **도메인 ↔ ORM 모델 = infra repository 안**
- 규칙: infra는 Entity만 위로 내보낸다(ORM 모델은 repository 안에서 죽는다). application은 DTO만 위로 내보낸다(Entity는 route로 안 나간다). route는 DTO만 만진다.

---

## 3. ⭐ 핵심 설계 규칙 (반드시 준수 — 평가 최우선)

> **객체(도메인) 간 메시지 조율은 오직 `application` 계층에서만 한다. `infrastructure` 계층은 서로 다른 객체의 데이터를 조회·조율하지 않는다.**

### 왜?
`infrastructure`는 **DB 접근(영속화) 계층**이다. 한 repository가 다른 객체의 DB를 조회하거나 여러 도메인 객체의 협력을 지휘하기 시작하면:
- 비즈니스 흐름(누가 누구에게 무슨 메시지를 보내는가)이 DB 계층으로 새어나가고,
- 트랜잭션·SQL 관심사와 도메인 조율 관심사가 뒤섞여 계층 경계가 무너진다.

**하나의 repository는 자기 aggregate 하나의 영속화만 책임진다.** 여러 aggregate를 엮는 유스케이스는 application 서비스가 지휘한다.

### 🚫 나쁜 예 (infra가 다른 객체를 조율)
```python
# infrastructure/repositories/postgres_order_repository.py
class PostgresOrderRepository:
    def save(self, order):
        # 🚫 주문 저장하면서 재고 repository를 직접 불러 재고까지 조율 → 규칙 위반
        inventory = PostgresInventoryRepository(self._conn).load()
        inventory.consume(order)
        PostgresInventoryRepository(self._conn).save(inventory)
        self._insert_order(order)
```

### ✅ 좋은 예 (application이 조율, infra는 각자 저장만)
```python
# application/checkout_service.py  ← 조율은 여기서
class CheckoutService:
    def checkout(self, cart):
        order = self.order_service.place_order(cart)   # 도메인 규칙
        with self.unit_of_work as uow:                 # 트랜잭션 경계만 infra가 제공
            uow.orders.save(order)                     # 자기 것만
            uow.inventory.save(self.order_service.inventory)  # 자기 것만
        return order
```

```python
# infrastructure/repositories/postgres_order_repository.py
class PostgresOrderRepository:
    def save(self, order):
        # ✅ 오직 order 테이블만. 다른 aggregate를 모른다.
        ...
```

### 트랜잭션 처리에 대한 주의 (함정)
- "여러 저장을 하나의 트랜잭션으로 묶는 것"과 "여러 객체의 메시지를 조율하는 것"은 다르다.
- **트랜잭션 경계(Unit of Work)는 infra가 제공하는 *메커니즘***이다. 하지만 "무엇을 어떤 순서로 저장/소비할지 결정"하는 **조율은 application의 책임**이다.
- 현재 `PostgresOrderPersister.persist`가 order+inventory 저장을 한 트랜잭션으로 묶는데, 이 안에서 **저장 대상·순서를 결정하는 조율 로직이 infra로 내려가지 않도록** Unit of Work 패턴으로 리팩터링한다. infra는 "이 두 개를 한 트랜잭션으로 커밋하라"는 기계적 실행만.

---

## 4. 진행 단계 (권장 순서)

1. **application 유스케이스 분해 (§1)** — `KioskSession`에서 무상태 유스케이스 서비스를 추출하고, 상태를 외부화한다. **route보다 먼저.** 기존 CLI가 새 유스케이스 서비스 위에서 그대로 도는지 테스트로 확인(코어 재사용 1차 증명).
2. **경계 설계** — 어떤 리소스/엔드포인트, 어떤 DTO, 어떤 상태를 서버가 보관할지 문서로 스케치.
3. **ORM 모델 + repository 교체** — Protocol은 고정한 채 내부만 SQLAlchemy로. 기존 infra 테스트가 그대로 통과하는지 확인(계약 불변 증명).
4. **Unit of Work 도입** — 트랜잭션 조율을 application으로 끌어올림(§3 함정 해소).
5. **FastAPI 라우터 + DTO** — 얇은 어댑터로 무상태 유스케이스 호출.
6. **무상태 세션 마무리** — 인메모리 상태 완전 제거, 다중 클라이언트 동작 확인.
7. **CLI가 여전히 도는지 확인** — 코어 재사용의 최종 증거.

---

## 5. 평가 기준

| 항목 | 확인 포인트 |
|------|-------------|
| **application 분해 (선행)** | 유스케이스가 무상태 서비스로 추출됐는가? CLI/route가 같은 서비스를 호출하는가? 화면 상태(step)가 어댑터 밖으로 안 새는가? |
| **계층 규칙 (최우선)** | infra repository가 자기 aggregate만 저장하는가? 객체 간 조율이 application에만 있는가? |
| **TDD 유지** | 서버 계층·유스케이스에도 test→feat 리듬이 이어지는가? |
| **domain 불변** | 도메인 규칙을 거의 안 건드리고 재사용했는가? |
| **Entity/DTO/ORM 분리** | 세 모델이 경계에서 명시적으로 변환되는가? 도메인/ORM 객체가 라우터로 새지 않는가? |
| **무상태성** | 전역 인메모리 상태 없이 다중 클라이언트가 동작하는가? |
| **원자성** | 결제 유스케이스가 하나의 원자적 단위인가? |

---

## 6. 금지 사항 / 흔한 실수

- ❌ §1을 건너뛰고 `KioskSession`에 route를 바로 얹기 (더 꼬인다)
- ❌ 처음부터 재작성 (도메인 재사용이 이 과제의 핵심)
- ❌ 라우터 안에 비즈니스 로직·조율
- ❌ 유스케이스 서비스가 상태(cart/step)를 인스턴스 필드로 보관
- ❌ infra repository가 다른 repository/aggregate를 조회·조율 (§3 위반)
- ❌ ORM 모델을 도메인 엔티티로 겸용 (규칙 검증 로직이 테이블 매핑에 섞임)
- ❌ 도메인 객체/ORM 객체를 그대로 HTTP 응답으로 직렬화
- ❌ application이 SQLAlchemy import (ORM은 infra 세부사항)

---

## 7. 제출물

1. 동작하는 FastAPI 서버 + 유지된 CLI (둘 다 같은 유스케이스 서비스 위에서 동작)
2. §4-2의 설계 스케치 문서 (엔드포인트/DTO/상태 표)
3. `KioskSession` 분해 전/후 구조를 스스로 서술한 짧은 회고 + 계층 규칙 준수 근거 (`docs/`에 1p)

---

*질문·막힘은 두 가지 질문으로 판단할 것: (1) "이건 유스케이스인가, 화면 흐름인가?" → 계층이 결정됨. (2) "이 로직이 조율인가, 단순 저장인가?" → application이냐 infra냐가 결정됨.*
