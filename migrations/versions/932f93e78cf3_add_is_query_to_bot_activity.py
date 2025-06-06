"""Add is_query to bot activity

Revision ID: 932f93e78cf3
Revises: 6f73d1d4827b
Create Date: 2025-06-02 16:25:00.218384

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '932f93e78cf3'
down_revision = '6f73d1d4827b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bot_activity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_query', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bot_activity', schema=None) as batch_op:
        batch_op.drop_column('is_query')

    # ### end Alembic commands ###
