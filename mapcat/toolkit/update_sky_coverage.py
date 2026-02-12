import numpy as np
from pixell import enmap

from mapcat.database.depth_one_map import DepthOneMapTable
from mapcat.database.sky_coverage import SkyCoverageTable


def get_sky_coverage(tmap: enmap.enmap) -> list:
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


def coverage_from_depthone(d1map: DepthOneMapTable) -> list[SkyCoverageTable]:
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

    tmap = enmap.read_map(d1map.mean_time_path)

    coverage_tiles = get_sky_coverage(tmap)

    return [
        SkyCoverageTable(x=tile[0], y=tile[1], map=d1map, map_id=d1map.map_id)
        for tile in coverage_tiles
    ]


def main():
    from mapcat.helper import settings

    with settings.session() as session:
        d1maps = (
            session.query(DepthOneMapTable)
            .outerjoin(
                SkyCoverageTable, SkyCoverageTable.map_id == DepthOneMapTable.map_id
            )
            .filter(SkyCoverageTable.map_id.is_(None))
            .all()
        )
        for d1map in d1maps:
            print(d1map)
            SkyCov = coverage_from_depthone(d1map)
            d1map.depth_one_sky_coverage = SkyCov
            session.add(d1map)
            session.commit()
