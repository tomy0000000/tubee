"""empty message

Revision ID: f28a243e95f2
Revises: 36a02dfb6a68
Create Date: 2019-06-25 16:40:13.095519

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f28a243e95f2'
down_revision = '36a02dfb6a68'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash', new_column_name='_password_hash', type_=sa.String(length=128))
        batch_op.alter_column('pushover_key', new_column_name='_pushover_key', type_=sa.String(length=40))
        # batch_op.add_column(sa.Column('_password_hash', sa.String(length=128), nullable=False))
        # batch_op.add_column(sa.Column('_pushover_key', sa.String(length=40), nullable=True))
        # batch_op.drop_column('password_hash')
        # batch_op.drop_column('pushover_key')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('_password_hash', new_column_name='password_hash', type_=sa.String(length=128))
        batch_op.alter_column('_pushover_key', new_column_name='pushover_key', type_=sa.String(length=40))
        # batch_op.add_column(sa.Column('pushover_key', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=40), nullable=True))
        # batch_op.add_column(sa.Column('password_hash', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=128), nullable=False))
        # batch_op.drop_column('_pushover_key')
        # batch_op.drop_column('_password_hash')

    # ### end Alembic commands ###