"""empty message

Revision ID: d84508274ff3
Revises: ee9a8cb256b5
Create Date: 2020-02-20 01:38:54.685142

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd84508274ff3'
down_revision = 'ee9a8cb256b5'
branch_labels = None
depends_on = None

name = 'actionenum'
tmp_name = 'tmp_' + name
old_options = ('NOTIFICATION', 'PLAYLIST', 'DOWNLOAD')
new_options = ('Notification', 'Playlist', 'Download')
old_type = sa.Enum(*old_options, name=name)
new_type = sa.Enum(*new_options, name=name)


def upgrade():
    op.execute('ALTER TYPE {enum_name} RENAME TO {tmp_enum_name}'.format(
        enum_name=name,
        tmp_enum_name=tmp_name))
    new_type.create(op.get_bind())
    op.execute('ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {enum_name} USING {column_name}::text::{enum_name}'.format(
        table_name="action",
        column_name="action_type",
        enum_name="actionenum"))
    op.execute('DROP TYPE {}'.format(tmp_name))


def downgrade():
    op.execute('ALTER TYPE {enum_name} RENAME TO {tmp_enum_name}'.format(
        enum_name=name,
        tmp_enum_name=tmp_name))
    old_type.create(op.get_bind())
    op.execute('ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {enum_name} USING {column_name}::text::{enum_name}'.format(
        table_name="action",
        column_name="action_type",
        enum_name="actionenum"))
    op.execute('DROP TYPE {}'.format(tmp_name))
