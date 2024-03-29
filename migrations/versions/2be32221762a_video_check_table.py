"""Video Check Table

Revision ID: 2be32221762a
Revises: f9a298276847
Create Date: 2022-07-09 04:26:06.407841

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2be32221762a"
down_revision = "f9a298276847"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "video_check",
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("video_id", sa.String(length=16), nullable=False),
        sa.Column("checked", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("username", "video_id", name=op.f("pk_video_check")),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("video_check")
    # ### end Alembic commands ###
