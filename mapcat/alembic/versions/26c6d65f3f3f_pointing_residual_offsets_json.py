"""Store pointing residual offsets as JSON.

Revision ID: 26c6d65f3f3f
Revises: 6ce7e94dfd2d
Create Date: 2026-04-21 20:26:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "26c6d65f3f3f"
down_revision: str | None = "6ce7e94dfd2d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("depth_one_pointing_residuals") as batch_op:
        batch_op.alter_column(
            "ra_offset",
            existing_type=sa.Float(),
            type_=sa.JSON(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "dec_offset",
            existing_type=sa.Float(),
            type_=sa.JSON(),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("depth_one_pointing_residuals") as batch_op:
        batch_op.alter_column(
            "ra_offset",
            existing_type=sa.JSON(),
            type_=sa.Float(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "dec_offset",
            existing_type=sa.JSON(),
            type_=sa.Float(),
            existing_nullable=True,
        )
