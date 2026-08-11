"""Initial schema from models.py

Revision ID: 0001_initial
Revises: None
Create Date: 2026-08-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. ingredient
    op.create_table(
        'ingredient',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('unit', sa.Text(), nullable=False, server_default=''),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # 2. menu
    op.create_table(
        'menu',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # 3. recipe_item
    op.create_table(
        'recipe_item',
        sa.Column('menu_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredient.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['menu_id'], ['menu.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('menu_id', 'ingredient_id')
    )

    # 4. option_master
    op.create_table(
        'option_master',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('default_min_select', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('default_max_select', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('selection_mode', sa.Text(), nullable=False, server_default='choice'),
        sa.Column('default_option_name', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. option_item
    op.create_table(
        'option_item',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('option_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('additional_price', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['option_id'], ['option_master.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. option_recipe_item
    op.create_table(
        'option_recipe_item',
        sa.Column('option_item_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredient.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['option_item_id'], ['option_item.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('option_item_id', 'ingredient_id')
    )

    # 7. option_group
    op.create_table(
        'option_group',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('menu_id', sa.Integer(), nullable=False),
        sa.Column('option_id', sa.Integer(), nullable=False),
        sa.Column('override_min_select', sa.Integer(), nullable=True),
        sa.Column('override_max_select', sa.Integer(), nullable=True),
        sa.Column('override_selection_mode', sa.Text(), nullable=True),
        sa.Column('override_default_option_name', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['menu_id'], ['menu.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['option_id'], ['option_master.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. inventory
    op.create_table(
        'inventory',
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredient.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('ingredient_id')
    )

    # 9. customer_order
    op.create_table(
        'customer_order',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_uuid', sa.Uuid(), nullable=False),
        sa.Column('total_price', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_uuid')
    )

    # 10. order_item
    op.create_table(
        'order_item',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('menu_name', sa.Text(), nullable=False),
        sa.Column('menu_price', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['customer_order.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. order_item_option
    op.create_table(
        'order_item_option',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_item_id', sa.Integer(), nullable=False),
        sa.Column('option_name', sa.Text(), nullable=False),
        sa.Column('additional_price', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['order_item_id'], ['order_item.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    tables = [
        'order_item_option',
        'order_item',
        'customer_order',
        'inventory',
        'option_group',
        'option_recipe_item',
        'option_item',
        'option_master',
        'recipe_item',
        'menu',
        'ingredient',
    ]
    for table in tables:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")