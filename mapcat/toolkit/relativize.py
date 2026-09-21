"""
Rewrite absolute paths stored in the mapcat database to be relative to
the appropriate MAPCAT_*_PARENT directory.
"""

import argparse as ap
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from mapcat.database import (
    AtomicMapCoaddTable,
    AtomicMapTable,
    DepthOneCoaddTable,
    DepthOneMapTable,
)

HELP_TEXT = """Use this utility to rewrite path columns in the mapcat
database from absolute paths to paths relative to the corresponding
MAPCAT_*_PARENT directory (e.g. MAPCAT_DEPTH_ONE_PARENT for depth-1
maps). Paths that are already relative are left untouched.

By default, all four map/coadd tables are processed. Use --table to
restrict to a subset. Use --dry-run to preview the changes that would
be made without writing them to the database.

An absolute path that does not live under the relevant parent
directory is left unchanged and reported as skipped, unless --force
is given, in which case it is rewritten using '..' segments as needed.
"""

USAGE = """Examples:

  Preview what would change, without touching the database:

    mapcatrelativize --dry-run

  Relativize every path column in every table:

    mapcatrelativize

  Only relativize depth-1 map paths:

    mapcatrelativize --table depth_one_map

  Relativize paths even if they fall outside the configured parent
  directory (using '..' segments):

    mapcatrelativize --force
"""

# table name -> (table class, settings attribute for the parent dir, path columns)
TABLE_PATH_COLUMNS = {
    "depth_one_map": (
        DepthOneMapTable,
        "depth_one_parent",
        [
            "map_path",
            "ivar_path",
            "rho_path",
            "kappa_path",
            "flux_path",
            "snr_path",
            "start_time_path",
            "mean_time_path",
            "end_time_path",
        ],
    ),
    "depth_one_coadd": (
        DepthOneCoaddTable,
        "depth_one_coadd_parent",
        [
            "map_path",
            "ivar_path",
            "rho_path",
            "kappa_path",
            "start_time_path",
            "mean_time_path",
            "end_time_path",
        ],
    ),
    "atomic_map": (
        AtomicMapTable,
        "atomic_parent",
        ["map_path", "ivar_path", "prefix_path"],
    ),
    "atomic_coadd": (
        AtomicMapCoaddTable,
        "atomic_coadd_parent",
        ["prefix_path", "geom_file_path"],
    ),
}


def relativize_path(path: str, parent: Path, force: bool) -> str | None:
    """
    Compute the path relative to `parent`, if `path` is absolute.

    Parameters
    ----------
    path : str
        The (possibly absolute) path to relativize.
    parent : Path
        The parent directory to relativize against.
    force : bool
        If True, relativize even if `path` does not live under `parent`,
        using '..' segments as needed. If False, such paths are left
        untouched (None is returned).

    Returns
    -------
    str | None
        The new relative path, or None if no change should be made
        (the path was already relative, or is outside `parent` and
        `force` is False).
    """

    if not os.path.isabs(path):
        return None

    resolved_parent = parent.resolve()
    resolved_path = Path(path).resolve()

    try:
        return str(resolved_path.relative_to(resolved_parent))
    except ValueError:
        if not force:
            return None
        return os.path.relpath(resolved_path, resolved_parent)


def core(session: sessionmaker, args: ap.Namespace):
    """
    Driver function for relativize.py. Rewrites absolute path columns
    in the requested tables to be relative to their configured parent
    directory.

    Parameters
    ----------
    session : sessionmaker
        A SQLAlchemy sessionmaker to use for database access.
    args : argparse.Namespace
        Parsed args with the relativize options.
    """

    from mapcat.helper import settings

    updated = 0
    skipped = []

    with session() as cur_session:
        for table_name in args.table:
            table_cls, parent_attr, columns = TABLE_PATH_COLUMNS[table_name]
            parent = getattr(settings, parent_attr)

            rows = cur_session.execute(select(table_cls)).scalars().all()

            for row in rows:
                for column in columns:
                    value = getattr(row, column)
                    if value is None:
                        continue

                    new_value = relativize_path(value, parent, args.force)
                    if new_value is None:
                        if os.path.isabs(value):
                            skipped.append(f"{table_name}.{column}: {value}")
                        continue

                    print(f"{table_name}.{column}: {value} -> {new_value}")
                    updated += 1
                    if not args.dry_run:
                        setattr(row, column, new_value)

        if not args.dry_run:
            cur_session.commit()

    print(
        f"\n{'Would update' if args.dry_run else 'Updated'} {updated} path column(s)."
    )
    if skipped:
        print(
            f"Skipped {len(skipped)} path(s) outside their configured parent "
            "directory (use --force to relativize them anyway):"
        )
        for entry in skipped:
            print(f"  {entry}")


def main():
    from mapcat.helper import settings

    parser = ap.ArgumentParser(
        prog="mapcatrelativize",
        usage=USAGE,
        description=HELP_TEXT,
        formatter_class=ap.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-t",
        "--table",
        type=str,
        nargs="+",
        choices=list(TABLE_PATH_COLUMNS),
        default=list(TABLE_PATH_COLUMNS),
        help="Which table(s) to relativize paths for. Defaults to all of them.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the changes that would be made without writing them.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Relativize paths even if they fall outside their configured "
            "parent directory, using '..' segments as needed."
        ),
    )

    args = parser.parse_args()

    core(session=settings.session, args=args)
