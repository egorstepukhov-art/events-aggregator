"""check models visible

Revision ID: 85f563818f0f
Revises: bc089d0fce68
Create Date: 2026-11-20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '85f563818f0f'
down_revision: Union[str, None] = 'bc089d0fce68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass