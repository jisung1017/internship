# 동시성 제어 리뷰 — 주문이 몰릴 때 재고는 정확한가

> 대상 브랜치: `fix/connection` (기준 커밋 `2f6ffea`)
> 검증 방법: 코드 리뷰 + 별도 테스트 DB(`kiosk_conc`)에 실제 부하를 걸어 재현
> 검증 대상: `OrderApplicationService.place_order`, `KioskAdminService.restock` / `update_order_status`, `OrmInventoryRepository`

---

## 0. 한 줄 요약

**주문 경로의 동시성 제어는 정확하게 동작한다.** 반면 **주문 취소(재고 복구) 경로에는 락이 없어 동시 주문의 재고 차감이 조용히 유실된다.**

| # | 항목 | 상태 | 영향 |
|---|------|------|------|
| — | 주문 폭주 시 재고 차감 | ✅ 정상 | 초과 판매 0건, 재고 음수 0건 |
| 1 | 취소가 동시 주문의 차감을 덮어씀 | ❌ 결함 | **초과 판매**, 무음 데이터 오염 |
| 2 | 동일 주문 중복 취소 | ❌ 결함 | 재고 과다 복구 (1번 수정 시 표면화) |
| 3 | `place_order(inventory=...)` 락 우회 | ❌ 결함 | CLI 경유 시 1번과 동일한 유실 |
| 4 | `save()`의 전체 덮어쓰기 | ⚠️ 구조 | 1·3번의 근본 원인 |
| 5 | 공통 재료 락에 의한 전 주문 직렬화 | ⚠️ 성능 | 동시성 40배에 처리량 1.5배 |
| 6 | 주문 API 멱등성 부재 | ⚠️ 결함 | 재시도/더블클릭 시 중복 주문 |
| 7 | 재고 이력 미저장 | ⚠️ 운영 | 사고 발생 시 사후 추적 불가 |

---

## 1. ✅ 잘 된 부분 — 주문 경로

`src/infrastructure/repositories/orm_inventory_repository.py:38` `load_for_update()`의 설계는 옳다.

```python
# 1. 락을 잡을 원재료 ID 조회 및 오름차순 정렬 (Lock Ordering)
ing_models = (... .order_by(IngredientModel.id.asc()).all())

# 2. PostgreSQL Advisory Lock 획득
for (ing_id,) in ing_models:
    self._session.execute(text("SELECT pg_advisory_xact_lock(:id)"), {"id": ing_id})

# 3. 락을 획득한 상태에서 최신 재고 수량 조회
```

세 가지가 모두 맞게 되어 있다.

1. **잠근 다음에 읽는다.** 읽고 나서 잠그면 이미 낡은 값을 손에 쥔 상태라 의미가 없다. 순서가 정확하다.
2. **락 획득 순서를 ID 오름차순으로 고정했다.** 서로 다른 재료 집합을 쓰는 주문끼리 엇갈려 잠그는 데드락을 구조적으로 차단한다.
3. **트랜잭션 경계가 맞다.** `pg_advisory_xact_lock`은 commit/rollback 시 자동 해제되고, 락 → 재고 확인 → 결제 → 차감 → 주문 저장 → commit이 전부 `place_order`의 단일 `with self.uow:` 블록 안에 있다 (`src/application/order_application_service.py:56-72`). 락 누수가 발생할 경로가 없다.

### 검증 결과

원두 90g(아메리카노 5잔 분량)에 **20건 동시 주문**:

```
성공 = 5건    실패(품절) = 15건    최종 원두 = 0g
```

초과 판매 없음, 재고 음수 없음, 정확히 소진. **이 경로는 통과다.**

---

## 2. ❌ 문제 1 — 주문 취소가 동시 주문의 차감을 덮어쓴다 (최우선)

**위치:** `src/application/kiosk_admin_service.py:109` `_restore_inventory_for_order()`

```python
inventory = self.uow.inventories.load()   # ← 락 없음. 게다가 전체 재고를 읽는다
for _, (ingredient, total_qty) in restore_map.items():
    inventory.restock(ingredient, Quantity(total_qty), reason="CANCEL")
self.uow.inventories.save(inventory)      # ← 전체 재고를 통째로 UPDATE
```

주문 경로는 `load_for_update()`로 **필요한 재료만 잠그고 그 재료만** 쓴다. 그런데 취소 경로는 **락 없이 전체 재고를 읽어 전체를 덮어쓴다.** 읽은 시점과 쓰는 시점 사이에 커밋된 모든 주문의 차감이 사라진다. 복구 대상 재료뿐 아니라 **그 주문과 아무 상관 없는 전 재료**가 함께 오염된다.

### 재현

취소 30건과 라떼 주문 30건을 동시에 실행하고, 동일 작업의 순차 실행 결과와 비교:

```
재료      동시 실행    순차 기준    차이
우유       -6000       -6000       ✅
물          -620        -900       ❌ +280   ← 차감 280 유실
원두        -504        -540       ❌  +36   ← 차감 36 유실

예외 0건, 불일치 재료 2종
```

