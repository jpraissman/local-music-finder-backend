"""empty message

Revision ID: b281f4faba61
Revises: 6c272d413474
Create Date: 2024-11-15 00:32:11.508061

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b281f4faba61'
down_revision = '6c272d413474'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event distance', schema=None) as batch_op:
        batch_op.alter_column('event_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event distance', schema=None) as batch_op:
        batch_op.alter_column('event_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
