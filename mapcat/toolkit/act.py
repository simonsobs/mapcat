"""
Create objects from an ACT depth 1 map file.
"""

import h5py

from pathlib import Path
from mapcat.database import DepthOneMapTable, TODDepthOneTable
# from astropy import units as u
# from astropy.coordinates import SkyCoord

def extract_string(input) -> str:
    return str(input).replace("b'", "").replace("'", "")

def parse_info_file(path: Path) -> dict:
    with h5py.File(path, "r") as f:
        return {
            "frequency": extract_string(f["band"][...])[1:],
            "tube_slot": extract_string(f["detset"][...]),
            "observations": [extract_string(x) for x in f["ids"][...]],
            "start_time": f["period"][0],
            "stop_time": f["period"][1],
            "ctime": float(f["t"][...]),
            "box": f["box"][...]
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

    return {
        x: str(y.relative_to(relative_to)) for x, y in paths.items() if y.exists()
    }


def create_objects(base: str, relative_to: Path) -> DepthOneMapTable:
    filenames = parse_filenames(base=base, relative_to=relative_to)
    file_info = parse_info_file(path=relative_to / filenames["info"])

    tods = [
        TODDepthOneTable(
            obs_id=obs_id,
            pwv=None,
            ctime=float(obs_id[4:14]),
            telescope="lat",
            tube_slot=file_info["tube_slot"],
            frequency=file_info["frequency"],
        )
        for obs_id in file_info["observations"]
    ]

    depth_one_map = DepthOneMapTable(
        map_name=filenames["map"].replace("_map.fits", ""),
        map_path=filenames["map"],
        ivar_path=filenames.get("ivar"),
        time_path=filenames.get("time"),
        tube_slot=file_info["tube_slot"],
        frequency=file_info["frequency"],
        ctime=file_info["ctime"],
        start_time=file_info["start_time"],
        stop_time=file_info["stop_time"],
        tods=tods
    )

    return depth_one_map

def glob(input_glob: str, relative_to: Path) -> list[DepthOneMapTable]:
    maps = []

    for map_file in relative_to.glob(input_glob):
        base = str(map_file).replace("_map.fits", "")
        depth_one_map = create_objects(
            base=base, relative_to=relative_to
        )
        maps.append(depth_one_map)

    return maps


def main():
    import sys
    from mapcat.helper import settings

    with settings.session() as session:
        maps = glob(sys.argv[1], Path(sys.argv[2]))
        session.add_all(maps)
        session.commit()


    


