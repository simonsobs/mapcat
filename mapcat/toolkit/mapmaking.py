from sqlalchemy import select
from sqlalchemy.orm import Session

from mapcat.database import DepthOneMapTable, TODDepthOneTable


def maps_containing_obs(obs_id: str, session: Session) -> list[DepthOneMapTable]:
    """
    Function for finding maps that an obs_id is in.

    Parameters
    ----------
    obs_id : str
        Obs id to get the map for
    session : Session
        Session to use

    Returns
    -------
    depth_one_maps : list[DepthOneMapTable]
        Table of depth one maps corresponding to the obs_id

    Raises
    ------
    ValueError
        If no tods with specified obs_id are found
    """

    stmt = select(TODDepthOneTable).where(TODDepthOneTable.obs_id == obs_id)

    tod = session.execute(stmt)

    tod = tod.scalars().all()
    if len(tod) == 0:  # pragma: no cover
        raise ValueError(f"No TODs with obs ID {obs_id} found.")

    return tod[0].maps


def build_obslists(
    obs_ids: list[str], session: Session
) -> tuple[list[DepthOneMapTable], list[str]]:
    """
    For a list of obs_ids, get the maps associated with each obs_id and also return whichever obs_ids do not have associated maps.

    Parameters
    ----------
    obs_ids : list[str]
        Obs_ids to get maps for
    session : Session
        Session to use

    Returns
    -------
    obs_mapping : tuple[list[DepthOneMapTable], list[str]]
        Tuple containing a list of depth one maps containing obs_id from obs_ids and a list of all obs_id without corresponding maps.
    """

    map_dict = {}
    no_map_list = []
    with session.begin():
        for obs_id in obs_ids:
            map_list = maps_containing_obs(obs_id=obs_id, session=session)
            if len(map_list) == 0:
                no_map_list.append(obs_id)
            else:
                map_dict[obs_id] = map_list

    return (map_dict, no_map_list)
