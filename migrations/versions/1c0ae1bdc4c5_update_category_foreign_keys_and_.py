"""update category foreign keys and nullable

Revision ID: 1c0ae1bdc4c5
Revises: 96904c054e6a
Create Date: 2026-11-23 19:02:12.024999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c0ae1bdc4c5'
down_revision = '96904c054e6a'
branch_labels = None
depends_on = None


def upgrade():
    naming_convention = {
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    }
    with op.batch_alter_table('categories', naming_convention=naming_convention) as batch_op:
        batch_op.drop_constraint('fk_categories_user_id_users', type_='foreignkey')
        batch_op.drop_constraint('fk_categories_parent_id_categories', type_='foreignkey')
        batch_op.create_foreign_key('fk_categories_user_id_users', 'users', ['user_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key('fk_categories_parent_id_categories', 'categories', ['parent_id'], ['id'], ondelete='SET NULL')
        batch_op.alter_column('user_id',
               existing_type=sa.String(length=36),
               nullable=True)


def downgrade():
    naming_convention = {
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    }
    with op.batch_alter_table('categories', naming_convention=naming_convention) as batch_op:
        batch_op.drop_constraint('fk_categories_user_id_users', type_='foreignkey')
        batch_op.drop_constraint('fk_categories_parent_id_categories', type_='foreignkey')
        batch_op.create_foreign_key('fk_categories_user_id_users', 'users', ['user_id'], ['id'])
        batch_op.create_foreign_key('fk_categories_parent_id_categories', 'categories', ['parent_id'], ['id'])
        batch_op.alter_column('user_id',
               existing_type=sa.String(length=36),
               nullable=False)
