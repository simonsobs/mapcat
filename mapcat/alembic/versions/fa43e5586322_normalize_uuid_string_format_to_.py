"""normalize uuid string format to undashed hex

Revision ID: fa43e5586322
Revises: 6eeaa35444bb
Create Date: 2026-07-16 19:51:42.644908

Corrective follow-up to 6eeaa35444bb: that migration's raw-SQL backfill
wrote new map_id/coadd_id values via str(uuid.uuid4()) (36-char, dashed),
but SQLAlchemy's sa.Uuid() bind processor serializes UUID values as 32-char
undashed hex for SQLite. Since SQLite compares TEXT columns byte-for-byte,
any query that binds a fresh uuid.UUID value (e.g. an explicit map_id=/
coadd_id= filter) silently matched zero rows against the dashed values
6eeaa35444bb wrote, even though the values were logically equal.

This migration normalizes every map_id/coadd_id column to the 32-char
undashed form. It is idempotent (only touches values that are still
36-char/dashed), so it is a no-op against any database created after
6eeaa35444bb's backfill fix landed -- it only matters for databases
migrated before that fix.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa43e5586322'
down_revision: Union[str, None] = '6eeaa35444bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (table, column) pairs touched by 6eeaa35444bb's backfill.
_UUID_COLUMNS = [
    ("depth_one_maps", "map_id"),
    ("depth_one_coadds", "coadd_id"),
    ("time_domain_processing", "map_id"),
    ("time_domain_processing", "coadd_id"),
    ("depth_one_pointing_residuals", "map_id"),
    ("depth_one_sky_coverage", "map_id"),
    ("link_depth_one_map_to_coadd", "map_id"),
    ("link_depth_one_map_to_coadd", "coadd_id"),
    ("link_tod_to_depth_one_map", "map_id"),
    ("pipeline_information", "map_id"),
]


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("PRAGMA foreign_keys=OFF"))
    for table, column in _UUID_COLUMNS:
        bind.execute(
            sa.text(
                f"UPDATE {table} SET {column} = REPLACE({column}, '-', '') "
                f"WHERE length({column}) = 36"
            )
        )
    bind.execute(sa.text("PRAGMA foreign_keys=ON"))


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("PRAGMA foreign_keys=OFF"))
    for table, column in _UUID_COLUMNS:
        bind.execute(
            sa.text(
                f"UPDATE {table} SET {column} = "
                f"substr({column}, 1, 8) || '-' || "
                f"substr({column}, 9, 4) || '-' || "
                f"substr({column}, 13, 4) || '-' || "
                f"substr({column}, 17, 4) || '-' || "
                f"substr({column}, 21, 12) "
                f"WHERE length({column}) = 32"
            )
        )
    bind.execute(sa.text("PRAGMA foreign_keys=ON"))
