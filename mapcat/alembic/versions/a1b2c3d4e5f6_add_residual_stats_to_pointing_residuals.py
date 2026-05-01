"""Add residual_stats to PointingResidualTable

Revision ID: a1b2c3d4e5f6
Revises: cd9bc4ba5bc0
Create Date: 2026-04-23

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "cd9bc4ba5bc0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("depth_one_pointing_residuals") as batch:
        batch.add_column(sa.Column("residual_stats", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("depth_one_pointing_residuals") as batch:
        batch.drop_column("residual_stats")
