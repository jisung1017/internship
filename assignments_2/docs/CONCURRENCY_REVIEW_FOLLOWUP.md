# 동시성 수정 검토 — 고쳐졌나, 그리고 무엇이 새로 깨졌나

> 대상: `CONCURRENCY_REVIEW.md`(기준 커밋 `0f71a6e`) 지적사항에 대한 수정 결과
> 검토 범위: `0f71a6e..b41bbed` (PR #34 `fix/concurrency` 머지 포함, 19개 커밋)
> 검증 방법: 코드 대조 + 전체 테스트 실행(PostgreSQL) + 재고 이력 저장 동작 재현

---

## 0. 한 줄 요약

**핵심 동시성 결함(문제 1·2·3)은 정확하게 해결됐다.** 다만 **부가 작업(멱등성·재고 이력)에서 기능을 파괴하는 회귀 2건이 새로 들어왔다.**

| 구분 | 결과 |
|------|------|
| 동시성 결함 (문제 1~4, 7.3, 7.4) | ✅ 전부 해결 |
| 테스트 | ✅ 208건 + 동시성 4건 전부 통과 |
| 신규 회귀 | 🔴 2건 — 키오스크당 주문 1건 제한, 재고 이력 유실 |
| 신규 성능 저하 | 🔴 1건 — 락 구간 내 이력 전체 조회 |
| 부분 해결 | 🟡 3건 — 테스트 DB, 멱등성 경합, save 범위 검증 |

---

## 1. ✅ 제대로 고쳐진 것

| 원 항목 | 상태 | 수정 내용 |
|---------|------|-----------|
| **문제 1** 취소 시 락 없는 전체 덮어쓰기 | ✅ | `kiosk_admin_service.py:117` → `load_for_update(ingredient_names)`. `load() + save()` 조합이 코드베이스에서 완전히 사라짐 |
| **문제 2** 동일 주문 중복 취소 (TOCTOU) | ✅ | `find_by_id_for_update()` 추가 (`orm_order_repository.py:65`) |
| **문제 3** `place_order(inventory=...)` 락 우회 | ✅ | 파라미터 제거, `cli.py:295` 호출부도 함께 정리 |
| **문제 4** `save()` 전체 덮어쓰기 | ✅ (a안) | `_locked_ingredient_names`로 락 범위 밖 재료 저장 시 예외 |
| **7.3** advisory lock 키 충돌 | ✅ | `pg_advisory_xact_lock(1000, :id)` 2-인자 형태로 네임스페이스 분리 |
| **7.4** 락 대상 없으면 조용히 통과 | ✅ | 요청 재료 수 ≠ 조회 수이면 예외. 중복 이름 제거(`set`)도 함께 처리 |
| **7.6** 재고 부족 응답 코드 | ✅ | 라우터·앱 핸들러 양쪽 409. 데코레이터 스택도 별도 함수로 올바르게 분리 |
| **회귀 테스트** | ✅ | 취소×주문 혼합, 동일 주문 중복 취소 2종 추가 |

### 특히 잘 된 부분

**`find_by_id_for_update`의 로더 선택이 정확하다.**

```python
query = (
    self._session.query(OrderModel)
    .filter(OrderModel.id == order_id)
    .options(selectinload(OrderModel.items).selectinload(OrderItemModel.options))
)
if not is_sqlite:
    query = query.with_for_update(of=OrderModel)
```

기존 `find_by_id`가 쓰던 `joinedload`를 그대로 뒀다면 PostgreSQL에서 `FOR UPDATE cannot be applied to the nullable side of an outer join` 에러가 났을 것이다. `selectinload`로 바꾼 것은 의도적이고 올바른 판단이다. `of=OrderModel`로 잠금 대상을 주문 행으로 한정한 것도 맞다.

**데드락 경로도 새로 생기지 않았다.** 취소는 `주문 행 락 → 재료 advisory 락` 순, 주문은 `재료 advisory 락 → INSERT` 순이다. 주문 경로가 기존 주문 행을 잠그지 않으므로 순환 대기가 성립하지 않는다.

### 검증 결과

```
tests/ (동시성 제외)      208 passed
tests/test_concurrency.py   4 passed   (PostgreSQL)
```

추가된 두 시나리오가 실제로 통과한다 — 문제 1과 2는 재현 테스트로 방어된다.

---

## 2. 🔴 회귀 1 — `x-kiosk-uuid`를 `order_uuid`로 사용했다 (최우선)

**위치:** `src/interface/api/routers/kiosk.py:47`

```python
order = order_service.place_order_from_dto(
    items_dto=request.items,
    order_uuid=x_kiosk_uuid,   # ← 단말 식별자를 주문 UUID로
)
```

`x-kiosk-uuid`는 헤더 설명 그대로 **"클라이언트 키오스크 UUID"**, 즉 단말마다 고정된 값이다. 이걸 주문 UUID로 넘기면 멱등성 검사(`order_application_service.py:47-54`)에 그대로 걸린다.

```python
if order_uuid is not None:
    exisiting_record = self.uow.orders.find_by_uuid(order_uuid)
    if exisiting_record:
        return Order(items=cart.items, id=..., order_uuid=...)   # 조기 반환
```

### 결과

**같은 키오스크의 두 번째 주문부터는 영원히 첫 주문이 반환된다.**

```
1번 주문  → 정상 접수
2번 주문  → 201 응답 + 첫 주문 UUID 반환, 주문 미생성, 재고 미차감
3번 주문  → 동일
```

응답은 201에 "주문이 성공적으로 접수되었습니다"인데 아무 일도 일어나지 않는다. 게다가 반환되는 `total_price`는 **저장된 주문이 아니라 이번 요청 장바구니** 기준이라 금액까지 어긋난다.

### 원 리뷰의 의도

7.1이 요청한 것은 **요청마다 새로 생성되는 `Idempotency-Key`** 다. 단말 식별자와 요청 식별자는 다른 개념이다.

### 수정

```python
def create_order(
    request: CreateOrderRequest,
    response: Response,
    x_kiosk_uuid: Annotated[UUID, Header(...)],
    idempotency_key: Annotated[UUID | None, Header(alias="Idempotency-Key")] = None,
    ...
):
    order = order_service.place_order_from_dto(
        items_dto=request.items,
        idempotency_key=idempotency_key,
    )
```

`customer_order`에 `idempotency_key` 컬럼을 추가하고 유니크 제약을 건다. `order_uuid`는 서버가 생성하는 주문 식별자로 되돌린다.

> ⚠️ API 테스트에 **성공하는 주문 생성 케이스가 하나도 없다.** 208건이 통과했는데도 이 회귀가 잡히지 않은 이유다. 수정과 함께 반드시 추가해야 한다.

---

## 3. 🔴 회귀 2 — 재고 이력이 첫 트랜잭션 것만 저장된다

**위치:** `src/infrastructure/repositories/orm_inventory_repository.py:119-124`, `:153`

```python
# load_for_update()
histories = self._load_histories()
inventory = Inventory(items=items)          # ← history 를 비운 채 생성
inventory._locked_ingredient_names = set(unique_names)
inventory._saved_history_count = len(histories)   # ← 그런데 DB 전체 이력 개수를 넣는다
```

```python
# save()
new_histories = inventory.history[inventory._saved_history_count:]
```

`history`는 비어 있는데 오프셋은 DB 전체 이력 개수다. 소비/복구로 `history`에 N건이 쌓여도 `history[전체개수:]`는 **항상 빈 리스트**다.

### 재현

sqlite 인메모리 DB에 `load_for_update` → `restock` → `save` → `commit`을 3회 반복:

```
round 0: 이력 테이블 1건
round 1: 이력 테이블 1건    ← 증가하지 않음
round 2: 이력 테이블 1건
```

첫 트랜잭션에서만 DB 이력이 0건이라 오프셋이 0이 되어 우연히 저장된다. 그 이후로는 단 한 건도 남지 않는다.

### 왜 위험한가

7.2를 넣은 이유가 **"동시성 사고는 사후 추적이 생명"** 이었다. 지금 상태는 이력 테이블이 존재하고 코드도 있으니 추적이 되고 있다고 착각하기 쉬운데, 실제로는 첫 한 건 이후 아무것도 쌓이지 않는다. **이력이 아예 없는 것보다 나쁘다.**

### 수정

`load_for_update`는 이력을 읽을 이유가 없다. 새로 쌓인 것만 세면 된다.

```python
inventory = Inventory(items=items)
inventory._locked_ingredient_names = set(unique_names)
inventory._saved_history_count = 0    # 이 인스턴스의 history 는 비어 있으므로 0
```

`_load_histories()` 호출 자체를 제거한다(→ 4번과 함께 해결된다).

---

## 4. 🔴 회귀 3 — 이력 전체 조회가 락 구간과 메뉴 조회에 들어갔다

**위치:** `orm_inventory_repository.py:19` `_load_histories()`

```python
hist_models = (
    self._session.query(InventoryHistoryModel)
    .join(InventoryHistoryModel.ingredient)
    .order_by(InventoryHistoryModel.id.asc())
    .all()                                    # ← 필터 없음. 전 이력을 읽는다
)
```

이 메서드가 `load()`(`:57`)와 `load_for_update()`(`:119`) **양쪽에서 매번** 호출된다.

| 호출 경로 | 영향 |
|-----------|------|
| `load_for_update()` | **advisory lock을 쥔 상태에서** 무한히 커지는 테이블을 풀스캔한다. 주문·취소가 쌓일수록 락 유지 시간이 선형으로 늘어난다 |
| `load()` | 메뉴 목록 API(`order_application_service.py:40`)마다 전 이력을 읽는다. 재고 판정에 이력은 쓰이지도 않는다 |

원 리뷰 §6은 "**락 구간의 DB 왕복을 줄이라**"고 했는데, 정확히 반대 방향의 변경이 들어갔다. 이력이 10만 건 쌓인 시점에 주문 폭주가 오면 문제 5(직렬화)가 그대로 증폭된다.

### 수정

이력은 `save()`가 INSERT할 때만 필요하다. **읽기 경로에서 전부 제거한다.** 조회용 이력이 필요해지면 별도 조회 메서드(기간·재료 필터 + 페이징)로 분리한다.

---

## 5. 🟡 부분 해결 / 남은 것

### 5.1 테스트가 여전히 개발 DB를 지운다 (원 7.5)

**위치:** `tests/test_concurrency.py:17`

```python
db_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
...
Base.metadata.drop_all(bind=engine)
```

환경변수 우선 적용은 됐지만, **미설정 시 여전히 로컬 개발 DB(`kiosk`)를 `drop_all`** 한다. 개발자가 무심코 `pytest`를 돌리면 로컬 데이터가 날아간다.

→ 전용 테스트 DB URL을 요구하고, 미설정 시 `pytest.skip`으로 빠지게 하는 편이 안전하다.

### 5.2 멱등성 검사 자체에 경합이 남아 있다

`order_application_service.py:48` `find_by_uuid` 조회 후 INSERT — **검사와 사용 사이가 비어 있는 전형적인 TOCTOU**다. 문제 2와 구조가 같다.

동시 재시도 2건이 모두 조회를 통과하면 둘 다 INSERT를 시도하고, `order_uuid` 유니크 제약에 걸린 쪽은 `IntegrityError`가 그대로 올라가 **500**이 된다. 멱등성이 필요했던 상황(네트워크 타임아웃 재시도)에서 정확히 터진다.

```python
try:
    ...
    self.uow.commit()
except IntegrityError:
    self.uow.rollback()
    existing = self.uow.orders.find_by_uuid(key)   # 경쟁에서 진 쪽은 기존 주문 반환
    return existing
```

유니크 제약을 최종 방어선으로 삼고, 위반을 잡아 기존 주문으로 수렴시키는 형태가 맞다.

### 5.3 `save()` 범위 검증에 한쪽 구멍이 남아 있다

**위치:** `orm_inventory_repository.py:127`

```python
locked_names = getattr(inventory, "_locked_ingredient_names", None)
for item in inventory.items:
    if locked_names is not None and item.ingredient.name not in locked_names:
        raise ValueError(...)
```

`load()`로 만든 `Inventory`는 `_locked_ingredient_names`가 `None`이라 **검증이 통째로 건너뛰어진다.** 지금은 `load() + save()` 호출자가 없어서 드러나지 않지만, 문제 1이 재발하는 경로 자체는 그대로 열려 있다.

→ `None`일 때를 "검증 면제"가 아니라 "락 없이 저장 시도 = 예외"로 뒤집는 편이 원래 의도에 맞다.

### 5.4 sqlite 분기는 동시성을 검증하지 못한다

`load_for_update`와 `find_by_id_for_update` 모두 `dialect.name == "sqlite"`이면 락을 건너뛴다.

```python
if not is_sqlite:
    self._session.execute(text("SELECT pg_advisory_xact_lock(1000, :id)"), ...)
```

동시성 테스트가 PostgreSQL로 돌고 있으므로 현재는 문제가 없다. 다만 **sqlite 기반 테스트로는 동시성을 절대 검증할 수 없다**는 점이 코드에 명시돼 있지 않다. 주석이나 테스트 가드로 남겨두는 편이 좋다.

### 5.5 원 리뷰에서 미착수 (우선순위 5 — 예상된 범위)

- **커넥션 풀 ↔ 스레드풀 불일치** — 여전히 15 vs 40 (`dependencies.py:22`)
- **주문마다 전체 메뉴 조회** — `place_order_from_dto`의 `get_all_menus()` 그대로

정확성 확보가 우선이었으므로 이번 라운드에서 빠진 것은 타당하다.

---

## 6. 수정 우선순위

| 순위 | 항목 | 이유 |
|------|------|------|
| **1** | 회귀 1 — `Idempotency-Key` 분리 | 지금 프로덕션에 올라가면 키오스크당 주문이 1건만 접수된다 |
| **1** | 성공 주문 API 테스트 추가 | 이 회귀를 208건 중 아무도 잡지 못했다 |
| **2** | 회귀 2·3 — `_load_histories` 읽기 경로에서 제거 | 한 번의 수정으로 이력 유실과 락 구간 풀스캔이 동시에 해결된다 |
| **3** | 멱등성 `IntegrityError` 처리 (5.2) | 멱등성이 실제로 필요한 순간에 500이 난다 |
| **4** | 테스트 DB 분리 강제 (5.1) | 개발 데이터 유실 방지 |
| 5 | `save()` 범위 검증 뒤집기 (5.3) | 구조적 방어의 완성 |
| 6 | 성능 (5.5) | 정확성 확보 후 |

### 테스트 보강

- **주문 생성 성공 경로 API 테스트** — 201 응답, `Location` 헤더, 실제 재고 차감까지 확인
- **동일 `Idempotency-Key` 재요청** — 주문이 1건만 생성되고 재고도 1회만 차감되는지 (순차 + 동시 양쪽)
- **서로 다른 요청, 동일 `x-kiosk-uuid`** — 주문이 2건 생성되는지 (회귀 1 재발 방지)
- **재고 이력 누적** — 주문·취소를 N회 반복한 뒤 이력 행 수가 N에 비례하는지 (회귀 2 재발 방지)