### 왜 위험한가

**예외 없이 조용히 틀린다.** 실제로는 팔렸는데 장부상 재고는 줄지 않은 상태가 된다.

```
장부 재고 > 실물 재고  →  없는 재료로 주문을 받는다  →  초과 판매
```

취소가 잦을수록 오차가 누적되고, 로그에도 흔적이 남지 않는다.

### 수정

```python
inventory = self.uow.inventories.load_for_update(list(restore_map.keys()))
```

`load_for_update()`는 이미 ID 오름차순 락 순서를 보장하므로 주문 경로와 맞물려도 데드락이 나지 않는다. `_restore_inventory_for_order`는 `update_order_status`의 `with self.uow:` 블록 안에서 호출되고 commit도 그 안에서 일어나므로, 락의 획득·해제 범위도 그대로 맞는다.

---

## 3. ❌ 문제 2 — 같은 주문을 동시에 여러 번 취소할 수 있다

**위치:** `src/application/kiosk_admin_service.py:60-71` `update_order_status()`

```python
order_record = self.uow.orders.find_by_id(order_id)      # 락 없는 조회
if order_record.status == OrderStatus.CANCEL:            # 검사(Check)
    raise ValueError("이미 취소된 주문은 ...")
...
self._restore_inventory_for_order(order_record)          # 사용(Use)
```

검사와 사용 사이에 락이 없는 전형적인 **TOCTOU(Time-of-check to time-of-use)**다. 동일 주문에 취소 요청 4건을 동시에 넣으면 **4건 모두 검사를 통과하고 예외는 0건**이다.

> ⚠️ **문제 1과 반드시 함께 고쳐야 한다.**
> 지금 재고 숫자가 우연히 맞아 보이는 것은, 문제 1의 전체 덮어쓰기가 중복 복구를 서로 지워주기 때문이다. 문제 1만 고치면 **재고가 4배로 복구되는 버그로 성격이 바뀐다.**

### 수정 (택1)

**(a) 주문 행을 잠근다**

```python
order_record = self.uow.orders.find_by_id_for_update(order_id)  # SELECT ... FOR UPDATE
```

**(b) 조건부 UPDATE로 만든다**

```sql
UPDATE customer_order SET status = :new WHERE id = :id AND status != 'CANCEL'
```

영향 행 수가 0이면 이미 다른 요청이 취소했다는 뜻이므로 중단한다.

---

## 4. ❌ 문제 3 — `place_order(inventory=...)`가 락을 우회한다

**위치:** `src/application/order_application_service.py:60-63`

```python
current_inventory = (
    inventory                                              # ← 락 없이 그대로 사용
    if inventory is not None
    else self.uow.inventories.load_for_update(ingredient_names)
)
```

그리고 이 경로를 실제로 타는 곳이 있다 — `src/interface/cli.py:295`

```python
self.order_app_service.place_order(self.cart, self.payment, self.inventory)
```

CLI가 오래 들고 있던 **메모리상 재고 스냅샷**이 락도, 최신 읽기도 없이 그대로 `save()`로 전체 덮어쓰기된다. API와 CLI가 같은 DB를 바라보는 순간 문제 1과 동일한 유실이 발생한다.

**수정:** `inventory` 파라미터를 제거한다. 테스트에서 재고를 주입해야 한다면 Fake UoW로 대체한다(이미 `tests/test_acceptance.py`에 패턴이 있다).

---

## 5. ⚠️ 문제 4 — `save()`의 전체 덮어쓰기 (1·3번의 근본 원인)

**위치:** `src/infrastructure/repositories/orm_inventory_repository.py:81`

```python
def save(self, inventory: Inventory) -> None:
    for item in inventory.items:      # 넘겨받은 모든 item을
        ...
        model.quantity = item.quantity.value   # 절대값으로 덮어쓴다
```

**"잠근 범위 = 읽은 범위 = 쓰는 범위"** 라는 불변식이 코드 어디에도 강제되어 있지 않다. 이 셋이 어긋나는 순간(문제 1·3) 곧바로 유실이 된다. 두 가지 방어 중 하나를 권한다.

| 방법 | 내용 | 효과 |
|------|------|------|
| **(a) 범위 검증** | `load_for_update`가 잠근 재료 목록을 `Inventory`에 기록해 두고, `save()`가 그 범위 밖 재료를 쓰려 하면 예외 | 같은 실수가 런타임에 즉시 드러남 |
| **(b) 상대 UPDATE** | 절대값 대신 `quantity = quantity - :delta` | 덮어쓰기 자체가 성립하지 않음 |

---

## 6. ⚠️ 문제 5 — 공통 재료 락으로 사실상 모든 주문이 직렬화된다

거의 모든 메뉴가 `물`·`테이크아웃 컵`·`얼음`을 공유한다. 따라서 서로 다른 메뉴의 주문이라도 **공통 재료 락에서 전부 줄을 선다.**

동일 재고 조건에서 주문 40건 처리:

