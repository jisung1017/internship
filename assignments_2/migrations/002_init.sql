BEGIN;

-- ============================================================
-- Ingredient
-- ============================================================

INSERT INTO ingredient (name)
VALUES
    ('원두'),
    ('우유'),
    ('얼음'),
    ('컵');

-- ============================================================
-- Inventory
-- ============================================================

INSERT INTO inventory (
    ingredient_id,
    quantity
)
SELECT
    id,
    100
FROM ingredient;

-- ============================================================
-- Menu
-- ============================================================

INSERT INTO menu (
    name,
    price
)
VALUES
    ('아메리카노', 3000),
    ('카페라떼', 4000),
    ('에스프레소', 3500),
    ('카푸치노', 4500);

-- ============================================================
-- Recipe Item
-- ============================================================

-- 아메리카노
INSERT INTO recipe_item (menu_id, ingredient_id, quantity)
SELECT
    m.id,
    i.id,
    v.quantity
FROM (
    VALUES
        ('아메리카노', '원두', 1),
        ('아메리카노', '컵', 1),

        ('카페라떼', '원두', 1),
        ('카페라떼', '우유', 1),
        ('카페라떼', '컵', 1),

        ('에스프레소', '원두', 2),
        ('에스프레소', '컵', 1),

        ('카푸치노', '원두', 1),
        ('카푸치노', '우유', 1),
        ('카푸치노', '컵', 1)
) AS v(menu_name, ingredient_name, quantity)
JOIN menu m
    ON m.name = v.menu_name
JOIN ingredient i
    ON i.name = v.ingredient_name;

-- ============================================================
-- Option Group
-- ============================================================

INSERT INTO option_group (
    menu_id,
    name,
    min_select,
    max_select,
    selection_mode
)
SELECT
    id,
    '추가 옵션',
    0,
    3,
    'choice'
FROM menu;

-- ============================================================
-- Option Item
-- ============================================================

INSERT INTO option_item (
    option_group_id,
    name,
    additional_price
)
SELECT
    og.id,
    v.name,
    v.price
FROM option_group og
CROSS JOIN (
    VALUES
        ('샷 추가', 500),
        ('얼음 추가', 0),
        ('우유 추가', 500)
) AS v(name, price);

-- ============================================================
-- Option Recipe Item
-- ============================================================

-- 샷 추가
INSERT INTO option_recipe_item (
    option_id,
    ingredient_id,
    quantity
)
SELECT
    oi.id,
    i.id,
    1
FROM option_item oi
JOIN ingredient i
    ON i.name = '원두'
WHERE oi.name = '샷 추가';

-- 얼음 추가
INSERT INTO option_recipe_item (
    option_id,
    ingredient_id,
    quantity
)
SELECT
    oi.id,
    i.id,
    1
FROM option_item oi
JOIN ingredient i
    ON i.name = '얼음'
WHERE oi.name = '얼음 추가';

-- 우유 추가
INSERT INTO option_recipe_item (
    option_id,
    ingredient_id,
    quantity
)
SELECT
    oi.id,
    i.id,
    1
FROM option_item oi
JOIN ingredient i
    ON i.name = '우유'
WHERE oi.name = '우유 추가';

COMMIT;