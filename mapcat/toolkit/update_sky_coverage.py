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
    tmap_path : Path
        The local path to the tmap for the depth one map
    """
    tmap_path = settings.depth_one_parent / d1table.mean_time_path
    return tmap_path


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

    ras = np.arange(ra_min, ra_max, 10)
    decs = np.arange(dec_min, dec_max, 10)

    ra_idx = []
    dec_id = []

    for ra in ras:
        for dec in decs:
            skybox = np.array(
                [
                    [np.deg2rad(dec), np.deg2rad(ra + 10)],
                    [np.deg2rad(dec + 10), np.deg2rad(ra)],
                ]
            )
            submap = enmap.submap(tmap, skybox)
            if np.any(submap):
                ra_idx.append(int(ra / 10))
                dec_id.append(int(dec / 10) + 9)

    return list(zip(ra_idx, dec_id))


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
    with session() as session:
        d1maps = (
            session.query(DepthOneMapTable)
            .outerjoin(
                SkyCoverageTable, SkyCoverageTable.map_id == DepthOneMapTable.map_id
            )
            .filter(SkyCoverageTable.map_id.is_(None))
            .all()
        )
        for d1map in d1maps:
            SkyCov = coverage_from_depthone(d1map)
            session.add_all(SkyCov)

        session.commit()


def main():
    core(session=settings.session)
