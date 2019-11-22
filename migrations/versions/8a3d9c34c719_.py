"""empty message

Revision ID: 8a3d9c34c719
Revises: 0749207b97a6
Create Date: 2019-11-23 04:20:50.486070

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a3d9c34c719'
down_revision = '0749207b97a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('callback', schema=None) as batch_op:
        # batch_op.add_column(sa.Column('callback_id', sa.String(length=36), nullable=False))
        # batch_op.drop_column('id')
        batch_op.alter_column('id', new_column_name='callback_id', type_=sa.String(length=36))
        batch_op.create_foreign_key(batch_op.f('fk_callback_channel_id_channel'), 'channel', ['channel_id'], ['channel_id'])

    with op.batch_alter_table('notification', schema=None) as batch_op:
        # batch_op.add_column(sa.Column('notification_id', sa.String(length=36), nullable=False))
        # batch_op.drop_column('id')
        batch_op.alter_column('id', new_column_name='notification_id', type_=sa.String(length=36))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('callback', schema=None) as batch_op:
        # batch_op.add_column(sa.Column('id', sa.VARCHAR(length=32), autoincrement=False, nullable=False))
        # batch_op.drop_column('callback_id')
        batch_op.alter_column('callback_id', new_column_name='id', type_=sa.String(length=32))
        batch_op.drop_constraint(batch_op.f('fk_callback_channel_id_channel'), type_='foreignkey')

    with op.batch_alter_table('notification', schema=None) as batch_op:
        # batch_op.add_column(sa.Column('id', sa.VARCHAR(length=32), autoincrement=False, nullable=False))
        # batch_op.drop_column('notification_id')
        batch_op.alter_column('notification_id', new_column_name='id', type_=sa.String(length=32))

    # ### end Alembic commands ###
