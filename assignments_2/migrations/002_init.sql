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
        ('원두', 1000),
        ('물', 5000),
        ('우유', 3000),
        ('컵', 100),
        ('시럽', 1000)
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
-- Option Group
-- (option_group.menu_id 는 NOT NULL FK 라서, 원본에서 여러 메뉴가
--  공유하던 temperature_group/shot_group/syrup_group 을
--  메뉴별로 각각 별도 행으로 만든다)
--
-- ⚠️ INSERT ... SELECT ... FROM (VALUES ...) JOIN ... 은 삽입 순서를
--    보장하지 않는다. option_group.id 순서가 곧 CLI가 옵션을 물어보는
--    순서(온도 → 샷추가 → 시럽추가)라서, 순서가 뒤바뀌면 CLI가
--    잘못된 그룹에 잘못된 형식(choice/count)의 입력을 요구하게 된다.
--    그래서 seq 컬럼으로 의도한 순서를 명시하고 ORDER BY로 강제한다.
-- ============================================================

INSERT INTO option_group (menu_id, name, min_select, max_select, selection_mode)
SELECT
    m.id,
    v.name,
    v.min_select,
    v.max_select,
    v.selection_mode
FROM (
    VALUES
        (1,  '아메리카노', '온도', 1, 1, 'choice'),
        (2,  '아메리카노', '샷추가', 0, 4, 'count'),
        (3,  '아메리카노', '시럽추가', 0, 2, 'count'),

        (4,  '카페라떼', '온도', 1, 1, 'choice'),
        (5,  '카페라떼', '샷추가', 0, 4, 'count'),
        (6,  '카페라떼', '시럽추가', 0, 2, 'count'),

        (7,  '에스프레소', '샷추가', 0, 4, 'count'),

        (8,  '카푸치노', '샷추가', 0, 4, 'count'),
        (9,  '카푸치노', '시럽추가', 0, 2, 'count'),

        (10, '카라멜마키아토', '온도', 1, 1, 'choice'),
        (11, '카라멜마키아토', '샷추가', 0, 4, 'count'),
        (12, '카라멜마키아토', '시럽추가', 0, 2, 'count')
) AS v(seq, menu_name, name, min_select, max_select, selection_mode)
JOIN menu m
    ON m.name = v.menu_name
ORDER BY v.seq;

-- ============================================================
-- Option Item
-- ============================================================

INSERT INTO option_item (option_group_id, name, additional_price)
SELECT
    og.id,
    v.option_name,
    v.price
FROM option_group og
JOIN (
    VALUES
        (1, '온도', 'HOT', 0),
        (2, '온도', 'ICE', 0),
        (3, '샷추가', '샷추가', 500),
        (4, '시럽추가', '시럽추가', 200)
) AS v(seq, group_name, option_name, price)
    ON v.group_name = og.name
ORDER BY og.id, v.seq;

-- ============================================================
-- Option Recipe Item
-- (온도 옵션(HOT/ICE)은 원본에서도 레시피가 없어 그대로 비워둔다)
-- ============================================================

INSERT INTO option_recipe_item (option_id, ingredient_id, quantity)
SELECT
    oi.id,
    i.id,
    v.quantity
FROM option_item oi
JOIN option_group og
    ON og.id = oi.option_group_id
JOIN (
    VALUES
        ('샷추가', '원두', 10),
        ('시럽추가', '시럽', 10)
) AS v(group_name, ingredient_name, quantity)
    ON v.group_name = og.name
JOIN ingredient i
    ON i.name = v.ingredient_name;

COMMIT;