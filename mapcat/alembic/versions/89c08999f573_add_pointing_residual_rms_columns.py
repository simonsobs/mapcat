"""Add RMS fields to pointing residuals.

Revision ID: 89c08999f573
Revises: 26c6d65f3f3f
Create Date: 2026-04-21 20:52:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "89c08999f573"
down_revision: str | None = "26c6d65f3f3f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("depth_one_pointing_residuals") as batch_op:
        batch_op.add_column(sa.Column("ra_offset_rms", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("dec_offset_rms", sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("depth_one_pointing_residuals") as batch_op:
        batch_op.drop_column("dec_offset_rms")
        batch_op.drop_column("ra_offset_rms")
