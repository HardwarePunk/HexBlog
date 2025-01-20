"""Initial migration

Revision ID: 67d5433e92e3
Revises: 
Create Date: 2025-01-19 21:29:28.958183

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67d5433e92e3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.Column('tf_phone_number', sa.String(length=128), nullable=True),
    sa.Column('tf_primary_method', sa.String(length=64), nullable=True),
    sa.Column('tf_totp_secret', sa.String(length=255), nullable=True),
    sa.Column('display_name', sa.String(length=255), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('avatar_url', sa.String(length=255), nullable=True),
    sa.Column('website', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('fs_uniquifier', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('fs_uniquifier'),
    sa.UniqueConstraint('username')
    )
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=255), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('summary', sa.String(length=500), nullable=True),
    sa.Column('is_published', sa.Boolean(), nullable=True),
    sa.Column('is_featured', sa.Boolean(), nullable=True),
    sa.Column('meta_description', sa.String(length=160), nullable=True),
    sa.Column('meta_keywords', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('published_at', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('roles_users',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roles_users')
    op.drop_table('post')
    op.drop_table('user')
    op.drop_table('role')
    # ### end Alembic commands ###
