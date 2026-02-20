"""Add notes JSON field to depth_one_maps

Revision ID: bc2be980cfe7
Revises: 57b97937e1bc
Create Date: 2025-12-15 17:01:14.401164

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bc2be980cfe7"
down_revision: str | None = "57b97937e1bc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("depth_one_maps", sa.Column("notes", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("depth_one_maps", "notes")
