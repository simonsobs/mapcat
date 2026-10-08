import argparse
from collections.abc import Iterator
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
    path : Path
        The local path to the tmap for the depth one map

    Raises
    ------
    ValueError
        If the map has no mean time path.
    """
    if d1table.mean_time_path is None:
        raise ValueError(f"No mean time map available for {d1table.map_name}")
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

    Raises
    ------
    ValueError
        If RA is not finite.
    """
    if not np.isfinite(ra):
        raise ValueError("RA must be finite")
    return int(_tile_floor((ra % 360) / 10)) % 36


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

    Raises
    ------
    ValueError
        If Dec is nonfinite or outside [-90, 90].
    """
    if not np.isfinite(dec) or not -90 <= dec <= 90:
        raise ValueError("Dec must be between -90 and 90 degrees")
    return min(int(_tile_floor((dec + 90) / 10)), 17)


def _tile_floor(values):
    """Stabilize exact tile boundaries against FITS WCS floating-point noise."""
    nearest = np.rint(values)
    return np.floor(np.where(np.abs(values - nearest) < 1e-10, nearest, values))


def _observed_pixel_coordinates(
    tmap: enmap.ndmap,
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    """Yield observed pixel rows and columns, processing 128 rows at a time.

    A pixel is observed if any component has a finite, nonzero value.
    Returned row numbers refer to the full map, not the current block.
    """
    for first_row in range(0, tmap.shape[-2], 128):
        block = np.asarray(tmap[..., first_row : first_row + 128, :])
        observed = np.isfinite(block) & (block != 0)
        component_axes = tuple(range(observed.ndim - 2))
        if component_axes:
            observed = np.any(observed, axis=component_axes)

        rows, columns = np.nonzero(observed)
        if rows.size:
            yield rows + first_row, columns


def _separable_car_axes(
    tmap: enmap.ndmap,
) -> tuple[np.ndarray, np.ndarray] | None:
    """Cache Dec per row and RA per column for unrotated equatorial CAR maps.

    Each sky tile is a rectangle of rows and columns for these maps, even
    when either pixel axis is reversed. Return None for other geometries.
    """
    wcs = tmap.wcs.wcs
    if list(wcs.ctype) != ["RA---CAR", "DEC--CAR"] or wcs.crval[1] != 0:
        return None

    # Off-diagonal matrix terms mix rows and columns, preventing this shortcut.
    pixel_matrix = wcs.get_pc()
    if not np.all(pixel_matrix == np.diag(np.diag(pixel_matrix))):
        return None

    nrows, ncolumns = tmap.shape[-2:]
    dec_by_row = np.rad2deg(
        enmap.pix2sky(
            tmap.shape, tmap.wcs, [np.arange(nrows), np.zeros(nrows)], safe=False
        )[0]
    )
    ra_by_column = np.rad2deg(
        enmap.pix2sky(
            tmap.shape, tmap.wcs, [np.zeros(ncolumns), np.arange(ncolumns)], safe=False
        )[1]
    )
    return dec_by_row, ra_by_column


def _sky_coordinates_to_tiles(
    dec_degrees: np.ndarray,
    ra_degrees: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Convert valid celestial coordinates into RA and Dec tile indices.

    RA wraps around the sky. Dec is offset by 90 degrees to index from the
    south pole; clipping keeps the north pole in the final tile. Boundary
    rounding uses the same tolerance as the scalar coordinate helpers.
    """
    valid = (
        np.isfinite(ra_degrees) & np.isfinite(dec_degrees) & (np.abs(dec_degrees) <= 90)
    )
    ra_tiles = _tile_floor((ra_degrees[valid] % 360) / 10).astype(int) % 36
    dec_tiles = np.clip(_tile_floor((dec_degrees[valid] + 90) / 10).astype(int), 0, 17)
    return ra_tiles, dec_tiles


