"""initial migration

Revision ID: 8000929c7f0b
Revises: 
Create Date: 2023-11-27 18:22:35.690115

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8000929c7f0b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    sa.Column('password', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('matches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team1', sa.String(length=200), nullable=True),
    sa.Column('team2', sa.String(length=200), nullable=True),
    sa.Column('stadium', sa.String(length=200), nullable=True),
    sa.Column('time', sa.String(length=200), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('news',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('article', sa.String(length=1000), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('player',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('age', sa.String(length=200), nullable=True),
    sa.Column('weight', sa.String(length=200), nullable=True),
    sa.Column('height', sa.String(length=200), nullable=True),
    sa.Column('imageFile', sa.String(length=200), nullable=True),
    sa.Column('nationality', sa.String(length=200), nullable=True),
    sa.Column('jersey_no', sa.String(length=200), nullable=True),
    sa.Column('position', sa.String(length=200), nullable=True),
    sa.Column('match_played', sa.String(length=200), nullable=True),
    sa.Column('goals', sa.String(length=200), nullable=True),
    sa.Column('assists', sa.String(length=200), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('purchase',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=False),
    sa.Column('seat_type', sa.String(length=50), nullable=False),
    sa.Column('num_tickets', sa.Integer(), nullable=False),
    sa.Column('total_price', sa.Float(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('card_number', sa.String(length=16), nullable=False),
    sa.Column('cardholder_name', sa.String(length=100), nullable=False),
    sa.Column('expiry_date', sa.String(length=5), nullable=False),
    sa.Column('security_code', sa.String(length=3), nullable=False),
    sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('purchase')
    op.drop_table('user')
    op.drop_table('player')
    op.drop_table('news')
    op.drop_table('matches')
    op.drop_table('admin_user')
    # ### end Alembic commands ###
