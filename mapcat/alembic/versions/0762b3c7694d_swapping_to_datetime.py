"""Swapping to datetime

Revision ID: 0762b3c7694d
Revises: 6eeaa35444bb
Create Date: 2026-07-27 11:19:49.803412

"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0762b3c7694d"
down_revision: str | None = "6eeaa35444bb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_DEFINITIONS = {
    "atomic_maps": {
        "primary_key_name": "atomic_map_id",
        "column_names": [("ctime", False)],
    },
    "atomic_map_coadds": {
        "primary_key_name": "coadd_id",
        "column_names": [("start_time", False), ("stop_time", False)],
    },
    "depth_one_maps": {
        "primary_key_name": "map_id",
        "column_names": [("ctime", True), ("start_time", True), ("stop_time", True)],
    },
    "depth_one_coadds": {
        "primary_key_name": "coadd_id",
        "column_names": [("ctime", False), ("start_time", False), ("stop_time", False)],
    },
}


def unix_to_datetime(
    table_name: str,
    primary_key_name: str,
    column_names: list[tuple[str, bool]],
) -> None:
    """
    Convert a column from unix time to datetime.

    Parameters
    ----------
    table_name : str
        The name of the table to modify.
    primary_key_name : str
        The name of the primary key column for the table.
    column_names : list[tuple[str, bool]]
        The names of the columns to convert and boolean defining whether the column is indexed.
    """
    bind = op.get_bind()
    metadata = sa.MetaData()
    cur_table = sa.Table(table_name, metadata, autoload_with=bind)
    for column_name, is_indexed in column_names:
        temp_col_name = f"temp_datetime_{column_name}"
        if is_indexed:
            op.drop_index(f"ix_{table_name}_{column_name}", table_name=table_name)

        op.add_column(
            table_name, sa.Column(temp_col_name, sa.DateTime(), nullable=True)
        )

        stmt = sa.select(cur_table.c[column_name], cur_table.c[primary_key_name])
        results = bind.execute(stmt).fetchall()
        for row in results:
            unix_time = row[column_name]
            primary_key_value = row[primary_key_name]
            datetime_value = datetime.fromtimestamp(int(unix_time), tz=timezone.utc)
            update_stmt = (
                cur_table.update()
                .where(cur_table.c[primary_key_name] == primary_key_value)
                .values({temp_col_name: datetime_value})
            )
            bind.execute(update_stmt)

        with op.batch_alter_table(table_name) as batch_op:
            batch_op.drop_column(column_name)
            batch_op.alter_column(
                temp_col_name,
                new_column_name=column_name,
                nullable=False,
            )

        if is_indexed:
            op.create_index(f"ix_{table_name}_{column_name}", table_name, [column_name])


def _datetime_to_unix_value(datetime_value: datetime) -> int | None:
    datetime_value = datetime_value.astimezone(timezone.utc)
    return int(datetime_value.timestamp())


def datetime_to_unix(
    table_name: str,
    primary_key_name: str,
    column_names: list[tuple[str, bool]],
) -> None:
    """
    Convert a column from datetime to unix time.

    Parameters
    ----------
    table_name : str
        The name of the table to modify.
    primary_key_name : str
        The name of the primary key column for the table.
    column_names : list[tuple[str, bool]]
        The names of the columns to convert and a boolean defining whether the column is indexed.
    """
    bind = op.get_bind()
    metadata = sa.MetaData()
    cur_table = sa.Table(table_name, metadata, autoload_with=bind)
    for column_name, is_indexed in column_names:
        temp_col_name = f"temp_unix_{column_name}"
        if is_indexed:
            op.drop_index(f"ix_{table_name}_{column_name}", table_name=table_name)

        op.add_column(table_name, sa.Column(temp_col_name, sa.String(), nullable=True))

        stmt = sa.select(cur_table.c[column_name], cur_table.c[primary_key_name])
        results = bind.execute(stmt).fetchall()
        for row in results:
            datetime_value = row[column_name]
            primary_key_value = row[primary_key_name]
            unix_time = _datetime_to_unix_value(datetime_value)
            update_stmt = (
                cur_table.update()
                .where(cur_table.c[primary_key_name] == primary_key_value)
                .values({temp_col_name: unix_time})
            )
            bind.execute(update_stmt)

        with op.batch_alter_table(table_name) as batch_op:
            batch_op.drop_column(column_name)
            batch_op.alter_column(
                temp_col_name,
                new_column_name=column_name,
                nullable=False,
            )

        if is_indexed:
            op.create_index(f"ix_{table_name}_{column_name}", table_name, [column_name])


def upgrade() -> None:
    for table_name, table_data in TABLE_DEFINITIONS.items():
        unix_to_datetime(
            table_name, table_data["primary_key_name"], table_data["column_names"]
        )


def downgrade() -> None:
    for table_name, table_data in TABLE_DEFINITIONS.items():
        datetime_to_unix(
            table_name, table_data["primary_key_name"], table_data["column_names"]
        )
