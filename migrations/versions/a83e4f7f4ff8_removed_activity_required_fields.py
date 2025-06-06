"""Removed activity required fields

Revision ID: a83e4f7f4ff8
Revises: e329c5e1c40e
Create Date: 2025-06-01 01:02:15.534451

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a83e4f7f4ff8'
down_revision = 'e329c5e1c40e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('activity', schema=None) as batch_op:
        batch_op.alter_column('user_agent',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('ip',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('referer',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('activity', schema=None) as batch_op:
        batch_op.alter_column('referer',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('ip',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('user_agent',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # ### end Alembic commands ###
