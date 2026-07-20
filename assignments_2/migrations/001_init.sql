BEGIN;

-- ============================================================
-- Ingredient
-- ============================================================

CREATE TABLE ingredient (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL,

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
-- Option Group
-- ============================================================

CREATE TABLE option_group (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    menu_id BIGINT NOT NULL,

    name TEXT NOT NULL,

    min_select INTEGER NOT NULL,
    max_select INTEGER NOT NULL,

    CONSTRAINT pk_option_group
        PRIMARY KEY (id),

    CONSTRAINT ck_option_group_min
        CHECK (min_select >= 0),

    CONSTRAINT ck_option_group_max
        CHECK (max_select >= 1),

    CONSTRAINT ck_option_group_range
        CHECK (min_select <= max_select),

    CONSTRAINT fk_option_group_menu
        FOREIGN KEY (menu_id)
        REFERENCES menu(id)
        ON DELETE CASCADE
);

-- ============================================================
-- Option Item
-- ============================================================

CREATE TABLE option_item (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    option_group_id BIGINT NOT NULL,

    name TEXT NOT NULL,

    additional_price INTEGER NOT NULL,

    CONSTRAINT pk_option_item
        PRIMARY KEY (id),

    CONSTRAINT ck_option_price
        CHECK (additional_price >= 0),

    CONSTRAINT fk_option_item_group
        FOREIGN KEY (option_group_id)
        REFERENCES option_group(id)
        ON DELETE CASCADE
);

-- ============================================================
-- Option Recipe Item
-- ============================================================

CREATE TABLE option_recipe_item (
    option_id BIGINT NOT NULL,
    ingredient_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,

    CONSTRAINT pk_option_recipe_item
        PRIMARY KEY (option_id, ingredient_id),

    CONSTRAINT ck_option_recipe_quantity
        CHECK (quantity > 0),

    CONSTRAINT fk_option_recipe_option
        FOREIGN KEY (option_id)
        REFERENCES option_item(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_option_recipe_ingredient
        FOREIGN KEY (ingredient_id)
        REFERENCES ingredient(id)
        ON DELETE RESTRICT
);

COMMIT;