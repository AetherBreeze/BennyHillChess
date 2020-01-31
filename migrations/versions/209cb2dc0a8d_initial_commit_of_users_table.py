"""initial commit of users table

Revision ID: 209cb2dc0a8d
Revises: 
Create Date: 2020-01-20 17:19:37.410540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '209cb2dc0a8d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('guest_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_guest_user_username'), 'guest_user', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_guest_user_username'), table_name='guest_user')
    op.drop_table('guest_user')
    # ### end Alembic commands ###