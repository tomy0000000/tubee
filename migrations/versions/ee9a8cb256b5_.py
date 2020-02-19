"""empty message

Revision ID: ee9a8cb256b5
Revises: c960e1668521
Create Date: 2020-02-19 22:51:19.167464

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee9a8cb256b5'
down_revision = 'c960e1668521'
branch_labels = None
depends_on = None

name = 'service'
tmp_name = 'tmp_' + name
old_options = ('ALL', 'PUSHOVER', 'LINE_NOTIFY')
new_options = ('Pushover', 'LineNotify')
old_type = sa.Enum(*old_options, name=name)
new_type = sa.Enum(*new_options, name=name)


def upgrade():
    op.execute('ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE json USING {column_name}::json'.format(
        table_name="action",
        column_name="details"))
    op.execute('ALTER TYPE {enum_name} RENAME TO {tmp_enum_name}'.format(
        enum_name=name,
        tmp_enum_name=tmp_name))
    new_type.create(op.get_bind())
    op.execute('ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {enum_name} USING {column_name}::text::{enum_name}'.format(
        table_name="notification",
        column_name="service",
        enum_name="service"))
    op.execute('DROP TYPE {}'.format(tmp_name))


def downgrade():
    op.execute('ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE VARCHAR(32) USING {column_name}::text'.format(
        table_name="action",
        column_name="details"))
    op.execute('ALTER TYPE {enum_name} RENAME TO {tmp_enum_name}'.format(
        enum_name=name,
        tmp_enum_name=tmp_name))
    old_type.create(op.get_bind())
    op.execute('ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {enum_name} USING {column_name}::text::{enum_name}'.format(
        table_name="notification",
        column_name="service",
        enum_name="service"))
    op.execute('DROP TYPE {}'.format(tmp_name))
