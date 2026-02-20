"""Create atomic maps

Revision ID: 57b97937e1bc
Revises: 78293df04081
Create Date: 2025-10-27 14:37:51.078172

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "57b97937e1bc"
down_revision: str | None = "78293df04081"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "atomic_maps",
        sa.Column("atomic_map_id", sa.Integer, primary_key=True),
        sa.Column("obs_id", sa.String(), nullable=False),
        sa.Column("telescope", sa.String(), nullable=False),
        sa.Column("freq_channel", sa.String(), nullable=False),
        sa.Column("wafer", sa.String(), nullable=False),
        sa.Column("ctime", sa.Integer(), nullable=False),
        sa.Column("split_label", sa.String(), nullable=False),
        sa.Column("map_path", sa.String(), nullable=True),
        sa.Column("ivar_path", sa.String(), nullable=True),
        sa.Column("valid", sa.Boolean(), nullable=True),
        sa.Column("split_detail", sa.String(), nullable=True),
        sa.Column("prefix_path", sa.String(), nullable=True),
        sa.Column("elevation", sa.Float(), nullable=True),
        sa.Column("azimuth", sa.Float(), nullable=True),
        sa.Column("pwv", sa.Float(), nullable=True),
        sa.Column("dpwv", sa.Float(), nullable=True),
        sa.Column("total_weight_qu", sa.Float(), nullable=True),
        sa.Column("mean_weight_qu", sa.Float(), nullable=True),
        sa.Column("median_weight_qu", sa.Float(), nullable=True),
        sa.Column("leakage_avg", sa.Float(), nullable=True),
        sa.Column("noise_avg", sa.Float(), nullable=True),
        sa.Column("ampl_2f_avg", sa.Float(), nullable=True),
        sa.Column("gain_avg", sa.Float(), nullable=True),
        sa.Column("tau_avg", sa.Float(), nullable=True),
        sa.Column("f_hwp", sa.Float(), nullable=True),
        sa.Column("roll_angle", sa.Float(), nullable=True),
        sa.Column("scan_speed", sa.Float(), nullable=True),
        sa.Column("scan_acc", sa.Float(), nullable=True),
        sa.Column("sun_distance", sa.Float(), nullable=True),
        sa.Column("ambient_temperature", sa.Float(), nullable=True),
        sa.Column("uv", sa.Float(), nullable=True),
        sa.Column("ra_center", sa.Float(), nullable=True),
        sa.Column("dec_center", sa.Float(), nullable=True),
        sa.Column("number_dets", sa.Integer(), nullable=True),
        sa.Column("moon_distance", sa.Float(), nullable=True),
        sa.Column("wind_speed", sa.Float(), nullable=True),
        sa.Column("wind_direction", sa.Float(), nullable=True),
    )

    op.create_table(
        "atomic_map_coadds",
        sa.Column("coadd_id", sa.Integer(), primary_key=True),
        sa.Column("coadd_name", sa.String(), nullable=False),
        sa.Column("coadd_path", sa.String(), nullable=False),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("interval", sa.String(), nullable=False),
        sa.Column("start_time", sa.Float(), nullable=False),
        sa.Column("end_time", sa.Float(), nullable=False),
        sa.Column("frequency", sa.String(), nullable=False),
    )

    op.create_table(
        "link_atomic_map_to_coadd",
        sa.Column(
            "atomic_map_id",
            sa.Integer(),
            sa.ForeignKey("atomic_maps.atomic_map_id"),
            nullable=False,
        ),
        sa.Column(
            "coadd_id",
            sa.Integer(),
            sa.ForeignKey("atomic_map_coadds.coadd_id"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("link_atomic_map_to_coadd")
    op.drop_table("atomic_map_coadds")
    op.drop_table("atomic_maps")
