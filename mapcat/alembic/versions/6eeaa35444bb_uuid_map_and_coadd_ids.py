"""Convert depth_one_maps.map_id / depth_one_coadds.coadd_id to UUID
primary keys, and generalize time_domain_processing to track coadds too

Revision ID: 6eeaa35444bb
Revises: 46575bc0d660
Create Date: 2026-07-16 13:15:00.000000

This is a one-way migration: the original integer IDs are not recoverable
once dropped, so downgrade() is intentionally not implemented (see
downgrade() below for details).

Step C (swapping in the new UUID columns and their constraints) is done
with raw SQL table recreation rather than op.batch_alter_table()'s
create_primary_key()/create_foreign_key(). In this SQLAlchemy/Alembic
version, batch mode's constraint reflection silently produced wrong
results here -- e.g. depth_one_maps ended up with *no* primary key at all,
and depth_one_sky_coverage's composite (map_id, x, y) primary key silently
shrunk to just (x, y) -- because the table's columns individually declare
primary_key=True (redundant with the table-level constraint), which
conflicts with reflection during batch recreation. Raw SQL sidesteps that
ambiguity entirely: every target table's DDL below is written out in full
and verified against a real SQLite database before this migration was
finalized.
"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6eeaa35444bb"
down_revision: str | None = "46575bc0d660"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _backfill(bind, table: str, id_column: str, mapping: dict) -> None:
    """UPDATE `table` SET `id_column`_new = <uuid> WHERE `id_column` = <old id>,
    for every (old id -> new uuid) pair in `mapping`. Batches statements in
    chunks rather than one round-trip per row."""
    new_column = f"{id_column}_new"
    items = list(mapping.items())
    chunk_size = 500
    for start in range(0, len(items), chunk_size):
        chunk = items[start : start + chunk_size]
        for old_id, new_uuid in chunk:
            bind.execute(
                sa.text(
                    f"UPDATE {table} SET {new_column} = :new_uuid "
                    f"WHERE {id_column} = :old_id"
                ),
                {"new_uuid": str(new_uuid), "old_id": old_id},
            )


def _recreate_table(bind, table: str, create_sql: str, insert_sql: str) -> None:
    """Standard SQLite table-recreation dance: build the new table under a
    temporary name, copy data across, drop the old table, then rename the
    new one into place. `create_sql`/`insert_sql` must reference the
    temporary name `{table}_new`."""
    bind.execute(sa.text(create_sql))
    bind.execute(sa.text(insert_sql))
    bind.execute(sa.text(f"DROP TABLE {table}"))
    bind.execute(sa.text(f"ALTER TABLE {table}_new RENAME TO {table}"))


def upgrade() -> None:
    bind = op.get_bind()

    # -- Step A: add nullable UUID shadow columns everywhere a map_id or
    # coadd_id appears, so we can backfill without ever having a NOT NULL
    # column with no value.
    with op.batch_alter_table("depth_one_maps") as batch_op:
        batch_op.add_column(sa.Column("map_id_new", sa.Uuid(), nullable=True))
    with op.batch_alter_table("depth_one_coadds") as batch_op:
        batch_op.add_column(sa.Column("coadd_id_new", sa.Uuid(), nullable=True))

    with op.batch_alter_table("time_domain_processing") as batch_op:
        batch_op.add_column(sa.Column("map_id_new", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("coadd_id", sa.Uuid(), nullable=True))
    with op.batch_alter_table("depth_one_pointing_residuals") as batch_op:
        batch_op.add_column(sa.Column("map_id_new", sa.Uuid(), nullable=True))
    with op.batch_alter_table("depth_one_sky_coverage") as batch_op:
        batch_op.add_column(sa.Column("map_id_new", sa.Uuid(), nullable=True))
    with op.batch_alter_table("link_depth_one_map_to_coadd") as batch_op:
        batch_op.add_column(sa.Column("map_id_new", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("coadd_id_new", sa.Uuid(), nullable=True))
    with op.batch_alter_table("link_tod_to_depth_one_map") as batch_op:
        batch_op.add_column(sa.Column("map_id_new", sa.Uuid(), nullable=True))
    with op.batch_alter_table("pipeline_information") as batch_op:
        batch_op.add_column(sa.Column("map_id_new", sa.Uuid(), nullable=True))

    # -- Step B: generate new UUIDs for every existing map/coadd, and
    # propagate the old-id -> new-uuid mapping to every dependent table.
    # Raw SQL only -- never import the (still-evolving) ORM model classes
    # inside a migration.
    map_rows = bind.execute(sa.text("SELECT map_id FROM depth_one_maps")).fetchall()
    map_id_mapping = {row.map_id: uuid.uuid4() for row in map_rows}
    _backfill(bind, "depth_one_maps", "map_id", map_id_mapping)

    coadd_rows = bind.execute(
        sa.text("SELECT coadd_id FROM depth_one_coadds")
    ).fetchall()
    coadd_id_mapping = {row.coadd_id: uuid.uuid4() for row in coadd_rows}
    _backfill(bind, "depth_one_coadds", "coadd_id", coadd_id_mapping)

    _backfill(bind, "time_domain_processing", "map_id", map_id_mapping)
    _backfill(bind, "depth_one_pointing_residuals", "map_id", map_id_mapping)
    _backfill(bind, "depth_one_sky_coverage", "map_id", map_id_mapping)
    _backfill(bind, "link_depth_one_map_to_coadd", "map_id", map_id_mapping)
    _backfill(bind, "link_depth_one_map_to_coadd", "coadd_id", coadd_id_mapping)
    _backfill(bind, "link_tod_to_depth_one_map", "map_id", map_id_mapping)
    _backfill(bind, "pipeline_information", "map_id", map_id_mapping)

    # -- Step C: swap in the new UUID columns and their constraints via raw
    # SQL table recreation (see module docstring for why). depth_one_maps/
    # depth_one_coadds go first, so dependent tables' new FK constraints
    # have something to point at.
    _recreate_table(
        bind,
        "depth_one_maps",
        """
        CREATE TABLE depth_one_maps_new (
            map_name VARCHAR NOT NULL,
            map_path VARCHAR,
            ivar_path VARCHAR,
            mean_time_path VARCHAR,
            tube_slot VARCHAR NOT NULL,
            frequency VARCHAR NOT NULL,
            ctime FLOAT NOT NULL,
            start_time FLOAT NOT NULL,
            stop_time FLOAT NOT NULL,
            notes JSON,
            rho_path VARCHAR,
            kappa_path VARCHAR,
            start_time_path VARCHAR,
            end_time_path VARCHAR,
            flux_path VARCHAR,
            snr_path VARCHAR,
            map_id CHAR(32) NOT NULL,
            PRIMARY KEY (map_id),
            UNIQUE (map_path),
            UNIQUE (map_name)
        )
        """,
        """
        INSERT INTO depth_one_maps_new
        SELECT map_name, map_path, ivar_path, mean_time_path, tube_slot,
               frequency, ctime, start_time, stop_time, notes, rho_path,
               kappa_path, start_time_path, end_time_path, flux_path,
               snr_path, map_id_new
        FROM depth_one_maps
        """,
    )
    for index_sql in [
        "CREATE INDEX ix_depth_one_maps_map_name ON depth_one_maps (map_name)",
        "CREATE INDEX ix_depth_one_maps_start_time ON depth_one_maps (start_time)",
        "CREATE INDEX ix_depth_one_maps_ctime ON depth_one_maps (ctime)",
        "CREATE INDEX ix_depth_one_maps_stop_time ON depth_one_maps (stop_time)",
        "CREATE INDEX ix_depth_one_maps_frequency ON depth_one_maps (frequency)",
        "CREATE INDEX ix_depth_one_maps_tube_slot ON depth_one_maps (tube_slot)",
    ]:
        bind.execute(sa.text(index_sql))

    _recreate_table(
        bind,
        "depth_one_coadds",
        """
        CREATE TABLE depth_one_coadds_new (
            coadd_name VARCHAR NOT NULL,
            coadd_type VARCHAR NOT NULL,
            map_path VARCHAR NOT NULL,
            frequency VARCHAR NOT NULL,
            ctime FLOAT NOT NULL,
            start_time FLOAT NOT NULL,
            stop_time FLOAT NOT NULL,
            ivar_path VARCHAR,
            rho_path VARCHAR,
            kappa_path VARCHAR,
            start_time_path VARCHAR,
            mean_time_path VARCHAR,
            end_time_path VARCHAR,
            coadd_id CHAR(32) NOT NULL,
            PRIMARY KEY (coadd_id)
        )
        """,
        """
        INSERT INTO depth_one_coadds_new
        SELECT coadd_name, coadd_type, map_path, frequency, ctime,
               start_time, stop_time, ivar_path, rho_path, kappa_path,
               start_time_path, mean_time_path, end_time_path, coadd_id_new
        FROM depth_one_coadds
        """,
    )

    _recreate_table(
        bind,
        "time_domain_processing",
        """
        CREATE TABLE time_domain_processing_new (
            processing_status_id INTEGER NOT NULL,
            processing_start FLOAT,
            processing_end FLOAT,
            processing_status VARCHAR NOT NULL,
            map_id CHAR(32),
            coadd_id CHAR(32),
            PRIMARY KEY (processing_status_id),
            FOREIGN KEY(map_id) REFERENCES depth_one_maps (map_id) ON DELETE CASCADE,
            FOREIGN KEY(coadd_id) REFERENCES depth_one_coadds (coadd_id) ON DELETE CASCADE,
            CONSTRAINT ck_time_domain_processing_exactly_one_target
                CHECK ((map_id IS NOT NULL) != (coadd_id IS NOT NULL))
        )
        """,
        """
        INSERT INTO time_domain_processing_new
        SELECT processing_status_id, processing_start, processing_end,
               processing_status, map_id_new, coadd_id
        FROM time_domain_processing
        """,
    )
    bind.execute(
        sa.text(
            "CREATE INDEX ix_time_domain_processing_map_id "
            "ON time_domain_processing (map_id)"
        )
    )
    bind.execute(
        sa.text(
            "CREATE INDEX ix_time_domain_processing_coadd_id "
            "ON time_domain_processing (coadd_id)"
        )
    )
    bind.execute(
        sa.text(
            "CREATE INDEX ix_time_domain_processing_processing_status "
            "ON time_domain_processing (processing_status)"
        )
    )

    _recreate_table(
        bind,
        "depth_one_pointing_residuals",
        """
        CREATE TABLE depth_one_pointing_residuals_new (
            pointing_residual_id INTEGER NOT NULL,
            residual_model JSON NOT NULL,
            residual_stats JSON,
            map_id CHAR(32) NOT NULL,
            PRIMARY KEY (pointing_residual_id),
            FOREIGN KEY(map_id) REFERENCES depth_one_maps (map_id) ON DELETE CASCADE
        )
        """,
        """
        INSERT INTO depth_one_pointing_residuals_new
        SELECT pointing_residual_id, residual_model, residual_stats, map_id_new
        FROM depth_one_pointing_residuals
        """,
    )
    bind.execute(
        sa.text(
            "CREATE INDEX ix_depth_one_pointing_residuals "
            "ON depth_one_pointing_residuals (map_id)"
        )
    )

    _recreate_table(
        bind,
        "depth_one_sky_coverage",
        """
        CREATE TABLE depth_one_sky_coverage_new (
            x CHAR NOT NULL,
            y CHAR NOT NULL,
            map_id CHAR(32) NOT NULL,
            PRIMARY KEY (map_id, x, y),
            FOREIGN KEY(map_id) REFERENCES depth_one_maps (map_id) ON DELETE CASCADE
        )
        """,
        """
        INSERT INTO depth_one_sky_coverage_new
        SELECT x, y, map_id_new
        FROM depth_one_sky_coverage
        """,
    )
    bind.execute(
        sa.text(
            "CREATE INDEX ix_depth_one_sky_coverage_x ON depth_one_sky_coverage (x)"
        )
    )
    bind.execute(
        sa.text(
            "CREATE INDEX ix_depth_one_sky_coverage_y ON depth_one_sky_coverage (y)"
        )
    )

    _recreate_table(
        bind,
        "link_depth_one_map_to_coadd",
        """
        CREATE TABLE link_depth_one_map_to_coadd_new (
            map_id CHAR(32) NOT NULL,
            coadd_id CHAR(32) NOT NULL,
            PRIMARY KEY (map_id, coadd_id),
            FOREIGN KEY(map_id) REFERENCES depth_one_maps (map_id) ON DELETE CASCADE,
            FOREIGN KEY(coadd_id) REFERENCES depth_one_coadds (coadd_id) ON DELETE CASCADE
        )
        """,
        """
        INSERT INTO link_depth_one_map_to_coadd_new
        SELECT map_id_new, coadd_id_new
        FROM link_depth_one_map_to_coadd
        """,
    )

    _recreate_table(
        bind,
        "link_tod_to_depth_one_map",
        """
        CREATE TABLE link_tod_to_depth_one_map_new (
            tod_id INTEGER NOT NULL,
            map_id CHAR(32) NOT NULL,
            PRIMARY KEY (tod_id, map_id),
            FOREIGN KEY(tod_id) REFERENCES tod_depth_one (tod_id) ON DELETE CASCADE,
            FOREIGN KEY(map_id) REFERENCES depth_one_maps (map_id) ON DELETE CASCADE
        )
        """,
        """
        INSERT INTO link_tod_to_depth_one_map_new
        SELECT tod_id, map_id_new
        FROM link_tod_to_depth_one_map
        """,
    )

    _recreate_table(
        bind,
        "pipeline_information",
        """
        CREATE TABLE pipeline_information_new (
            pipeline_information_id INTEGER NOT NULL,
            sotodlib_version VARCHAR NOT NULL,
            map_maker VARCHAR NOT NULL,
            preprocess_info JSON,
            map_id CHAR(32) NOT NULL,
            PRIMARY KEY (pipeline_information_id),
            FOREIGN KEY(map_id) REFERENCES depth_one_maps (map_id) ON DELETE CASCADE
        )
        """,
        """
        INSERT INTO pipeline_information_new
        SELECT pipeline_information_id, sotodlib_version, map_maker,
               preprocess_info, map_id_new
        FROM pipeline_information
        """,
    )


def downgrade() -> None:
    raise NotImplementedError(
        "This migration is one-way: the original integer map_id/coadd_id "
        "values are dropped and cannot be recovered. A 'downgrade' that "
        "renumbered rows from scratch would silently desync any external "
        "system that cached the old integer IDs, so it is not implemented. "
        "Restore from a backup taken before this migration if you need to "
        "roll back."
    )
