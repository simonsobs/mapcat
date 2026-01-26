"""add indices

Revision ID: 976527c198bd
Revises: fd6670a1fdbe
Create Date: 2026-01-09 13:05:17.392069

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "976527c198bd"
down_revision: Union[str, None] = "fd6670a1fdbe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_depth_one_maps_map_name",
        "depth_one_maps",
        ["map_name"],
        postgresql_using="hash",
    )
    op.create_index("ix_depth_one_maps_tube_slot", "depth_one_maps", ["tube_slot"])
    op.create_index("ix_depth_one_maps_frequency", "depth_one_maps", ["frequency"])
    op.create_index("ix_depth_one_maps_ctime", "depth_one_maps", ["ctime"])
    op.create_index("ix_depth_one_maps_start_time", "depth_one_maps", ["start_time"])
    op.create_index("ix_depth_one_maps_stop_time", "depth_one_maps", ["stop_time"])

    op.create_index("ix_tod_depth_one_pwv", "tod_depth_one", ["pwv"])
    op.create_index("ix_tod_depth_one_ctime", "tod_depth_one", ["ctime"])
    op.create_index("ix_tod_depth_one_start_time", "tod_depth_one", ["start_time"])
    op.create_index("ix_tod_depth_one_stop_time", "tod_depth_one", ["stop_time"])
    op.create_index("ix_tod_depth_one_telescope", "tod_depth_one", ["telescope"])
    op.create_index("ix_tod_depth_one_frequency", "tod_depth_one", ["frequency"])
    op.create_index("ix_tod_depth_one_wafer_count", "tod_depth_one", ["wafer_count"])

    op.create_index(
        "ix_time_domain_processing_map_id", "time_domain_processing", ["map_id"]
    )
    op.create_index(
        "ix_time_domain_processing_processing_status",
        "time_domain_processing",
        ["processing_status"],
    )

    op.create_index("ix_depth_one_sky_coverage_x", "depth_one_sky_coverage", ["x"])
    op.create_index("ix_depth_one_sky_coverage_y", "depth_one_sky_coverage", ["y"])

    op.create_index(
        "ix_depth_one_pointing_residuals", "depth_one_pointing_residuals", ["map_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_depth_one_maps_stop_time", table_name="depth_one_maps")
    op.drop_index("ix_depth_one_maps_start_time", table_name="depth_one_maps")
    op.drop_index("ix_depth_one_maps_ctime", table_name="depth_one_maps")
    op.drop_index("ix_depth_one_maps_frequency", table_name="depth_one_maps")
    op.drop_index("ix_depth_one_maps_tube_slot", table_name="depth_one_maps")
    op.drop_index("ix_depth_one_maps_map_name", table_name="depth_one_maps")

    op.drop_index("ix_tod_depth_one_pwv", table_name="tod_depth_one")
    op.drop_index("ix_tod_depth_one_ctime", table_name="tod_depth_one")
    op.drop_index("ix_tod_depth_one_start_time", table_name="tod_depth_one")
    op.drop_index("ix_tod_depth_one_stop_time", table_name="tod_depth_one")
    op.drop_index("ix_tod_depth_one_telescope", table_name="tod_depth_one")
    op.drop_index("ix_tod_depth_one_frequency", table_name="tod_depth_one")
    op.drop_index("ix_tod_depth_one_wafer_count", table_name="tod_depth_one")

    op.drop_index(
        "ix_time_domain_processing_map_id", table_name="time_domain_processing"
    )
    op.drop_index(
        "ix_time_domain_processing_processing_status",
        table_name="time_domain_processing",
    )

    op.drop_index("ix_depth_one_sky_coverage_x", table_name="depth_one_sky_coverage")
    op.drop_index("ix_depth_one_sky_coverage_y", table_name="depth_one_sky_coverage")

    op.drop_index(
        "ix_depth_one_pointing_residuals", table_name="depth_one_pointing_residuals"
    )
