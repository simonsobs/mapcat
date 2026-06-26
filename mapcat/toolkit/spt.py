"""
Create objects from an SPT single observation maps.
"""

import argparse as ap
from pathlib import Path

import h5py
from sqlalchemy.orm import sessionmaker

from mapcat.database import DepthOneMapTable, TODDepthOneTable


def extract_string(input: bytes) -> str:
    return str(input).replace("b'", "").replace("'", "")


def create_objects(base: str, relative_to: Path) -> DepthOneMapTable:
    tods = []
    obsid, band = base.split('/')[-1].split('_')[:2]
    ## could read in the observation frame, but then
    ## we have to read every map file.
    start_time = int(obsid) + 1483228800 # unix time
    end_time = start_time + 2* 3600 # assume a 2 hour observation for now
    return DepthOneMapTable(
        map_name=base,
        map_path=base + "_tonly.g3.gz",
        tube_slot='all',
        frequency=band,
        ctime=start_time,
        start_time=start_time,
        stop_time=end_time,
        tods=tods,
    )


def glob(input_glob: str, relative_to: Path) -> list[DepthOneMapTable]:
    maps = []

    for map_file in relative_to.glob(input_glob):
        base = str(map_file).replace("_tonly.g3.gz", "")
        depth_one_map = create_objects(
            base=base, relative_to=relative_to,  
        )
        maps.append(depth_one_map)

    return maps


HELP_TEXT = """Use this utility to ingest single observation maps created by the SPT mapmaker.
Uses a glob pattern to ingest items. The glob
should list the '*.g3' files, and is relative to the top level directory.
"""

USAGE = """Imagine you have a directory /my/path/to/maps, containing:

ra0hdec-44.75/ ra0hdec-52.25/ ...

Each directory contains multiple maps, e.g.

ra0hdec-44.75/84864583_90GHz_tonly.g3.gz
ra0hdec-44.75/84864583_150GHz_tonly.g3.gz
ra0hdec-44.75/[spt3g_obsid]_[band]_tonly.g3.gz
...

You should pass '/my/path/to/maps/ra0hdec-44.75' as 'relative-to', and
'*_tonly.g3.gz' as the glob pattern.
or, if you wnat to make a mapcat with only 90GHz maps,
you can pass '*_90GHz_tonly.g3.gz' as the glob pattern.
"""


def core(session: sessionmaker, args: ap.Namespace):
    """
    Driver function for spt.py Takes a session and a arg parser
    and creates DepthOneMapTable objects from the files listed
    matching the glob pattern in the parser and adds them to the
    database in session.

    Parameters
    ----------
    session : sessionmaker
        A SQLAlchemy sessionmaker to use for database access.
    args : argparse.Namespace
       Parsed args with the glob patterns to match.
    """

    with session() as cur_session:
        maps = glob(args.glob, args.relative_to)
        cur_session.add_all(maps)
        cur_session.commit()


def main():
    from mapcat.helper import settings

    parser = ap.ArgumentParser(prog="sptingest", usage=USAGE, description=HELP_TEXT)

    parser.add_argument(
        "-r",
        "--relative-to",
        type=Path,
        required=True,
        help="Base path that maps are relative to",
    )

    parser.add_argument(
        "-g",
        "--glob",
        type=str,
        required=True,
        help="Glob pattern below relative-to that lists the _tonly.g3.gz files",
    )

    args = parser.parse_args()

    core(session=settings.session, args=args)
