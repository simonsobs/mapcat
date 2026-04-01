from pathlib import Path

import numpy as np
from pixell import enmap

from mapcat.database.depth_one_map import DepthOneMapTable
from mapcat.database.sky_coverage import SkyCoverageTable
from mapcat.helper import settings


def resolve_tmap(d1table: DepthOneMapTable) -> Path:
    """
    Resolve the local path to a tmap from a d1 table.

    Parameters
    ----------
    d1table : DepthOneMapTable
        The depth one map table to resolve the tmap for

    Returns
    -------
    ettings.depth_one_parent / d1table.mean_time_path : Path
        The local path to the tmap for the depth one map
    """
    return settings.depth_one_parent / d1table.mean_time_path


def index_to_skybox(ra_idx: int, dec_idx: int) -> np.ndarray:
    """
    Convert a sky coverage tile index to a sky box in radians

    Parameters
    ----------
    ra_idx : int
        The RA index of the sky coverage tile
    dec_idx : int
        The Dec index of the sky coverage tile

    Returns
    -------
    skybox : np.ndarray
        A 2x2 array containing the corners of the sky box in radians, in the format [[dec_min, ra_max], [dec_max, ra_min]]
    """
    ra_min = ra_idx * 10
    ra_max = ra_min + 10
    dec_min = (dec_idx - 9) * 10
    dec_max = dec_min + 10

    return np.array(
        [
            [np.deg2rad(dec_min), np.deg2rad(ra_max)],
            [np.deg2rad(dec_max), np.deg2rad(ra_min)],
        ]
    )


def ra_to_index(ra: float) -> int:
    """
    Convert an ra in degrees to a sky coverage tile index

    Parameters
    ----------
    ra : float
        The ra in degrees to convert

    Returns
    -------
    idx : int
        The sky coverage tile index corresponding to the input ra
    """
    return int(np.floor(ra / 10))


def dec_to_index(dec: float) -> int:
    """
    Convert a dec in degrees to a sky coverage tile index

    Parameters
    ----------
    dec : float
        The dec in degrees to convert

    Returns
    -------
    idx : int
        The sky coverage tile index corresponding to the input dec
    """
    return int(np.floor(dec / 10)) + 9


def _ra_to_index_pixell(ra: float) -> int:
    """
    Convert an ra in degrees to a sky coverage tile index using the
    pixell convention where -180 < ra < 180. You should probably
    not ever touch this function.

    Parameters
    ----------
    ra : float
        The ra in degrees to convert

    Returns
    -------
    idx : int
        The sky coverage tile index corresponding to the input ra
    """
    return int(np.floor(ra / 10)) + 18


def get_sky_coverage(tmap: enmap.ndmap) -> list:
    """
    Given the time map of a depth1 map, return the list
    of sky coverage tiles that cover that map

    Parameters
    ----------
    tmap : enmap.enmap
        The time map of the depth-one map. Pixels that were observed have non-zero values.

    Returns
    -------
    tiles : list
        A list of sky coverage tiles that cover the map
    """
    box = tmap.box()

    dec_min, ra_max = np.rad2deg(box[0])
    dec_max, ra_min = np.rad2deg(box[1])

    dec_min = np.floor(dec_min / 10) * 10
    dec_max = np.ceil(dec_max / 10) * 10
    ra_min = np.floor(ra_min / 10) * 10
    ra_max = np.ceil(ra_max / 10) * 10
    ra_min += 180  # Convert from pixel standard to normal RA convention
    ra_max += 180

    ras = np.arange(ra_min, ra_max, 10)
    decs = np.arange(dec_min, dec_max, 10)

    ra_idx = []
    dec_idx = []

    for ra in ras:
        for dec in decs:
            ra_id = ra_to_index(ra)
            dec_id = dec_to_index(dec)
            skybox = index_to_skybox(ra_id, dec_id)
            skybox[..., 1] -= np.pi  # Convert from standard RA to pixell convention
            submap = enmap.submap(tmap, skybox)
            if np.any(submap):
                ra_idx.append(ra_id)
                dec_idx.append(dec_id)

    return list(zip(ra_idx, dec_idx))


def coverage_from_depthone(d1table: DepthOneMapTable) -> list[SkyCoverageTable]:
    """
    Get the list of sky coverage tiles that cover a given depth one map

    Parameters
    ----------
    d1map : DepthOneMapTable
        The depth one map to get the sky coverage for

    Returns
    -------
    tiles : list[SkyCoverageTable]
        A list of sky coverage tiles that cover the map
    """
    tmap_path = resolve_tmap(d1table)
    tmap = enmap.read_map(str(tmap_path))

    coverage_tiles = get_sky_coverage(tmap)

    return [
        SkyCoverageTable(x=tile[0], y=tile[1], map_id=d1table.map_id)
        for tile in coverage_tiles
    ]


def core(session):
    """
    Core function for updating the sky coverage table. For each depth one map that does not have any associated sky coverage tiles, compute the sky coverage tiles and add them to the database.

    Parameters
    ----------
    session : sessionmaker
        A SQLAlchemy sessionmaker to use for database access.
    """
    with session() as cur_session:
        d1maps = (
            cur_session.query(DepthOneMapTable)
            .outerjoin(
                SkyCoverageTable, SkyCoverageTable.map_id == DepthOneMapTable.map_id
            )
            .filter(SkyCoverageTable.map_id.is_(None))
            .all()
        )
        for d1map in d1maps:
            SkyCov = coverage_from_depthone(d1map)
            cur_session.add_all(SkyCov)

        cur_session.commit()


def main():
    core(session=settings.session)
