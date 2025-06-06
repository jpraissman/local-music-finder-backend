"""Update relationship between event views and events

Revision ID: e00cba5c75de
Revises: 8d02e1f7fe38
Create Date: 2025-06-03 17:33:24.696624

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e00cba5c75de'
down_revision = '8d02e1f7fe38'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event_view', schema=None) as batch_op:
        batch_op.drop_constraint('event_view_event_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'event', ['event_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event_view', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('event_view_event_id_fkey', 'event', ['event_id'], ['id'])

    # ### end Alembic commands ###
