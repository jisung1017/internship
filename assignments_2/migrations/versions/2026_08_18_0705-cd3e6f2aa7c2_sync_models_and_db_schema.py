"""sync_models_and_db_schema

Revision ID: cd3e6f2aa7c2
Revises: '0001_initial'
Create Date: 2026-08-18 07:05:35.991024+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'cd3e6f2aa7c2'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('customer_order', 'total_price',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)
    op.alter_column('inventory', 'quantity',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)
    op.alter_column('menu', 'price',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)
    op.alter_column('option_group', 'override_min_select',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)
    op.alter_column('option_group', 'override_max_select',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)

    # 💡 유니크 제약조건 조건부 생성 (이미 존재하면 건너뜀)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_menu_option'
            ) THEN
                ALTER TABLE option_group ADD CONSTRAINT uq_menu_option UNIQUE (menu_id, option_id);
            END IF;
        END $$;
    """)

    op.alter_column('option_item', 'additional_price',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False,
               existing_server_default=sa.text('0'))
    op.alter_column('option_master', 'default_min_select',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False,
               existing_server_default=sa.text('0'))
    op.alter_column('option_master', 'default_max_select',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False,
               existing_server_default=sa.text('1'))
    op.alter_column('option_recipe_item', 'quantity',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)
    op.alter_column('order_item', 'menu_price',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)
    op.alter_column('order_item', 'quantity',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)
    op.alter_column('order_item_option', 'additional_price',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False,
               existing_server_default=sa.text('0'))
    op.alter_column('recipe_item', 'quantity',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)


def downgrade() -> None:
    op.alter_column('recipe_item', 'quantity',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('order_item_option', 'additional_price',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default=sa.text('0'))
    op.alter_column('order_item', 'quantity',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('order_item', 'menu_price',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('option_recipe_item', 'quantity',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('option_master', 'default_max_select',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default=sa.text('1'))
    op.alter_column('option_master', 'default_min_select',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default=sa.text('0'))
    op.alter_column('option_item', 'additional_price',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default=sa.text('0'))

    op.execute("ALTER TABLE option_group DROP CONSTRAINT IF EXISTS uq_menu_option;")

    op.alter_column('option_group', 'override_max_select',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.alter_column('option_group', 'override_min_select',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.alter_column('menu', 'price',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('inventory', 'quantity',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('customer_order', 'total_price',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)