"""update atomic map coadd table

Revision ID: fd6670a1fdbe
Revises: 1195d17201ba
Create Date: 2025-12-18 19:50:23.313924

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fd6670a1fdbe"
down_revision: str | None = "1195d17201ba"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "link_coadd_map_to_coadd",
        sa.Column(
            "parent_coadd_id",
            sa.Integer(),
            sa.ForeignKey("atomic_map_coadds.coadd_id"),
            nullable=False,
        ),
        sa.Column(
            "child_coadd_id",
            sa.Integer(),
            sa.ForeignKey("atomic_map_coadds.coadd_id"),
            nullable=False,
        ),
    )

    with op.batch_alter_table("atomic_map_coadds") as batch:
        batch.add_column(sa.Column("stop_time", sa.Float(), nullable=False))
        batch.add_column(sa.Column("prefix_path", sa.String(), nullable=False))
        batch.add_column(sa.Column("freq_channel", sa.String(), nullable=False))
        batch.add_column(sa.Column("geom_file_path", sa.String(), nullable=False))
        batch.add_column(sa.Column("split_label", sa.String(), nullable=False))

        batch.drop_column("end_time")
        batch.drop_column("coadd_path")
        batch.drop_column("frequency")


def downgrade() -> None:
    with op.batch_alter_table("atomic_map_coadds") as batch:
        batch.add_column(sa.Column("frequency", sa.Float(), nullable=False))
        batch.add_column(sa.Column("coadd_path", sa.String(), nullable=False))
        batch.add_column(sa.Column("end_time", sa.String(), nullable=False))

        batch.drop_column("split_label")
        batch.drop_column("geom_file_path")
        batch.drop_column("freq_channel")
        batch.drop_column("prefix_path")
        batch.drop_column("stop_time")

    op.drop_table("link_coadd_map_to_coadd")
