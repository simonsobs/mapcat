"""update to uuid and datetime

Revision ID: c87d072aac99
Revises: 46575bc0d660
Create Date: 2026-06-24 13:58:05.429510

"""

from collections.abc import Sequence

import sqlalchemy as sa
import uuid7 as uuid
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c87d072aac99"
down_revision: str | None = "46575bc0d660"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _update_links(
    link_table_name: str,
    link_column_name: str,
    foreign_table_name: str,
    foreign_key_name: str,
    foreign_uuid_column_name: str,
    tmp_column_name: str | None = None,
) -> None:
    """
    Function for updating a link table to use a new UUID foreign key
    from an old integer foreign key. Copilot assisted in writing this function:
    I wrote pure SQL statements that achieved the desired result, as well as a
    skeleton for _update_links, and Copilot translated the SQL statement into
    an alembic migration using SQLAlchemy.

    Parameters
    ----------
    link_table_name : str
        Name of the link table to modify
    link_column_name : str
        Name of current foreign key column in link_table
    foreign_table_name : str
        Name of foreign table to link into
    foreign_key_name : str
        Name of current ID column (int) in foreign table that link_column_name foreign key into
    foreign_uuid_column_name : str
        Name of new ID column (UUID) in foreign table that we would like link_table to be foreign key into

    Returns
    -------
    None
    """

    bind = op.get_bind()
    metadata = sa.MetaData()

    tmp_column = f"{link_column_name}_tmp"

    # First make a temporary column of type UUID. This will be our foreign key column eventually
    op.add_column(
        table_name=link_table_name,
        column=sa.Column(tmp_column, sa.Uuid(), nullable=True),
    )

    link_table = sa.Table(link_table_name, metadata, autoload_with=bind)
    foreign_table = sa.Table(foreign_table_name, metadata, autoload_with=bind)

    # Update the link table temporary column we just made
    # The value of this column with be the UUID column value in
    # foreign table where the old index
    stmt = sa.update(link_table).values(
        **{
            tmp_column: (
                sa.select(foreign_table.c[foreign_uuid_column_name])
                .where(
                    foreign_table.c[foreign_key_name] == link_table.c[link_column_name]
                )
                .scalar_subquery()
            )
        }
    )
    bind.execute(stmt)

    # We can now safely drop the original foreign key in link table as the link info is saved in tmp_column
    op.drop_column(link_table_name, link_column_name)

    # Add a new, permanent link column, which we will copy values from tmp_column into.
    # We intentionally leave the FK creation for later so it points at the final
    # parent column name after the parent table is renamed.
    # Note the foreign key constraint isn't actually made here yet since we
    # will later rename the foreign key column in foreign_table from TABLE_id_uuid to TABLE_id.
    op.add_column(
        table_name=link_table_name,
        column=sa.Column(
            link_column_name,
            sa.Uuid(),
            nullable=False,
            index=True,
        ),
    )

    stmt = sa.update(link_table).values(**{link_column_name: link_table.c[tmp_column]})
    bind.execute(stmt)

    op.drop_column(link_table_name, tmp_column)


