# 🗄️ DB 연동 안내서 (PostgreSQL + 원시 SQL)

> 이 문서는 지금까지 **메모리(dict)** 로 관리하던 데이터를 **PostgreSQL** 로 옮기기 위한 학습용 안내서입니다.
> ORM 없이 **원시 SQL** 을 직접 작성하며, "SQL / 트랜잭션 / 행 잠금" 을 손으로 경험하는 것이 목표입니다.

---

## 🎯 이번 단계의 목표

1. 프로그램을 껐다 켜도 **재고가 유지**되게 만든다. (지금은 매번 초기값으로 리셋됨)
2. **식별자(id)를 의미 없는 UUID 로 바꾼다.** 지금은 `'bean'`, `'americano'` 같은 의미 있는 값을 id 로 쓰는데, 이건 안티패턴이라 이번에 바로잡는다. (→ [0단계](#0단계-식별자-설계-원칙-먼저-읽기) 참고)
3. DB를 아는 코드(SQL)는 새로운 `infrastructure` 계층에만 둔다. 도메인은 **id 의미 변경을 제외하면** 거의 손대지 않는다.
4. `checkout` 의 "재고 확인 → 결제 → 재고 차감" 원자성을 **DB 트랜잭션**으로 보장한다.
5. 여러 주문이 동시에 들어올 때의 **재고 경쟁(race condition)** 을 `SELECT ... FOR UPDATE` 로 막아본다.

> 💡 **왜 재고(Inventory)부터?**
> 메뉴/재료는 잘 안 바뀌는 "읽기 위주" 데이터지만, **재고는 결제할 때마다 바뀌는 유일한 가변 상태**입니다.
> DB 연동의 진짜 학습 포인트(트랜잭션·잠금)가 전부 여기 몰려 있으니 재고부터 시작합니다.
> 메뉴/재료/옵션은 그다음에 같은 패턴으로 확장하면 됩니다.

---

## 🧱 핵심 개념: Repository 패턴

지금 구조를 다시 보면:

```
main.py  ──> create_inventory()  # environment 계층에서 "메모리 dict" 로 재고를 만든다
         └─> OrderService(payment, inventory)
```

`OrderService` 는 `Inventory` 객체가 **어디서 왔는지 모릅니다.** 그냥 받아서 씁니다.
바로 이 점 덕분에 1차 DB 연동에서는 핵심 도메인 로직을 거의 바꾸지 않아도 됩니다.
다만 주문 단위 트랜잭션과 동시성까지 적용하는 단계에서는, Application 계층에 "최신 재고 조회 → 주문 처리 → 저장" 흐름을 조율하는 코드가 추가됩니다.

우리가 할 일은 `create_inventory()` 자리에 **DB에서 재고를 읽고/쓰는 객체(Repository)** 를 끼워 넣는 것뿐입니다.

```
main.py  ──> InventoryRepository(db)         # infrastructure 계층 (SQL 실행)
         │      .load()  -> Inventory        # DB row -> 도메인 객체로 조립
         │      .save(inventory)             # 도메인 객체 -> DB 반영
         └─> OrderService(payment, inventory)
```

> **Repository** = "도메인 객체를 저장/조회해주는 창구". 도메인은 SQL을 모르고, SQL은 도메인 규칙(음수 방지 등)을 모릅니다. 각자 할 일만 합니다.

---

## 🏗️ 바뀌는 폴더 구조

```
src/
├── domain/          # (변경 없음) 순수 비즈니스 로직
├── application/     # (변경 없음) OrderService
├── environment/     # (유지) 초기 시드 데이터 정의
├── interface/       # (변경 없음) CLI
├── infrastructure/  # 🆕 DB 연결 + Repository (SQL 여기에만!)
│   ├── db.py                # 커넥션 생성/관리
│   └── inventory_repository.py
└── main.py          # 조립 지점만 수정 (create_inventory -> repository.load)

migrations/          # 🆕 SQL 스키마 파일
└── 001_init.sql
docker-compose.yml   # 🆕 (선택) Docker로 띄울 때만 필요 — 직접 설치하면 불필요
```

> ✅ 핵심: DB를 아는 코드(SQL)는 **`infrastructure/` 에만** 둡니다. 도메인은 SQL을 절대 모릅니다.

---

## 0단계. 식별자 설계 원칙 (먼저 읽기)

DB를 붙이기 전에, 이 프로젝트의 **가장 중요한 설계 결정** 부터 바로잡습니다.

### 문제: 지금은 "의미 있는 값"을 식별자로 쓴다

```python
# environment/ingredients.py
Ingredient(name="원두", id=IngredientId("bean"))   # id 가 사람이 읽는 의미('bean')

# environment/menus.py — 레시피가 'bean' 이라는 문자열로 재료를 참조
"recipe": [("bean", 18), ("water", 250), ("cup", 1)]
```

의미 있는 값을 식별자로 쓰는 것이 항상 잘못은 아닙니다. 하지만 이 프로젝트의 `'bean'`, `'americano'`, `'hot'` 같은 값은 이름·시드 키·영구 식별자의 역할이 섞여 있어 변경에 취약합니다. 이런 구조에서는 다음 문제가 생길 수 있습니다:

- 재료 이름/코드를 바꾸고 싶으면 → 그 id 를 참조하던 **레시피·메뉴·옵션·재고·DB FK 를 전부** 같이 고쳐야 함
- 하나라도 놓치면 → 조용히 참조가 깨지거나 잘못된 재료가 차감됨
- "id 는 곧 이름" 이라는 착각 때문에, 이름은 원래 **바뀔 수 있는 값** 인데 식별자로 굳어버림

### 이 프로젝트에서 사용할 원칙: 내부 조인은 정수 PK, 외부 식별은 UUID, 이름은 그냥 속성

식별자를 **두 종류로 분리** 하면 각 역할을 명확히 나눌 수 있습니다. 이 프로젝트에서는 아래 방식을 사용합니다.

| 컬럼               | 역할                                               | 노출 범위                      | 바뀌나                        | 예                       |
| ------------------ | -------------------------------------------------- | ------------------------------ | ----------------------------- | ------------------------ |
| **id (BIGINT PK)** | DB **내부** 조인·FK 전용 대리키                    | DB 안에서만 (도메인엔 노출 ❌) | ❌                            | `1`, `2`, `3`            |
| **uuid (UUID)**    | **외부에 노출되는 식별자** (도메인의 IngredientId) | 도메인·API·로그                | ❌                            | `550e8400-e29b-41d4-...` |
| **name**           | 화면에 보여줄 이름                                 | 표시용                         | ⭕ `"원두"`→`"콜롬비아 원두"` |
| **code** (선택)    | 시드/임포트 때 사람이 읽는 라벨                    | 시드 스크립트 안에서만         | ⭕                            | `"bean"`                 |

- **정수 `id`**: 테이블끼리 조인할 때 쓰는 내부 키. 정수라 인덱스/조인이 빠르고, **DB 밖으로는 절대 안 나감.**
- **`uuid`**: 도메인·API·외부 시스템이 이 재료를 가리킬 때 쓰는 **안정적인 공개 식별자.** 도메인의 `IngredientId` 가 바로 이 값.
- 왜 둘 다? → 정수 PK 를 그대로 외부에 노출하면 순번이 드러나고(`1,2,3...` 추측 가능), 외부 시스템과 식별자를 공유하기도 불편합니다. 그래서 이 프로젝트에서는 **내부는 정수, 외부는 UUID** 로 나눕니다.
- 비교·외부 식별은 **오직 `uuid`로**, 테이블 내부 FK 조인은 **정수 `id`로**. `name`/`code` 로는 절대 식별하지 않는다.
- `code`('bean')는 남겨도 되지만 **오직 시드 데이터를 사람이 읽고 엮기 위한 용도** 일 뿐, 런타임 식별에는 절대 쓰지 않는다.

> ⚠️ 이건 DB만의 문제가 아니라 **도메인 코드의 문제** 라, DB를 붙이는 김에 도메인 id 의미부터 바꿉니다.
> 아래 **『도메인 코드 바꾸기: id → UUID』** 절에 바꿔야 할 곳을 하나도 빠짐없이 정리했습니다.

---

## 1단계. 로컬 PostgreSQL 띄우기

두 가지 방법 중 하나를 고르면 됩니다. **처음이라면 방법 A(직접 설치)** 를 권합니다 — pgAdmin(그래픽 도구)까지 같이 깔려서 DB를 눈으로 보기 좋습니다. Docker를 써보고 싶으면 방법 B(표준 방식)

### 방법 A. 직접 설치 (기본 · 권장) — Windows

1. `https://www.postgresql.org/download/windows/` 에서 **EDB 설치 프로그램** 다운로드
2. 실행 → 버전 17 선택. 설치 도중 **superuser(`postgres`) 비밀번호** 를 정합니다 (꼭 기억!)
3. 포트는 기본값 `5432` 그대로 진행
4. 설치가 끝나면 Postgres가 **Windows 서비스로 자동 등록** 되어 부팅 시 알아서 켜집니다
   (수동 제어는 `services.msc` → `postgresql-x64-17` 시작/중지)

> winget 을 쓰면 명령 한 줄로도 설치됩니다: `winget install PostgreSQL.PostgreSQL.17`

설치 후 DB 생성 — 시작 메뉴의 **SQL Shell (psql)** 실행 (또는 PowerShell에서 `psql -U postgres`):

```sql
CREATE DATABASE cafe;
\q
```

접속 문자열(나중에 코드에서 사용):

```
postgresql://postgres:<설치때_정한_비번>@localhost:5432/cafe
```

### 방법 B. Docker (대안)

Docker Desktop이 설치돼 있다면 `docker-compose.yml` 을 프로젝트 루트에 만듭니다.

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: cafe
      POSTGRES_PASSWORD: cafe
      POSTGRES_DB: cafe
    ports:
      - "5432:5432"
    volumes:
      - cafe_pgdata:/var/lib/postgresql/data

volumes:
  cafe_pgdata:
```

```bash
docker compose up -d      # 백그라운드로 DB 실행
docker compose ps         # 잘 떴는지 확인
docker compose down       # 끌 때 (데이터는 volume 에 유지됨)
```

접속 문자열: `postgresql://cafe:cafe@localhost:5432/cafe`

> 방법 A와 B는 **사용자/비밀번호/DB 이름만 다를 뿐** 이후 단계는 완전히 동일합니다. 자신이 고른 쪽의 접속 문자열을 4단계에서 사용하세요.

---

## 2단계. 스키마 설계 (`migrations/001_init.sql`)

도메인 모델을 테이블로 옮깁니다. 지금은 재고에 집중합니다.

```sql
-- 재료 (Ingredient)
CREATE TABLE ingredient (
    id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- 내부 조인용 정수 PK (DB 밖으로 안 나감)
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),   -- 외부 식별자 = 도메인의 IngredientId
    name TEXT NOT NULL,                                    -- 화면 표시용 이름 (언제든 바뀔 수 있음)
    code TEXT UNIQUE                                       -- (선택) 시드/임포트 전용 라벨. 식별에는 안 씀
);

-- 재고 (InventoryItem): 재료별 현재 수량
CREATE TABLE inventory_item (
    ingredient_id BIGINT PRIMARY KEY REFERENCES ingredient(id),  -- FK 는 정수 id 로 조인 (빠름)
    quantity      INTEGER NOT NULL CHECK (quantity >= 0)  -- Quantity 의 '음수 불가' 규칙을 DB에서도 강제
);
```

> 💡 **관찰 포인트 ①** — 정수 PK + UUID 2중 구조 (0단계의 결론)
>
> - `id`(정수): **테이블 내부 조인·FK 전용.** `inventory_item.ingredient_id` 가 이걸 참조합니다. 빠르고 DB 밖으로 안 나감.
> - `uuid`: **외부에 노출되는 식별자.** 도메인의 `IngredientId` 는 이 UUID 를 담습니다.
> - 즉 **DB 안에서 행을 이을 땐 정수 `id`, 도메인/외부가 재료를 가리킬 땐 `uuid`.** 역할이 분리돼요.
> - 이름(`name`)을 바꿔도 `id`·`uuid` 둘 다 그대로라 참조가 안 깨집니다. `name`/`code` 로는 식별하지 않습니다.
> - (`gen_random_uuid()` 는 PostgreSQL 13+ 기본 제공 — 별도 확장 불필요)
>
> 💡 **관찰 포인트 ②**: 도메인의 `Quantity(음수 불가)` 규칙을 DB `CHECK (quantity >= 0)` 로도 한 번 더 건다는 점.
> 검증은 도메인에서 하지만, DB도 최후의 방어선을 갖는 게 실무 습관입니다.

적용 — **방법 A(직접 설치)**:

```powershell
psql -U postgres -d cafe -f migrations\001_init.sql
```

**방법 B(Docker)**:

```bash
docker compose exec -T db psql -U cafe -d cafe < migrations/001_init.sql
```

초기 시드 데이터는 기존 `environment/inventory_data.py` 의 값을 그대로 `INSERT` 로 옮겨 넣습니다.
정수 `id` 와 `uuid` 는 DB가 자동 생성하므로 `code`/`name` 만 넣고, 재고는 `code` 로 재료를 찾아 **정수 FK(`id`)로** 연결합니다:

```sql
INSERT INTO ingredient (code, name) VALUES
    ('bean', '원두'), ('water', '물'), ('milk', '우유'), ('cup', '컵'), ('syrup', '시럽');

INSERT INTO inventory_item (ingredient_id, quantity)
SELECT ingredient.id, q.quantity          -- 정수 PK 를 FK 로 연결
FROM ingredient
JOIN (VALUES
    ('bean', 1000), ('water', 5000), ('milk', 3000), ('cup', 100), ('syrup', 1000)
) AS q(code, quantity) ON q.code = ingredient.code;
```

---

## 3단계. 드라이버 추가

```bash
uv add "psycopg[binary]"
```

`pyproject.toml` 의 `dependencies` 에 `psycopg` 가 추가됩니다.

---

## 4단계. DB 연결 (`src/infrastructure/db.py`)

```python
import os
import psycopg

def connect() -> psycopg.Connection:
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError(
            "DATABASE_URL 환경변수가 없습니다. PostgreSQL 접속 문자열을 설정해 주세요."
        )
    return psycopg.connect(dsn)
```

> 접속 정보를 코드에 하드코딩하지 말고 **환경변수**로 빼는 습관을 들이세요. (`DATABASE_URL`)
>
> PowerShell 예시:
>
> ```powershell
> $env:DATABASE_URL="postgresql://postgres:설치때_정한_비밀번호@localhost:5432/cafe"
> uv run python -m src.main
> ```

---

## 5단계. Repository 구현 (`src/infrastructure/inventory_repository.py`)

여기서 **SQL row ↔ 도메인 객체 변환**이 일어납니다. 두 개의 메서드부터 시작하세요.

```python
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.ingredient import Ingredient
from src.domain.id import IngredientId
from src.domain.quantity import Quantity


class InventoryRepository:
    def __init__(self, conn):
        self._conn = conn

    def load(self) -> Inventory:
        """DB의 재고 전체를 읽어 도메인 Inventory 객체로 조립한다."""
        # 테이블 조인은 내부 정수 id 로. 도메인에 넘길 식별자는 uuid 로.
        sql = """
            SELECT i.uuid, i.name, s.quantity
            FROM inventory_item s
            JOIN ingredient i ON i.id = s.ingredient_id   -- 내부 조인: 정수 id
        """
        with self._conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        items = [
            InventoryItem(
                Ingredient(name=name, id=IngredientId(str(ingredient_uuid))),  # 외부 식별자: uuid
                Quantity(quantity),
            )
            for (ingredient_uuid, name, quantity) in rows
        ]
        return Inventory.from_items(items)

    def save(self, inventory: Inventory) -> None:
        """도메인 Inventory 의 현재 수량을 DB에 반영한다."""
        # 도메인은 uuid 만 안다. uuid 로 재료의 정수 id 를 찾아 그 행을 갱신한다.
        sql = """
            UPDATE inventory_item
            SET quantity = %s
            WHERE ingredient_id = (
                SELECT id FROM ingredient WHERE uuid = %s::uuid
            )
        """
        with self._conn.cursor() as cur:
            for ingredient_id, item in inventory.items.items():
                cur.execute(sql, (item.quantity.value, ingredient_id.value))
                if cur.rowcount != 1:
                    raise RuntimeError(
                        f"재고를 찾을 수 없습니다: {ingredient_id.value}"
                    )

        # commit 하지 않는다.
        # 트랜잭션의 시작/커밋/롤백은 이 메서드를 호출하는 상위 코드가 관리한다.
```

> 💡 **관찰 포인트**: `load()` 가 하는 일은 "SQL 결과 → `Ingredient`/`InventoryItem`/`Quantity` 로 다시 포장" 입니다.
> DB는 값(uuid, text, int)만 알지 도메인 규칙을 모릅니다. **경계에서 도메인 객체로 되살리는 것**이 Repository의 핵심 역할이에요.
> 정수 `id` 는 SQL 조인 안에서만 쓰이고 **도메인엔 uuid 만 넘어갑니다.** `code`/`name` 은 비교에 전혀 관여하지 않습니다.
>
> Repository는 SQL 실행만 담당하고, `commit()`이나 `rollback()`은 하지 않습니다. 여러 작업을 하나로 묶어야 하므로 트랜잭션 경계는 Application 계층에서 관리합니다.

> ⚠️ **여기서 반드시 짚을 함정** (0단계와 직결):
> `Inventory.consume(recipe)` 는 레시피 속 재료 id 와 재고 속 재료 id 를 **비교해서** 차감합니다.
> 그런데 재고는 이제 DB의 UUID 를 쓰는데, **메뉴/레시피(`menus.py`)는 여전히 `IngredientId('bean')` 를 쓰면 id 가 서로 달라 차감이 실패합니다.**
> → 그래서 **재료를 만드는 곳(`create_ingredients()`)이 DB의 UUID 를 유일한 출처로 삼아야** 하고,
> 메뉴/레시피는 그 재료 객체(=DB UUID를 가진)를 재사용해야 합니다. 다음 절 체크리스트에서 정리합니다.

---

## 도메인 코드 바꾸기: id → UUID (빠짐없이 고칠 곳)

0단계 원칙을 실제 코드에 반영합니다. **의미 있는 값을 식별자로 쓰던 모든 지점** 을 찾아 바꿉니다.
아래가 그 전체 목록이에요 — 하나라도 놓치면 "재고 차감이 조용히 실패" 하는 버그가 납니다.

### ① `IngredientId` 의 의미를 바꾼다 (`src/domain/id.py`)

지금은 `Id.value` 가 "사람이 정한 문자열"이지만, 이제 **UUID 문자열** 을 담습니다. 형식 검증을 넣어두면 실수를 빨리 잡습니다.

```python
import uuid

@dataclass(frozen=True)
class IngredientId(Id):
    def __post_init__(self):
        super().__post_init__()
        uuid.UUID(self.value)   # UUID 형식이 아니면 여기서 즉시 에러 → 의미 있는 값 유입 차단
```

> `MenuId`, `OptionId` 도 나중에 같은 방식으로 UUID화하면 됩니다. (이번엔 재고 흐름과 직결된 `IngredientId` 부터)

### ② `Ingredient` 가 id 를 이름에서 만들지 않게 한다 (`src/domain/ingredient.py`)

현재 `id` 가 없으면 `IngredientId(self.name)` 로 **이름에서 id 를 만드는데, 이게 바로 안티패턴** 입니다.
id 는 반드시 **밖에서 주입** 받도록 바꿉니다. (이름과 id 의 연결고리를 끊는 것이 핵심)

```python
# 변경 전 (이름으로 id 생성 — 제거 대상)
if self.id is None:
    object.__setattr__(self, "id", IngredientId(self.name))

# 변경 후: id 는 필수 인자. 이름으로 만들지 않는다.
if not isinstance(self.id, IngredientId):
    raise TypeError("Ingredient 는 IngredientId(UUID) 를 반드시 받아야 합니다.")
```

### ③ 재료의 **유일한 출처를 DB로** 만든다 (`src/environment/ingredients.py`)

여기가 가장 중요합니다. 지금은 `IngredientId('bean')` 로 재료를 만들지만,
**재고와 레시피가 같은 UUID 를 공유해야** `Inventory.consume` 이 동작합니다.
따라서 재료를 코드가 지어내지 말고 **DB에서 읽어와** 반환하게 바꿉니다. (`code` 는 오직 dict 키 = 시드 연결용)

```python
def load_ingredients(conn) -> dict[str, Ingredient]:
    """code -> Ingredient(uuid 식별자) 매핑. code 는 코드 안에서 재료를 엮기 위한 편의 키일 뿐."""
    with conn.cursor() as cur:
        cur.execute("SELECT uuid, name, code FROM ingredient")   # 정수 id 는 꺼내지 않는다 (내부용)
        rows = cur.fetchall()
    return {
        code: Ingredient(name=name, id=IngredientId(str(ingredient_uuid)))
        for (ingredient_uuid, name, code) in rows
    }
```

### ④ 메뉴/레시피가 그 재료를 재사용하게 한다 (`src/environment/menus.py`)

`create_menu()` 가 `create_ingredients()` 대신 **③에서 DB로 읽어온 재료 dict** 를 받아 쓰게 바꿉니다.
`_build_recipe(items, ingredients)` 에서 `ingredients["bean"]` 로 꺼내는 코드는 **그대로 둬도 됩니다** —
`"bean"` 은 이제 "식별자"가 아니라 "시드 데이터를 엮는 로컬 키" 일 뿐이니까요. 꺼내진 `Ingredient` 의 식별자(`IngredientId`)는 DB의 `uuid` 값입니다.

```python
def create_menu(ingredients: dict[str, Ingredient]) -> list[Menu]:   # ingredients 를 주입받도록 변경
    option_groups = {...}   # 내부 로직은 그대로, ingredients 만 밖에서 받는다
    ...
```

> 💡 **핵심 통찰**: `'bean'` 이라는 문자열은 두 가지 역할을 **혼동** 하고 있었습니다 —
> (1) 영구 식별자, (2) 시드 데이터를 코드에서 엮는 임시 키. 이번 변경으로 (1)은 UUID 가 가져가고,
> (2)만 `'bean'` 이 담당합니다. **런타임 비교/저장은 전부 UUID**, `'bean'` 은 시드 조립 순간에만 존재.

### ⑤ 시드 UUID 는 고정하는 걸 권장

`gen_random_uuid()` 는 매번 다른 값을 만들어, DB를 다시 시드하면 UUID 가 바뀝니다.
학습/재현성을 위해 **시드에서는 UUID 를 고정** 하는 방법도 있습니다 (선택):

```sql
-- 정수 id 는 DB 가 자동 채번하고, 외부 식별자 uuid 만 고정한다
INSERT INTO ingredient (uuid, code, name) VALUES
    ('11111111-1111-1111-1111-111111111111', 'bean', '원두'),
    ('22222222-2222-2222-2222-222222222222', 'water', '물');
    -- ...
```

> 실무에선 보통 DB가 UUID 를 생성(`gen_random_uuid()`)하게 두지만, 여기선 시드가 소수라 고정하면 디버깅이 편합니다.

### ✅ 이 변경으로 얻는 것

- 재료 이름을 `"원두"` → `"콜롬비아 원두"` 로 바꿔도 **식별자(uuid)와 내부 PK(id)는 그대로** → 레시피·재고·주문 참조가 **하나도 안 깨짐**
- "이름=식별자" 라는 잘못된 가정이 사라져, 이름은 자유롭게 바뀌는 속성이 됨
- 도메인 객체의 비교와 외부 식별은 UUID로 통일하고, DB 테이블 사이의 FK와 조인은 정수 `id`를 사용 → 각 식별자의 역할이 명확해짐

---

## 6단계. 조립 지점 수정 (`src/main.py`)

`create_inventory()` 를 Repository 로 교체하고, 재료를 DB에서 읽어 메뉴에 주입합니다.

```python
from src.infrastructure.db import connect
from src.infrastructure.inventory_repository import InventoryRepository
from src.environment.ingredients import load_ingredients   # create_ingredients 대체
from src.environment.menus import create_menu               # 이제 ingredients 를 인자로 받음

def main() -> None:
    with connect() as conn:
        # 재료를 DB에서 한 번만 읽어(= UUID의 유일한 출처), 메뉴와 재고가 같은 재료 UUID를 공유하게 한다.
        ingredients = load_ingredients(conn)       # ③ code -> Ingredient(UUID)
        menus = create_menu(ingredients)           # ④ 같은 재료 객체를 메뉴/레시피에 주입

        inventory_repo = InventoryRepository(conn)
        inventory = inventory_repo.load()          # ← DB에서 읽어옴 (동일한 UUID)

        payment = Payment(balance=Money(10000))
        order_service = OrderService(payment, inventory)

        CLI(menus, order_service, payment).run()

        # 임시 방식: 프로그램이 정상 종료될 때 한 번 저장
        inventory_repo.save(inventory)
        conn.commit()
```

이 시점에서 실행해 보세요. **껐다 켜도 재고가 유지**되면 1차 목표 달성입니다.

> ⚠️ 이 방식은 학습을 위한 임시 단계입니다. 프로그램이 주문 중간에 종료되면 메모리 상태와 DB 상태가 어긋날 수 있고, 여러 키오스크가 동시에 주문하면 안전하지 않습니다. 다음 단계에서 주문 1건마다 트랜잭션을 적용합니다.

---

## 7단계. (심화) 트랜잭션으로 원자성 지키기

지금 6단계 방식은 문제가 있습니다: 프로그램이 중간에 죽으면 `save` 가 안 되어 재고가 안 맞습니다.
**결제 1건마다 트랜잭션으로 묶는 것**이 정석입니다. `checkout` 흐름을 이렇게 바꿔보세요.

```python
def checkout_and_persist(conn, inventory_repo, order_service, cart):
    with conn.transaction():
        order = order_service.checkout(cart)
        inventory_repo.save(order_service.inventory)
        return order
    # 블록 안의 DB 작업 중 예외가 나면 자동 ROLLBACK
    # 정상 종료되면 자동 COMMIT
```

> **관찰 포인트**: `conn.transaction()`이 자동으로 되돌리는 것은 **DB 안에서 실행된 변경뿐**입니다.
> 메모리의 `Inventory`, 메모리의 결제 잔액, 외부 결제 API의 승인 결과는 자동으로 원복되지 않습니다.
> 이번 단계에서는 DB 재고 저장의 원자성에 집중합니다. 실제 결제 연동에서는 결제 승인 시점, 결제 취소, 실패 보상 같은 별도 설계가 필요합니다.

---

## 8단계. (심화) 동시성 — 행 잠금 `SELECT ... FOR UPDATE`

키오스크 2대가 마지막 남은 컵 1개를 동시에 결제한다고 가정해봅시다.
두 프로그램이 시작할 때 재고를 한 번만 읽고 계속 사용하면, 둘 다 오래된 메모리 값을 보고 "재고 있음"이라고 판단할 수 있습니다.

따라서 잠금만 추가하는 것으로는 부족합니다. **주문 트랜잭션이 시작될 때 최신 재고를 DB에서 다시 읽고**, 그 행을 잠근 상태에서 재고 확인과 저장을 끝내야 합니다.

```sql
SELECT i.uuid, i.name, s.quantity
FROM inventory_item s
JOIN ingredient i ON i.id = s.ingredient_id
WHERE i.uuid = ANY(%s)
ORDER BY i.id
FOR UPDATE OF s;
```

- `FOR UPDATE OF s`: 선택한 재고 행을 현재 트랜잭션이 끝날 때까지 잠급니다.
- `ORDER BY i.id`: 여러 재료를 잠글 때 항상 같은 순서로 잠가 교착상태 위험을 줄입니다.
- 잠근 뒤 읽은 최신 수량으로 `Inventory`를 만들어야 합니다. 프로그램 시작 시 읽은 오래된 `Inventory`를 그대로 사용하면 안 됩니다.

Application 계층의 흐름은 다음처럼 바뀝니다.

```python
def checkout_and_persist(conn, inventory_repo, payment, cart):
    with conn.transaction():
        # 1. 주문에 필요한 재고를 잠그면서 최신 값으로 읽는다.
        inventory = inventory_repo.load_for_update(cart)

        # 2. 최신 재고를 사용해 주문을 처리한다.
        order_service = OrderService(payment, inventory)
        order = order_service.checkout(cart)

        # 3. 같은 트랜잭션 안에서 변경된 재고를 저장한다.
        inventory_repo.save(inventory)
        return order
```

첫 번째 키오스크가 행을 잠그면 두 번째 키오스크는 첫 번째 트랜잭션이 끝날 때까지 기다립니다.
첫 번째 트랜잭션이 커밋된 뒤 두 번째 키오스크는 줄어든 최신 재고를 읽고 정확하게 재고 부족을 판단합니다.

> ⚠️ 현재 `save()`처럼 메모리의 전체 재고를 다시 저장하는 방식은 학습용입니다.
> 반드시 같은 트랜잭션 안에서 최신 값을 잠가 읽은 경우에만 안전합니다. 실무에서는 변경된 재료만 저장하거나, `quantity = quantity - %s` 형태로 DB에서 직접 차감하는 방식도 자주 사용합니다.

> 이 부분은 실제로 두 개의 커넥션을 열어 재현해보면 "잠금 → 대기 → 커밋 후 진행"이 눈으로 보여서 학습 효과가 큽니다.

---

## ✅ 권장 진행 순서 (TDD 유지)

이 프로젝트의 원칙(테스트 먼저)을 DB 연동에도 적용합니다.

1. **DB 띄우기** → `psql` 로 접속되는지 확인 (1단계)
2. **스키마 + 시드**(UUID) 작성 및 적용 (2단계)
3. **도메인 id 를 UUID 로** 바꾸기 (『도메인 코드 바꾸기』 절 ①~④)
   - `IngredientId` UUID 검증, `Ingredient` id 주입 강제, `load_ingredients`, `create_menu(ingredients)`
   - 기존 도메인 단위 테스트가 여전히 통과하도록 테스트의 id 도 UUID 로 맞춘다
4. `InventoryRepository.load()` 부터 **테스트 작성** → 구현 (5단계)
   - 테스트 DB에 시드를 넣고, `load()` 결과가 기대한 `Inventory` 인지 검증
5. `save()` 테스트 → 구현
6. `main.py` 배선 후 실제 실행으로 "재고 유지" + "재고 차감 정상" 확인 (6단계)
7. `save()`의 `commit()`을 제거하고 Application 계층에서 주문 단위 트랜잭션 적용 (7단계)
8. 주문 시점에 최신 재고를 다시 읽고 행 잠금 적용 (8단계)

> ⚠️ **테스트 격리 주의**: DB 테스트는 매 테스트마다 트랜잭션을 열고 끝나면 롤백하거나, 별도 테스트 스키마를 쓰세요.
> `pytest` fixture 로 "테스트 전 시드 → 테스트 후 정리" 를 자동화하면 깔끔합니다.

---

## 📌 흔한 함정 체크리스트

- [ ] `name`·`code` 로 엔티티를 비교/조회했다면 → **식별은 UUID 로만.** 의미 있는 값으로 식별하지 않는다.
- [ ] 재고는 UUID, 메뉴/레시피는 아직 `'bean'` 이라면 → id 불일치로 **재고 차감이 조용히 실패.** 재료 출처를 DB 하나로 통일(③).
- [ ] `Ingredient` 가 이름에서 id 를 만들고 있다면(`IngredientId(self.name)`) → 아직 안 고침. id 는 반드시 주입.
- [ ] SQL 을 `f-string` 으로 조립했다면 → **SQL 인젝션**. 반드시 `%s` 파라미터 바인딩 사용.
- [ ] Repository 안에서 `commit()` 했다면 → 여러 작업을 하나의 트랜잭션으로 묶기 어려움. 커밋/롤백은 Application 계층에서 관리.
- [ ] 커넥션을 닫지 않았다면 → 누수. `with connect() as conn:` 또는 종료 시 `conn.close()`.
- [ ] 접속 정보를 코드에 하드코딩했다면 → 환경변수(`DATABASE_URL`)로.
- [ ] 주문할 때 프로그램 시작 시 읽은 재고를 그대로 쓴다면 → 오래된 값일 수 있음. 트랜잭션 안에서 최신 재고를 다시 조회.
- [ ] `UPDATE` 후 `rowcount`를 확인하지 않았다면 → 존재하지 않는 UUID가 조용히 무시될 수 있음.

---

## 🔜 다음 단계 (이 문서 이후)

- 메뉴 / 재료 / 옵션 / 레시피도 DB로 이관 (읽기 위주라 트랜잭션 부담은 적음)
- 주문(Order) 이력을 DB에 기록 → "오늘 판매 내역" 조회 기능
- 같은 `InventoryRepository` **인터페이스**를 SQLAlchemy 로 재구현 → "도메인 안 바꾸고 저장소만 교체" 체감
