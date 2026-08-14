BEGIN;

-- ============================================================
-- Ingredient
-- ============================================================

INSERT INTO ingredient (name, unit)
VALUES
    ('원두', 'g'),
    ('물', 'ml'),
    ('우유', 'ml'),
    ('컵', '개'),
    ('시럽', 'ml');

-- ============================================================
-- Inventory
-- ============================================================

INSERT INTO inventory (ingredient_id, quantity)
SELECT
    ingredient.id,
    v.quantity
FROM ingredient
JOIN (
    VALUES
        ('원두', 12345),
        ('물', 500000),
        ('우유', 300000),
        ('컵', 10000),
        ('시럽', 100000)
) AS v(name, quantity)
    ON v.name = ingredient.name;

-- ============================================================
-- Menu
-- ============================================================

INSERT INTO menu (name, price)
VALUES
    ('아메리카노', 3000),
    ('카페라떼', 4000),
    ('에스프레소', 3500),
    ('카푸치노', 4500),
    ('카라멜마키아토', 5500);

-- ============================================================
-- Recipe Item
-- ============================================================

INSERT INTO recipe_item (menu_id, ingredient_id, quantity)
SELECT
    m.id,
    i.id,
    v.quantity
FROM (
    VALUES
        ('아메리카노', '원두', 18),
        ('아메리카노', '물', 250),
        ('아메리카노', '컵', 1),

        ('카페라떼', '원두', 18),
        ('카페라떼', '물', 200),
        ('카페라떼', '우유', 150),
        ('카페라떼', '컵', 1),

        ('에스프레소', '원두', 10),
        ('에스프레소', '컵', 1),

        ('카푸치노', '원두', 10),
        ('카푸치노', '우유', 40),
        ('카푸치노', '컵', 1),

        ('카라멜마키아토', '원두', 10),
        ('카라멜마키아토', '우유', 30),
        ('카라멜마키아토', '컵', 1),
        ('카라멜마키아토', '시럽', 10)
) AS v(menu_name, ingredient_name, quantity)
JOIN menu m
    ON m.name = v.menu_name
JOIN ingredient i
    ON i.name = v.ingredient_name;

-- ============================================================
-- Option Master (기본 제약조건 포함)
-- ============================================================

INSERT INTO option_master (name, default_min_select, default_max_select, selection_mode, default_option_name)
VALUES
    ('온도', 1, 1, 'choice', 'HOT'),
    ('샷 추가', 0, 4, 'count', NULL),
    ('시럽 추가', 0, 2, 'count', NULL);

-- ============================================================
-- Option Item
-- ============================================================

INSERT INTO option_item (option_id, name, additional_price)
SELECT
    om.id,
    v.item_name,
    v.price
FROM (
    VALUES
        ('온도', 'HOT', 0),
        ('온도', 'ICE', 0),
        ('샷 추가', '샷 추가', 500),
        ('시럽 추가', '시럽 추가', 200)
) AS v(master_name, item_name, price)
JOIN option_master om
    ON om.name = v.master_name;

-- ============================================================
-- Option Recipe Item
-- ============================================================

INSERT INTO option_recipe_item (option_item_id, ingredient_id, quantity)
SELECT
    oi.id,
    i.id,
    v.quantity
FROM (
    VALUES
        ('샷 추가', '원두', 10),
        ('시럽 추가', '시럽', 10)
) AS v(item_name, ingredient_name, quantity)
JOIN option_item oi
    ON oi.name = v.item_name
JOIN ingredient i
    ON i.name = v.ingredient_name;

-- ============================================================
-- Option Group (PostgreSQL NULL 타입 명시적 캐스팅 보정)
-- ============================================================

INSERT INTO option_group (menu_id, option_id, override_min_select, override_max_select, override_default_option_name)
SELECT
    m.id,
    om.id,
    v.override_min,
    v.override_max,
    v.override_default
FROM (
    VALUES
        (1,  '아메리카노', '온도', CAST(NULL AS INTEGER), CAST(NULL AS INTEGER), CAST(NULL AS TEXT)),
        (2,  '아메리카노', '샷 추가', CAST(NULL AS INTEGER), CAST(NULL AS INTEGER), CAST(NULL AS TEXT)),
        (3,  '아메리카노', '시럽 추가', CAST(NULL AS INTEGER), CAST(NULL AS INTEGER), CAST(NULL AS TEXT)),

        (4,  '카페라떼', '온도', CAST(NULL AS INTEGER), CAST(NULL AS INTEGER), CAST(NULL AS TEXT)),
        (5,  '카페라떼', '샷 추가', CAST(NULL AS INTEGER), CAST(NULL AS INTEGER), CAST(NULL AS TEXT)),
        (6,  '카페라떼', '시럽 추가', CAST(NULL AS INTEGER), CAST(NULL AS INTEGER), CAST(NULL AS TEXT)),

        (7,  '에스프레소', '샷 추가', CAST(NULL AS INTEGER), 2, CAST(NULL AS TEXT)),

        (8,  '카푸치노', '온도', CAST(NULL AS INTEGER), CAST(NULL AS INTEGER), CAST(NULL AS TEXT)),
        (9,  '카푸치노', '샷 추가', CAST(NULL AS INTEGER), CAST(NULL AS INTEGER), CAST(NULL AS TEXT)),
        (10, '카푸치노', '시럽 추가', CAST(NULL AS INTEGER), CAST(NULL AS INTEGER), CAST(NULL AS TEXT)),

        (11, '카라멜마키아토', '온도', CAST(NULL AS INTEGER), CAST(NULL AS INTEGER), CAST(NULL AS TEXT)),
        (12, '카라멜마키아토', '샷 추가', CAST(NULL AS INTEGER), CAST(NULL AS INTEGER), CAST(NULL AS TEXT)),
        (13, '카라멜마키아토', '시럽 추가', CAST(NULL AS INTEGER), CAST(NULL AS INTEGER), CAST(NULL AS TEXT))
) AS v(seq, menu_name, option_name, override_min, override_max, override_default)
JOIN menu m ON m.name = v.menu_name
JOIN option_master om ON om.name = v.option_name
ORDER BY v.seq;

COMMIT;