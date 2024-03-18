"""Add action automate column

Revision ID: 37c20f05bf44
Revises: 2be32221762a
Create Date: 2022-07-31 15:27:45.040777

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "37c20f05bf44"
down_revision = "2be32221762a"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("action", schema=None) as batch_op:
        batch_op.add_column(sa.Column("automate", sa.Boolean(), nullable=True))

    op.execute('UPDATE "public"."action" SET "automate" = TRUE;')

    with op.batch_alter_table("action", schema=None) as batch_op:
        batch_op.alter_column("automate", existing_type=sa.BOOLEAN(), nullable=False)


def downgrade():
    with op.batch_alter_table("action", schema=None) as batch_op:
        batch_op.drop_column("automate")
