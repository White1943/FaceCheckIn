"""modify user_id to use uuid

Revision ID: xxx
Revises: previous_revision
Create Date: 2024-03-03 21:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    # 修改 user_id 列
    op.alter_column('users', 'user_id',
        existing_type=mysql.VARCHAR(length=32),
        nullable=False,
        server_default=sa.text('(uuid())'))

def downgrade():
    # 恢复原状
    op.alter_column('users', 'user_id',
        existing_type=mysql.VARCHAR(length=32),
        nullable=False,
        server_default=None) 