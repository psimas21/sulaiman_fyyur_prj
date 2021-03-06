"""adding new columns to the artist table

Revision ID: 83990f5c86be
Revises: 116a7ed6db55
Create Date: 2022-05-30 16:25:58.024015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83990f5c86be'
down_revision = '116a7ed6db55'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('artist', sa.Column('city', sa.String(length=120), nullable=True))
    op.add_column('artist', sa.Column('state', sa.String(length=120), nullable=True))
    op.add_column('artist', sa.Column('phone', sa.String(length=120), nullable=True))
    op.add_column('artist', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('artist', sa.Column('facebook_link', sa.String(length=120), nullable=True))
    op.add_column('artist', sa.Column('seeking_talent', sa.Boolean(create_constraint=120), default=True))
    op.add_column('artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('artist', sa.Column('image_link', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'image_link')
    op.drop_column('artist', 'seeking_description')
    op.drop_column('artist', 'seeking_talent')
    op.drop_column('artist', 'facebook_link')
    op.drop_column('artist', 'website')
    op.drop_column('artist', 'phone')
    op.drop_column('artist', 'state')
    op.drop_column('artist', 'city')
    op.drop_column('artist', 'genres')
    # ### end Alembic commands ###