def _coverage_for_nonseparable_wcs(tmap: enmap.ndmap) -> list[tuple[int, int]]:
    """Handle projections where a sky tile is not a pixel-axis rectangle."""
    covered_tiles = np.zeros((36, 18), dtype=bool)
    for rows, columns in _observed_pixel_coordinates(tmap):
        dec_degrees, ra_degrees = np.rad2deg(
            enmap.pix2sky(tmap.shape, tmap.wcs, [rows, columns], safe=False)
        )
        ra_tiles, dec_tiles = _sky_coordinates_to_tiles(dec_degrees, ra_degrees)
        covered_tiles[ra_tiles, dec_tiles] = True

    ra_tiles, dec_tiles = np.nonzero(covered_tiles)
    return [(int(ra), int(dec)) for ra, dec in zip(ra_tiles, dec_tiles)]


def get_sky_coverage(tmap: enmap.ndmap) -> list[tuple[int, int]]:
    """Return sorted 10-degree tiles containing finite, nonzero pixel centers.

    For unrotated equatorial CAR maps, including ACT, loop over RA and Dec
    tiles and check their pixel rectangles. Select rows and columns by their
    WCS coordinates rather than submap rounding or assumed axis directions.
    Leading component axes are combined: any observed component marks a pixel.
    Other projections use a pixel-coordinate fallback.

    Parameters
    ----------
    tmap : enmap.ndmap
        Coverage map with celestial WCS and at least two spatial axes.

    Returns
    -------
    list
        Unique (RA, Dec) tile indices, with 0 <= RA < 36 and 0 <= Dec < 18.

    Raises
    ------
    ValueError
        If the map has fewer than two axes.
    """
    if tmap.ndim < 2:
        raise ValueError("Coverage maps must have at least two spatial axes")

    coordinate_axes = _separable_car_axes(tmap)
    if coordinate_axes is None:
        return _coverage_for_nonseparable_wcs(tmap)
    dec_by_row, ra_by_column = coordinate_axes

    # Assign pixel centers to tiles. Modulo wraps RA without rotating the sky.
    valid_ra = np.isfinite(ra_by_column)
    valid_dec = np.isfinite(dec_by_row) & (np.abs(dec_by_row) <= 90)
    column_tiles = np.full(ra_by_column.shape, -1, dtype=int)
    row_tiles = np.full(dec_by_row.shape, -1, dtype=int)
    column_tiles[valid_ra] = (
        _tile_floor((ra_by_column[valid_ra] % 360) / 10).astype(int) % 36
    )
    row_tiles[valid_dec] = np.clip(
        _tile_floor((dec_by_row[valid_dec] + 90) / 10).astype(int), 0, 17
    )

    tiles = []
    for ra_idx in np.unique(column_tiles[valid_ra]):
        columns = np.flatnonzero(column_tiles == ra_idx)
        for dec_idx in np.unique(row_tiles[valid_dec]):
            rows = np.flatnonzero(row_tiles == dec_idx)
            submap = np.asarray(tmap[..., rows[:, None], columns])
            if np.any(np.isfinite(submap) & (submap != 0)):
                tiles.append((int(ra_idx), int(dec_idx)))

    return tiles


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


def core(session, *, replace: bool = False):
    """
    Core function for updating the sky coverage table. For each depth one map that does not have any associated sky coverage tiles, compute the sky coverage tiles and add them to the database.

    Parameters
    ----------
    session : sessionmaker
        A SQLAlchemy sessionmaker to use for database access.
    replace : bool, optional
        Recompute existing coverage as well, replacing it in one transaction.
    """
    with session() as cur_session:
        query = cur_session.query(DepthOneMapTable)
        if not replace:
            query = query.outerjoin(
                SkyCoverageTable, SkyCoverageTable.map_id == DepthOneMapTable.map_id
            ).filter(SkyCoverageTable.map_id.is_(None))
        for d1map in query.all():
            SkyCov = coverage_from_depthone(d1map)
            if replace:
                cur_session.query(SkyCoverageTable).filter_by(
                    map_id=d1map.map_id
                ).delete(synchronize_session=False)
            cur_session.add_all(SkyCov)

        cur_session.commit()


def main():
    parser = argparse.ArgumentParser(
        description="Generate sky coverage from time maps."
    )
    parser.add_argument(
        "--replace", action="store_true", help="Recompute and replace existing coverage"
    )
    args = parser.parse_args()
    core(session=settings.session, replace=args.replace)
