CREATE TABLE ingredient (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE inventory (
    ingredient_id BIGSERIAL PRIMARY KEY,
    quantity INTEGER NOT NULL CHECK(quantity >= 0),

    Foreign Key (ingredient_id)
        REFERENCES ingredient(id)
);

CREATE TABLE menu (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    price INTEGER NOT NULL
);

CREATE TABLE recipe_item (
    menu_id BIGINT,
    ingredient_id BIGINT,
    quantity INTEGER NOT NULL,

    PRIMARY KEY (menu_id, ingredient_id),

    FOREIGN KEY (menu_id)
        REFERENCES menu(id),
    FOREIGN KEY (ingredient_id)
        REFERENCES ingredient(id)
);

CREATE TABLE option_group (
    id BIGSERIAL PRIMARY KEY ,
    menu_id BIGINT NOT NULL ,
    name TEXT NOT NULL ,
    min_select BIGINT NOT NULL ,
    max_select BIGINT NOT NULL ,
    FOREIGN KEY (menu_id)
        REFERENCES menu(id)
);

CREATE TABLE option (
    id BIGSERIAL PRIMARY KEY,
    option_group_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    additional_price INTEGER NOT NULL,
    FOREIGN KEY(option_group_id)
        REFERENCES option_group(id)
);

CREATE TABLE option_recipe_item (
    option_id BIGINT,
    ingredient_id BIGINT,
    quantity INTEGER NOT NULL,
    PRIMARY KEY(option_id, ingredient_id),
    FOREIGN KEY(option_id)
        REFERENCES option(id),
    FOREIGN KEY(ingredient_id)
        REFERENCES ingredient(id)
);