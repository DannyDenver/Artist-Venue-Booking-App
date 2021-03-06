"""empty message

Revision ID: 3e9609c8a623
Revises: 74adb668e3a7
Create Date: 2019-10-03 08:32:38.786268

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3e9609c8a623'
down_revision = '74adb668e3a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('show')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('show',
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('start_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], [u'Artist.id'], name=u'show_artist_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], [u'Venue.id'], name=u'show_venue_id_fkey'),
    sa.PrimaryKeyConstraint('artist_id', 'venue_id', name=u'show_pkey')
    )
    # ### end Alembic commands ###
