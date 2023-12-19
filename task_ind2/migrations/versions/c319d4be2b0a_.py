"""empty message

Revision ID: c319d4be2b0a
Revises: 9fbd08add139
Create Date: 2023-12-19 22:24:33.045229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c319d4be2b0a'
down_revision = '9fbd08add139'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sport_event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('sport', sa.String(length=100), nullable=True),
    sa.Column('participants', sa.Integer(), nullable=True),
    sa.Column('area', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sport_event')
    # ### end Alembic commands ###
