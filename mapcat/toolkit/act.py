"""
Create objects from an ACT depth 1 map file.
"""

from pathlib import Path

import h5py

from mapcat.database import DepthOneMapTable, TODDepthOneTable

# from astropy import units as u
# from astropy.coordinates import SkyCoord


def extract_string(input: bytes) -> str:
    return str(input).replace("b'", "").replace("'", "")


def parse_info_file(path: Path) -> dict:
    with h5py.File(path, "r") as f:
        if "band" in f and "detset" in f:
            ## backward compatibility with old SO format
            return {
                "frequency": extract_string(f["band"][...])[1:],
                "tube_slot": extract_string(f["detset"][...]),
                "observations": [extract_string(x) for x in f["ids"][...]],
                "start_time": f["period"][0],
                "stop_time": f["period"][1],
                "ctime": float(f["t"][...]),
                "box": f["box"][...],
            }
        else:
            ## ACT depth1 format.
            return {
                "frequency": extract_string(f["array"][...]).split("_")[1],
                "tube_slot": extract_string(f["array"][...]).split("_")[0],
                "observations": [extract_string(x) for x in f["ids"][...]],
                "start_time": f["period"][0],
                "stop_time": f["period"][1],
                "ctime": float(f["t"][...]),
                "box": f["box"][...],
            }


def parse_filenames(base: str, relative_to: Path) -> dict[str, str]:
    """
    Parse a base filename (e.g. /path/base/18234/depth1_182341234_i1_f090)
    into map, info, ivar, time, relative to 'relative_to'.
    """

    paths = {
        "map": Path(base + "_map.fits"),
        "info": Path(base + "_info.hdf"),
        "ivar": Path(base + "_ivar.fits"),
        "time": Path(base + "_time.fits"),
    }

    # In case e.g. there is no inverse-variance map.
    return {x: str(y.relative_to(relative_to)) for x, y in paths.items() if y.exists()}


def create_objects(base: str, relative_to: Path, telescope: str) -> DepthOneMapTable:
    filenames = parse_filenames(base=base, relative_to=relative_to)
    file_info = parse_info_file(path=relative_to / filenames["info"])

    tods = [
        TODDepthOneTable(
            obs_id=obs_id,
            pwv=None,
            ctime=float(obs_id[4:14]),
            telescope=telescope,
            tube_slot=file_info["tube_slot"],
            frequency=file_info["frequency"],
        )
        for obs_id in file_info["observations"]
    ]

    depth_one_map = DepthOneMapTable(
        map_name=filenames["map"].replace("_map.fits", ""),
        map_path=filenames["map"],
        ivar_path=filenames.get("ivar"),
        mean_time_path=filenames.get("time"),
        tube_slot=file_info["tube_slot"],
        frequency=file_info["frequency"],
        ctime=file_info["ctime"],
        start_time=file_info["start_time"],
        stop_time=file_info["stop_time"],
        tods=tods,
    )

    return depth_one_map


def glob(input_glob: str, relative_to: Path, telescope: str) -> list[DepthOneMapTable]:
    maps = []

    for map_file in relative_to.glob(input_glob):
        base = str(map_file).replace("_map.fits", "")
        depth_one_map = create_objects(
            base=base, relative_to=relative_to, telescope=telescope
        )
        maps.append(depth_one_map)

    return maps


HELP_TEXT = """Use this utility to ingest depth-1 maps created by the ACT mapmaker.
This reads the _info.hdf files to extract relevant metadata, such as the TODs
that were used in the file. Uses a glob pattern to ingest items. The glob
should list the '*_map.fits' files, and is relative to the top level directory.
"""

USAGE = """Imagine you have a directory /my/path/to/maps, containing:

17577    17578     17579

Each directory contains multiple maps, e.g.

17577/depth1_1757723727_map.fits
17577/depth1_1757723727_ivar.fits
17577/depth1_1757723727_time.fits
17577/depth1_1757723727_info.hdf
17577/depth1_1757748298_map.fits
17577/depth1_1757748298_ivar.fits
17577/depth1_1757748298_time.fits
17577/depth1_1757748298_info.hdf

You should pass '/my/path/to/maps' as 'relative-to', and
'*/*_map.fits' as the glob pattern.
"""


def main():
    import argparse as ap

    from mapcat.helper import settings

    parser = ap.ArgumentParser(prog="actingest", usage=USAGE, description=HELP_TEXT)

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
        help="Glob pattern below relative-to that lists the _map.fits files",
    )

    parser.add_argument(
        "-t",
        "--telescope",
        type=str,
        default="act",
        help="Telescope label to use (e.g. lat, act)",
    )

    args = parser.parse_args()

    with settings.session() as session:
        maps = glob(args.glob, args.relative_to, args.telescope)
        session.add_all(maps)
        session.commit()
