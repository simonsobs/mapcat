"""merge heads

Revision ID: 1ea365628633
Revises: 0762b3c7694d, 6eeaa35444bb
Create Date: 2026-08-31 13:46:54.313874

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = '1ea365628633'
down_revision: str | None = ('0762b3c7694d', '6eeaa35444bb')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass