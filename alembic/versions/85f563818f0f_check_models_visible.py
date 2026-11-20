"""check models visible

Revision ID: 85f563818f0f
Revises: bc089d0fce68
Create Date: 2026-11-20

"""

from collections.abc import Sequence

revision: str = "85f563818f0f"
down_revision: str | None = "bc089d0fce68"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
