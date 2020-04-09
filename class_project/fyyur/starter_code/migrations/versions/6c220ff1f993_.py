"""empty message

Revision ID: 6c220ff1f993
Revises: 536051c94885
Create Date: 2020-04-01 17:16:49.382703

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c220ff1f993'
down_revision = '536051c94885'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('past_shows_count', sa.Integer(), nullable=True))
    op.add_column('artist', sa.Column('seeking_description', sa.String(length=200), nullable=True))
    op.add_column('artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('artist', sa.Column('upcoming_shows_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'upcoming_shows_count')
    op.drop_column('artist', 'seeking_venue')
    op.drop_column('artist', 'seeking_description')
    op.drop_column('artist', 'past_shows_count')
    # ### end Alembic commands ###