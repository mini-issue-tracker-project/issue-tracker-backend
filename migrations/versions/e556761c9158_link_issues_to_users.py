"""link issues to users

Revision ID: e556761c9158
Revises: link_issues_users_001
Create Date: 2025-07-28 19:38:47.753320

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e556761c9158'
down_revision = 'ff2d89cb14b5'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Add author_id as nullable
    op.add_column('issues', sa.Column('author_id', sa.Integer(), nullable=True))
    # 2) Backfill author_id by matching old author string to User.name
    op.execute("""
        UPDATE issues
        SET author_id = users.id
        FROM users
        WHERE issues.author = users.name
    """)
    # 3) Make author_id non-nullable
    op.alter_column('issues', 'author_id', nullable=False)
    # 4) Drop the old author column
    op.drop_column('issues', 'author')

def downgrade():
    # 1) Add author column back as nullable string
    op.add_column('issues', sa.Column('author', sa.String(length=120), nullable=True))
    # 2) Backfill author from User.name
    op.execute("""
        UPDATE issues
        SET author = users.name
        FROM users
        WHERE issues.author_id = users.id
    """)
    # 3) Drop author_id column
    op.drop_column('issues', 'author_id') 