from astropy.coordinates import ICRS
from sqlalchemy import select
from sqlalchemy.orm import Session

from mapcat.database import DepthOneMapTable
from mapcat.toolkit.update_sky_coverage import dec_to_index, ra_to_index


def get_maps_by_coverage(
    position: ICRS,
    session: Session,
) -> list[DepthOneMapTable]:
    """
    Get the depth one maps that cover a given position.

    Parameters
    ----------
    position : ICRS
        The position to query for coverage. Should be in ICRS coordinates.
    session : Session
        The database session to use for the query.

    Returns
    -------
    session.execute(stmt).scalars().all() : list[DepthOneMapTable]
        A list of depth one maps that cover the given position.

    Raises
    ------
    ValueError
        If the RA or Dec of the position is out of bounds.
    """
    ra = position.ra.deg
    dec = position.dec.deg

    # These aren't covered since ICRS automatically wraps
    # values back aground to 0-360 for RA and -90 to 90 for Dec.
    if ra < 0 or ra > 360:  # pragma: no cover
        raise ValueError("RA must be between 0 and 360 degrees")
    if dec < -90 or dec > 90:  # pragma: no cover
        raise ValueError("Dec must be between -90 and 90 degrees")

    ra_idx = ra_to_index(ra)
    dec_idx = dec_to_index(dec)

    stmt = (
        select(DepthOneMapTable)
        .join(DepthOneMapTable.depth_one_sky_coverage)
        .filter_by(x=ra_idx, y=dec_idx)
    )

    return session.execute(stmt).scalars().all()