def _update_to_UUID_with_links(
    table_name: str,
    old_key_name: str,
    link_table_list: list[tuple[str, str]] | None = None,
) -> None:
    """
    Function to update a table from integer ID to UUID.
    This function will correcly update all link tables with
    foreign keys into table_name to use the new UUID.

    Parameters
    ----------
    table_name : str
        Name of the table to update UUIDs.
    old_key_name : str
        Name of the column containing the old primary keys to be updated.
    link_table_list : list[tuple[str, str]] | None, default; None
        List of tuples where each entry is a pair of link table with a foreign key into table_name
        to be updated and foreign key name in that link table. If none, table_name has no foreign keys
        into it so we can just skip updating those links.

    Returns
    -------
    None
    """
    bind = op.get_bind()
    metadata = sa.MetaData()

    tmp_key_name = f"{old_key_name}_uuid"
    # Add a new column which will hold our UUIDs
    op.add_column(
        table_name=table_name,
        column=sa.Column(tmp_key_name, sa.Uuid(), nullable=True),
    )

    # Populate the UUID rows with uuids
    parent_table = sa.Table(table_name, metadata, autoload_with=bind)
    rows = bind.execute(sa.select(parent_table.c[old_key_name])).fetchall()
    for (old_id,) in rows:
        new_uuid = uuid.create()
        bind.execute(
            parent_table.update()
            .where(parent_table.c[old_key_name] == old_id)
            .values(tmp_key_name=new_uuid)
        )

    # Update the link tables
    if link_table_list:
        for link_table_name, link_column_name in link_table_list:
            _update_links(
                link_table_name=link_table_name,
                link_column_name=link_column_name,
                foreign_table_name=table_name,
                foreign_key_name=old_key_name,
                foreign_uuid_column_name=tmp_key_name,
            )

    # Now that we've done the sandbag swap we can drop the old ID
    # column and alter the new column to have the correct name and be primary
    op.drop_column(table_name=table_name, column_name=old_key_name)

    op.alter_column(
        table_name=table_name,
        column_name=tmp_key_name,
        new_column_name=old_key_name,
    )
    op.create_primary_key(
        f"pk_{table_name}",
        table_name,
        [old_key_name],
    )

    if link_table_list:
        # Recreate the foreign key constraints on the link tables
        for link_table_name, link_column_name in link_table_list:
            op.create_foreign_key(
                f"fk_{link_table_name}_{link_column_name}",
                link_table_name,
                table_name,
                [link_column_name],
                [old_key_name],
            )


def _update_sky_coverage():
    pass


def upgrade() -> None:

    # TODO: check these for foreign keys not in links.py
    atomic_coadd_link_tables = [
        ("link_atomic_map_to_coadd", "coadd_id"),
        ("link_coadd_map_to_coadd", "parent_coadd_id"),
        ("link_coadd_map_to_coadd", "child_coadd_id"),
    ]
    _update_to_UUID_with_links(
        table_name="atomic_map_coadds",
        old_key_name="coadd_id",
        link_table_list=atomic_coadd_link_tables,
    )

    atomic_map_link_tables = [("link_atomic_map_to_coadd", "atomic_map_id")]
    _update_to_UUID_with_links(
        table_name="atomic_maps",
        old_key_name="atomic_map_id",
        link_table_list=atomic_map_link_tables,
    )

    depth_one_coadd_link_tables = [("link_depth_one_map_to_coadd", "coadd_id")]
    _update_to_UUID_with_links(
        table_name="depth_one_coadds",
        old_key_name="coadd_id",
        link_table_list=depth_one_coadd_link_tables,
    )

    depth_one_link_tables = [
        ("link_depth_one_map_to_coadd", "map_id"),
        ("link_tod_to_depth_one_map", "map_id"),
    ]
    _update_to_UUID_with_links(
        table_name="depth_one_maps",
        old_key_name="map_id",
        link_table_list=depth_one_link_tables,
    )

    _update_to_UUID_with_links(
        table_name="pipeline_information",
        old_key_name="pipeline_information_id",
        link_table_list=None,
    )

    _update_to_UUID_with_links(
        table_name="depth_one_pointing_residuals",
        old_key_name="pointing_residual_id",
        link_table_list=None,
    )

    # TODO: write migration for sky coverage
    _update_sky_coverage()

    _update_to_UUID_with_links(
        table_name="time_domain_processing",
        old_key_name="processing_status_id",
        link_table_list=None,
    )

    tod_link_tables = [
        ("link_tod_to_depth_one_map", "tod_id"),
    ]
    _update_to_UUID_with_links(
        table_name="tod_depth_one",
        old_key_name="tod_id",
        link_table_list=tod_link_tables,
    )
