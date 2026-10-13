"""add planet map tables

Revision ID: b809eded6421
Revises: 0762b3c7694d
Create Date: 2026-10-07 11:21:13.132297

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b809eded6421'
down_revision: str | None = '0762b3c7694d'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # planet_map
    # ------------------------------------------------------------------
    op.create_table(
        "planet_map",
        sa.Column("obs_id", sa.String(), nullable=False),
        sa.Column("telescope", sa.String(), nullable=False),
        sa.Column("freq_channel", sa.String(), nullable=False),
        sa.Column("wafer", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),

        sa.Column("ctime", sa.DateTime(), nullable=False),

        sa.Column("hit_path", sa.String(), nullable=True),
        sa.Column("map_path", sa.String(), nullable=True),
        sa.Column("weight_path", sa.String(), nullable=True),
        sa.Column("weighted_map_path", sa.String(), nullable=True),

        sa.Column("elevation", sa.Float(), nullable=True),
        sa.Column("duration", sa.Float(), nullable=True),
        sa.Column("azimuth", sa.Float(), nullable=True),

        sa.Column("pwv", sa.Float(), nullable=True),
        sa.Column("pwv_std", sa.Float(), nullable=True),
        sa.Column("pwv_p2p", sa.Float(), nullable=True),

        sa.Column("pwv_apex", sa.Float(), nullable=True),
        sa.Column("pwv_apex_std", sa.Float(), nullable=True),
        sa.Column("pwv_apex_p2p", sa.Float(), nullable=True),

        sa.Column("f_hwp", sa.Float(), nullable=True),
        sa.Column("roll_angle", sa.Float(), nullable=True),
        sa.Column("scan_speed", sa.Float(), nullable=True),
        sa.Column("scan_acc", sa.Float(), nullable=True),

        sa.Column("sun_distance", sa.Float(), nullable=True),
        sa.Column("moon_distance", sa.Float(), nullable=True),

        sa.Column("wind_speed", sa.Float(), nullable=True),
        sa.Column("wind_direction", sa.Float(), nullable=True),
        sa.Column("ambient_temperature", sa.Float(), nullable=True),
        sa.Column("uv", sa.Float(), nullable=True),

        sa.Column(
            "detnum_before_fitselection",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "total_detnum",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "recenter",
            sa.Boolean(),
            nullable=True,
        ),

        sa.Column("yc", sa.Float(), nullable=True),
        sa.Column("xc", sa.Float(), nullable=True),

        sa.Column(
            "Tmap_variance",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "Qmap_variance",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "Umap_variance",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "proc",
            sa.JSON(),
            nullable=True,
        ),
        sa.Column(
            "detnum",
            sa.JSON(),
            nullable=True,
        ),
        sa.Column(
            "detid",
            sa.JSON(),
            nullable=True,
        ),

        sa.PrimaryKeyConstraint(
            "obs_id",
            "telescope",
            "freq_channel",
            "wafer",
            "source",
        ),
    )

    # ------------------------------------------------------------------
    # planet_map_fits
    # ------------------------------------------------------------------
    op.create_table(
        "planet_map_fits",
        sa.Column("obs_id", sa.String(), nullable=False),
        sa.Column("telescope", sa.String(), nullable=False),
        sa.Column("freq_channel", sa.String(), nullable=False),
        sa.Column("wafer", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),

        # Main-beam fit result (T map)
        sa.Column("peak", sa.Float(), nullable=True),
        sa.Column("amplitude", sa.Float(), nullable=True),
        sa.Column("xo", sa.Float(), nullable=True),
        sa.Column("yo", sa.Float(), nullable=True),
        sa.Column("sigmax", sa.Float(), nullable=True),
        sa.Column("sigmay", sa.Float(), nullable=True),
        sa.Column("theta", sa.Float(), nullable=True),
        sa.Column("redchit", sa.Float(), nullable=True),

        # Leakage-beam fit result (Q map)
        sa.Column("mq", sa.Float(), nullable=True),
        sa.Column("d0q", sa.Float(), nullable=True),
        sa.Column("d1q", sa.Float(), nullable=True),
        sa.Column("sigmaq", sa.Float(), nullable=True),
        sa.Column("redchiq", sa.Float(), nullable=True),

        # Leakage-beam fit result (U map)
        sa.Column("mu", sa.Float(), nullable=True),
        sa.Column("d0u", sa.Float(), nullable=True),
        sa.Column("d1u", sa.Float(), nullable=True),
        sa.Column("sigmau", sa.Float(), nullable=True),
        sa.Column("redchiu", sa.Float(), nullable=True),

        sa.ForeignKeyConstraint(
            [
                "obs_id",
                "telescope",
                "freq_channel",
                "wafer",
                "source",
            ],
            [
                "planet_map.obs_id",
                "planet_map.telescope",
                "planet_map.freq_channel",
                "planet_map.wafer",
                "planet_map.source",
            ],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "obs_id",
            "telescope",
            "freq_channel",
            "wafer",
            "source",
        ),
    )

    # ------------------------------------------------------------------
    # planet_todfit
    # ------------------------------------------------------------------
    op.create_table(
        "planet_todfit",
        sa.Column("obs_id", sa.String(), nullable=False),
        sa.Column("telescope", sa.String(), nullable=False),
        sa.Column("freq_channel", sa.String(), nullable=False),
        sa.Column("wafer", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("detid", sa.String(), nullable=False),

        sa.Column("ctime", sa.DateTime(), nullable=False),

        sa.Column("amplitude", sa.Float(), nullable=True),
        sa.Column("xo", sa.Float(), nullable=True),
        sa.Column("yo", sa.Float(), nullable=True),
        sa.Column("sigmax", sa.Float(), nullable=True),
        sa.Column("sigmay", sa.Float(), nullable=True),
        sa.Column("theta", sa.Float(), nullable=True),

        sa.Column("defla", sa.Float(), nullable=True),
        sa.Column("deflp", sa.Float(), nullable=True),

        sa.Column("amplitude_err", sa.Float(), nullable=True),
        sa.Column("xo_err", sa.Float(), nullable=True),
        sa.Column("yo_err", sa.Float(), nullable=True),
        sa.Column("sigmax_err", sa.Float(), nullable=True),
        sa.Column("sigmay_err", sa.Float(), nullable=True),
        sa.Column("theta_err", sa.Float(), nullable=True),

        sa.Column("defla_err", sa.Float(), nullable=True),
        sa.Column("deflp_err", sa.Float(), nullable=True),

        sa.Column("chisq", sa.Float(), nullable=True),
        sa.Column("dof", sa.Integer(), nullable=True),

        sa.Column("xi", sa.Float(), nullable=True),
        sa.Column("eta", sa.Float(), nullable=True),
        sa.Column("gamma", sa.Float(), nullable=True),

        sa.PrimaryKeyConstraint(
            "obs_id",
            "telescope",
            "freq_channel",
            "wafer",
            "source",
            "detid",
        ),
    )



def downgrade() -> None:
    op.drop_table("planet_map_fits")
    op.drop_table("planet_todfit")
    op.drop_table("planet_map")