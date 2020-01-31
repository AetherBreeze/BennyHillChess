"""added 'last active' datetime to guest accs

Revision ID: edfc20513439
Revises: 52017c58f0dc
Create Date: 2020-01-21 13:21:26.262238

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'edfc20513439'
down_revision = '52017c58f0dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_active_datetime', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_users_last_active_datetime'), 'users', ['last_active_datetime'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_last_active_datetime'), table_name='users')
    op.drop_column('users', 'last_active_datetime')
    # ### end Alembic commands ###