| 동시 스레드 | 소요 | 처리량 | p50 | p95 |
|------------|------|--------|-----|-----|
| 1 | 0.78s | 51.2 TPS | 19ms | 24ms |
| 40 | 0.53s | 75.5 TPS | **338ms** | **486ms** |

동시성을 40배 올렸는데 처리량은 1.5배, 지연은 **20배**다. 정확성을 위한 대가로 현재 규모에서는 감수할 만하지만, 다음 단계는 다음과 같다.

- **락 구간의 DB 왕복 줄이기** — `save()`가 재료마다 `SELECT`를 한 번씩 더 돈다. 재료 수만큼 쿼리가 늘어나 락 유지 시간이 그만큼 길어진다.
- **주문마다 전체 메뉴를 조회하지 않기** — `place_order_from_dto`가 주문 1건마다 `get_all_menus()`로 전체 메뉴를 별도 트랜잭션에서 읽는다(`src/application/order_application_service.py:78`). 락 밖이라 정확성 문제는 아니지만 주문 폭주 시 순수한 낭비다.
- **커넥션 풀과 스레드풀 맞추기** — 엔진이 기본값(`src/interface/api/dependencies.py:22`, 5 + overflow 10 = **15**)인데 FastAPI의 동기 엔드포인트 스레드풀은 **40**이다. 락을 기다리는 스레드가 커넥션을 쥔 채 대기하므로, 부하가 더 오르면 풀 고갈로 30초 타임아웃이 난다.

---

## 7. ⚠️ 그 밖에

### 7.1 주문 API에 멱등성이 없다

`src/interface/api/routers/kiosk.py:41`에서 `x-kiosk-uuid`를 헤더로 받지만 응답에 되돌려 줄 뿐 중복 방지에 쓰지 않는다. 키오스크에서 더블클릭하거나 네트워크 타임아웃으로 재시도하면 **주문 2건 + 재고 2번 차감**이다. 실전 키오스크에서는 동시성 못지않게 자주 터진다.

→ `Idempotency-Key` 헤더를 받아 유니크 제약으로 막는다.

### 7.2 재고 이력이 저장되지 않는다

도메인은 `CONSUME` / `RESTOCK` / `CANCEL` 이력을 성실히 쌓지만(`src/domain/inventory.py:39` `_record`), 대응하는 테이블도 `save()`의 저장 로직도 없어 commit과 함께 버려진다. **동시성 사고는 사후 추적이 생명인데 지금은 추적할 근거가 없다.**

### 7.3 advisory lock 키 충돌 여지

`pg_advisory_xact_lock(ing_id)`의 단일 인자 형태는 DB 전역 단일 네임스페이스를 쓴다. 나중에 다른 용도로 advisory lock을 도입하면 ID가 겹친다. 2-인자 형태 `pg_advisory_xact_lock(classid, objid)`로 네임스페이스를 분리해 두면 안전하다.

### 7.4 락 대상이 없으면 조용히 통과한다

`orm_inventory_repository.py:47-58` — `ingredient_names`가 DB에 없으면 락을 하나도 잡지 않고 그대로 진행한다. 조회된 락 대상 수가 요청한 재료 수와 다르면 예외를 던지는 편이 안전하다.

### 7.5 테스트가 DB URL을 하드코딩한다

`tests/test_concurrency.py:18`이 `DEFAULT_DATABASE_URL`을 직접 쓰고 `drop_all`을 건다. `DATABASE_URL` 환경변수를 무시하므로 CI 설정과 무관하게 **항상 로컬 기본 DB를 지운다.**

### 7.6 재고 부족은 409가 적절하다

현재 `400 Bad Request`로 응답한다. 클라이언트가 "잘못된 요청"과 "지금은 품절"을 구분해 재시도 여부를 판단할 수 있도록 `409 Conflict`가 맞다.

---

## 8. 수정 우선순위

| 순위 | 항목 | 이유 |
|------|------|------|
| **1** | 문제 1 + 2 **함께** | 지금 조용히 데이터가 틀어지고 있다. 하나만 고치면 다른 쪽이 표면화된다 |
| **2** | 문제 3 | 락을 우회하는 경로 자체를 없앤다 |
| **3** | 문제 4 | 같은 실수가 재발하지 않도록 구조로 막는다 |
| 4 | 멱등성(7.1), 재고 이력(7.2) | 운영 안정성과 사후 추적 |
| 5 | 성능(문제 5) | 정확성을 확보한 뒤에 다룬다 |

### 회귀 테스트 보강

현재 `tests/test_concurrency.py`는 **주문 경로만** 검증한다. 그래서 문제 1이 테스트를 통과해 버린다. 다음 시나리오를 추가해야 한다.

- **취소 × 주문 혼합** — 취소 N건과 주문 M건을 동시에 실행하고, 동일 작업의 순차 실행 결과와 재료별 delta를 비교한다 (문제 1)
- **동일 주문 중복 취소** — 같은 주문에 취소 요청 K건을 동시에 넣고, 복구량이 정확히 1회분인지 확인한다 (문제 2)
