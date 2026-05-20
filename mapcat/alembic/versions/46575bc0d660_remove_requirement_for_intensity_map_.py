"""Remove requirement for intensity map, add flux and snr

Revision ID: 46575bc0d660
Revises: a1b2c3d4e5f6
Create Date: 2026-05-20 16:08:14.624772

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "46575bc0d660"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("depth_one_maps") as batch_op:
        batch_op.add_column(sa.Column("flux_map", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("snr_map", sa.String(), nullable=True))
        batch_op.alter_column("map_path", existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("depth_one_maps") as batch_op:
        batch_op.drop_column("flux_map")
        batch_op.drop_column("snr_map")
        batch_op.alter_column("map_path", existing_type=sa.String(), nullable=False)
