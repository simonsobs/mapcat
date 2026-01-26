"""Add filtered masps

Revision ID: 6ce7e94dfd2d
Revises: 976527c198bd
Create Date: 2026-01-26 09:47:56.733253

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6ce7e94dfd2d"
down_revision: Union[str, None] = "976527c198bd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_COLUMNS_DEPTH_ONE = [
    "rho_path",
    "kappa_path",
    "start_time_path",
    "end_time_path",
]

NEW_COLUMNS_DEPTH_ONE_COADDS = [
    "ivar_path",
    "rho_path",
    "kappa_path",
    "start_time_path",
    "mean_time_path",
    "end_time_path",
]


def upgrade() -> None:
    # Depth 1
    op.alter_column("depth_one_maps", "time_path", new_column_name="mean_time_path")

    for column_name in NEW_COLUMNS_DEPTH_ONE:
        op.add_column(
            "depth_one_maps", sa.Column(column_name, sa.String(), nullable=True)
        )

    # Coadds
    op.alter_column("depth_one_coadds", "coadd_path", new_column_name="map_path")

    for column_name in NEW_COLUMNS_DEPTH_ONE_COADDS:
        op.add_column(
            "depth_one_coadds", sa.Column(column_name, sa.String(), nullable=True)
        )

    pass


def downgrade() -> None:
    # Depth 1
    op.alter_column("depth_one_maps", "mean_time_path", new_column_name="time_path")

    # Coadds
    op.alter_column("depth_one_coadds", "map_path", new_column_name="coadd_path")

    for column_name in NEW_COLUMNS_DEPTH_ONE_COADDS:
        op.drop_column("depth_one_coadds", column_name)

    pass
