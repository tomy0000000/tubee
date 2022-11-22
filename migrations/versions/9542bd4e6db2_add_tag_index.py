"""add tag index

Revision ID: 9542bd4e6db2
Revises: 37c20f05bf44
Create Date: 2022-11-22 02:43:42.004723

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9542bd4e6db2"
down_revision = "37c20f05bf44"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tag", schema=None) as batch_op:
        batch_op.add_column(sa.Column("sort_index", sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table("tag", schema=None) as batch_op:
        batch_op.drop_column("sort_index")
