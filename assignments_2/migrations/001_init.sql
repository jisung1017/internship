BEGIN;

-- ============================================================
-- Ingredient
-- ============================================================

CREATE TABLE ingredient (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT '',

    CONSTRAINT pk_ingredient
        PRIMARY KEY (id),

    CONSTRAINT uq_ingredient_name
        UNIQUE (name)
);

-- ============================================================
-- Inventory
-- ============================================================

CREATE TABLE inventory (
    ingredient_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,

    CONSTRAINT pk_inventory
        PRIMARY KEY (ingredient_id),

    CONSTRAINT ck_inventory_quantity
        CHECK (quantity >= 0),

    CONSTRAINT fk_inventory_ingredient
        FOREIGN KEY (ingredient_id)
        REFERENCES ingredient(id)
        ON DELETE RESTRICT
);

-- ============================================================
-- Menu
-- ============================================================

CREATE TABLE menu (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,

    CONSTRAINT pk_menu
        PRIMARY KEY (id),

    CONSTRAINT uq_menu_name
        UNIQUE (name),

    CONSTRAINT ck_menu_price
        CHECK (price >= 0)
);

-- ============================================================
-- Recipe Item
-- ============================================================

CREATE TABLE recipe_item (
    menu_id BIGINT NOT NULL,
    ingredient_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,

    CONSTRAINT pk_recipe_item
        PRIMARY KEY (menu_id, ingredient_id),

    CONSTRAINT ck_recipe_quantity
        CHECK (quantity > 0),

    CONSTRAINT fk_recipe_menu
        FOREIGN KEY (menu_id)
        REFERENCES menu(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_recipe_ingredient
        FOREIGN KEY (ingredient_id)
        REFERENCES ingredient(id)
        ON DELETE RESTRICT
);

-- ============================================================
-- Option Master (기본 제약조건 보유)
-- ============================================================

CREATE TABLE option_master (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL,
    default_min_select INTEGER NOT NULL DEFAULT 0,
    default_max_select INTEGER NOT NULL DEFAULT 1,
    selection_mode TEXT NOT NULL DEFAULT 'choice',

    CONSTRAINT pk_option_master
        PRIMARY KEY (id),

    CONSTRAINT ck_option_master_min
        CHECK (default_min_select >= 0),

    CONSTRAINT ck_option_master_max
        CHECK (default_max_select >= 1),

    CONSTRAINT ck_option_master_range
        CHECK (default_min_select <= default_max_select),

    CONSTRAINT ck_option_master_selection_mode
        CHECK (selection_mode IN ('choice', 'count'))
);

-- ============================================================
-- Option Item
-- ============================================================

CREATE TABLE option_item (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    option_id BIGINT NOT NULL,

    name TEXT NOT NULL,
    additional_price INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT pk_option_item
        PRIMARY KEY (id),

    CONSTRAINT ck_option_price
        CHECK (additional_price >= 0),

    CONSTRAINT fk_option_item_option
        FOREIGN KEY (option_id)
        REFERENCES option_master(id)
        ON DELETE CASCADE
);

-- ============================================================
-- Option Recipe Item
-- ============================================================

CREATE TABLE option_recipe_item (
    option_item_id BIGINT NOT NULL,
    ingredient_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,

    CONSTRAINT pk_option_recipe_item
        PRIMARY KEY (option_item_id, ingredient_id),

    CONSTRAINT ck_option_recipe_quantity
        CHECK (quantity > 0),

    CONSTRAINT fk_option_recipe_option_item
        FOREIGN KEY (option_item_id)
        REFERENCES option_item(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_option_recipe_ingredient
        FOREIGN KEY (ingredient_id)
        REFERENCES ingredient(id)
        ON DELETE RESTRICT
);

-- ============================================================
-- Option Group (N:M 매핑 + NULL 허용 Override)
-- ============================================================

CREATE TABLE option_group (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    menu_id BIGINT NOT NULL,
    option_id BIGINT NOT NULL,

    override_min_select INTEGER NULL,
    override_max_select INTEGER NULL,
    override_selection_mode TEXT NULL,

    CONSTRAINT pk_option_group
        PRIMARY KEY (id),

    CONSTRAINT ck_option_group_override_min
        CHECK (override_min_select IS NULL OR override_min_select >= 0),

    CONSTRAINT ck_option_group_override_max
        CHECK (override_max_select IS NULL OR override_max_select >= 1),

    CONSTRAINT ck_option_group_override_selection_mode
        CHECK (override_selection_mode IS NULL OR override_selection_mode IN ('choice', 'count')),

    CONSTRAINT fk_option_group_menu
        FOREIGN KEY (menu_id)
        REFERENCES menu(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_option_group_option
        FOREIGN KEY (option_id)
        REFERENCES option_master(id)
        ON DELETE RESTRICT
);

-- ============================================================
-- Customer Order
-- ============================================================

CREATE TABLE customer_order (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    order_uuid UUID NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    total_price INTEGER NOT NULL,

    CONSTRAINT pk_customer_order
        PRIMARY KEY (id),

    CONSTRAINT uq_customer_order_uuid
        UNIQUE (order_uuid),

    CONSTRAINT ck_customer_order_total_price
        CHECK (total_price >= 0)
);

CREATE TABLE order_item (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    order_id BIGINT NOT NULL,

    menu_name TEXT NOT NULL,
    menu_price INTEGER NOT NULL,
    quantity INTEGER NOT NULL,

    CONSTRAINT pk_order_item
        PRIMARY KEY (id),

    CONSTRAINT ck_order_item_menu_price
        CHECK (menu_price >= 0),

    CONSTRAINT ck_order_item_quantity
        CHECK (quantity > 0),

    CONSTRAINT fk_order_item_order
        FOREIGN KEY (order_id)
        REFERENCES customer_order(id)
        ON DELETE CASCADE
);

CREATE TABLE order_item_option (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    order_item_id BIGINT NOT NULL,

    option_name TEXT NOT NULL,
    additional_price INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT pk_order_item_option
        PRIMARY KEY (id),

    CONSTRAINT ck_order_item_option_price
        CHECK (additional_price >= 0),

    CONSTRAINT fk_order_item_option_item
        FOREIGN KEY (order_item_id)
        REFERENCES order_item(id)
        ON DELETE CASCADE
);

COMMIT;