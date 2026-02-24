"""
Reset processing statuses in the TimeDomainProcessingTable.
"""

import argparse as ap

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from mapcat.database import DepthOneMapTable, TimeDomainProcessingTable

VALID_STATUSES = ["failed", "completed", "permafail"]

HELP_TEXT = """Use this utility to reset processing statuses in the
TimeDomainProcessingTable. Statuses can be set to 'failed', 'completed', or
'permafail' (which tells the pipeline not to retry the map due to a
pathological failure), or removed entirely by not specifying a target status.

Entries to reset can be filtered by map ID, time range (using the map's ctime),
and/or current processing status.
"""

USAGE = """Examples:

  Reset all processing statuses to 'failed':

    mapcatreset --status failed

  Remove processing status entries for specific map IDs:

    mapcatreset --map-id 10 11 12

  Reset entries with status 'running' to 'failed' in a time range:

    mapcatreset --status failed --from-status running \\
        --start-time 1755000000 --end-time 1756000000

  Mark a specific map as 'permafail' (will not be retried by the pipeline):

    mapcatreset --status permafail --map-id 42
"""


def core(session: sessionmaker, args: ap.Namespace):
    """
    Driver function for reset.py. Takes a session and parsed args, then
    resets TimeDomainProcessingTable entries matching the given filters.

    Parameters
    ----------
    session : sessionmaker
        A SQLAlchemy sessionmaker to use for database access.
    args : argparse.Namespace
        Parsed args with the reset options.
    """

    with session() as cur_session:
        stmt = select(TimeDomainProcessingTable)

        if args.map_id:
            stmt = stmt.where(TimeDomainProcessingTable.map_id.in_(args.map_id))

        if args.start_time is not None or args.end_time is not None:
            stmt = stmt.join(
                DepthOneMapTable,
                TimeDomainProcessingTable.map_id == DepthOneMapTable.map_id,
            )
            if args.start_time is not None:
                stmt = stmt.where(DepthOneMapTable.ctime >= args.start_time)
            if args.end_time is not None:
                stmt = stmt.where(DepthOneMapTable.ctime <= args.end_time)

        if args.from_status is not None:
            stmt = stmt.where(
                TimeDomainProcessingTable.processing_status == args.from_status
            )

        entries = cur_session.execute(stmt).scalars().all()

        if args.status is None:
            for entry in entries:
                cur_session.delete(entry)
        else:
            for entry in entries:
                entry.processing_status = args.status

        cur_session.commit()


def main():
    from mapcat.helper import settings

    parser = ap.ArgumentParser(
        prog="mapcatreset",
        usage=USAGE,
        description=HELP_TEXT,
        formatter_class=ap.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-s",
        "--status",
        type=str,
        choices=VALID_STATUSES,
        default=None,
        help=(
            f"New status to set. Options: {', '.join(VALID_STATUSES)}. "
            "If not provided, matching processing status entries are removed."
        ),
    )

    parser.add_argument(
        "-m",
        "--map-id",
        type=int,
        nargs="+",
        default=None,
        help="Only reset entries for these map IDs.",
    )

    parser.add_argument(
        "--start-time",
        type=float,
        default=None,
        help=(
            "Only reset entries for maps whose ctime is >= START_TIME "
            "(unix timestamp)."
        ),
    )

    parser.add_argument(
        "--end-time",
        type=float,
        default=None,
        help=(
            "Only reset entries for maps whose ctime is <= END_TIME "
            "(unix timestamp)."
        ),
    )

    parser.add_argument(
        "--from-status",
        type=str,
        default=None,
        help="Only reset entries that currently have this processing status.",
    )

    args = parser.parse_args()

    core(session=settings.session, args=args)
