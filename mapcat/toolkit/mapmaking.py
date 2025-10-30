from pathlib import Path

import h5py

from sqlalchemy.orm import Session
from sqlalchemy import select

from mapcat.database import (
    DepthOneMapTable,
    TODDepthOneTable,
)


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
    """

    stmt = select(TODDepthOneTable).where(TODDepthOneTable.obs_id == obs_id)

    tods = session.execute(stmt)

    tods = tods.scalars().all()
    if len(tods) == 0:  # pragma: no cover
        raise ValueError(f"No TODs with obs ID {obs_id} found.")

    depth_one_maps = [tod.maps for tod in tods][0]
    return depth_one_maps


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

    return tuple((map_dict, no_map_list))
