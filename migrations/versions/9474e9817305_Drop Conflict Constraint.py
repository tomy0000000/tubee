"""Drop Conflict Constraint

Revision ID: 9474e9817305
Revises: 34935013ab33
Create Date: 2020-03-12 10:21:53.211649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9474e9817305"
down_revision = "34935013ab33"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("action", schema=None) as batch_op:
        batch_op.drop_constraint("fk_action_username_subscription", type_="foreignkey")
        batch_op.drop_constraint(
            "fk_action_channel_id_subscription", type_="foreignkey"
        )

    with op.batch_alter_table("subscription_tag", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_subscription_tag_channel_id_subscription", type_="foreignkey"
        )
        batch_op.drop_constraint(
            "fk_subscription_tag_username_subscription", type_="foreignkey"
        )

    with op.batch_alter_table("subscription", schema=None) as batch_op:
        batch_op.drop_constraint("uq_subscription_channel_id", type_="unique")
        batch_op.drop_constraint("uq_subscription_username", type_="unique")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("subscription", schema=None) as batch_op:
        batch_op.create_unique_constraint("uq_subscription_username", ["username"])
        batch_op.create_unique_constraint("uq_subscription_channel_id", ["channel_id"])

    with op.batch_alter_table("subscription_tag", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_subscription_tag_username_subscription",
            "subscription",
            ["username"],
            ["username"],
        )
        batch_op.create_foreign_key(
            "fk_subscription_tag_channel_id_subscription",
            "subscription",
            ["channel_id"],
            ["channel_id"],
        )

    with op.batch_alter_table("action", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_action_channel_id_subscription",
            "subscription",
            ["channel_id"],
            ["channel_id"],
        )
        batch_op.create_foreign_key(
            "fk_action_username_subscription",
            "subscription",
            ["username"],
            ["username"],
        )

    # ### end Alembic commands ###
