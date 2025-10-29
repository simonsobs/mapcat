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

    with session.begin():
        stmt = select(TODDepthOneTable).where(TODDepthOneTable.obs_id == obs_id)

        tods = session.execute(stmt)

    if len(tods) == 0:
        raise ValueError(f"No TODs with obs ID {obs_id} found.")
    # TODO: is an obs_id unique to a TOD?
    # if len(tod) > 1:
    #    raise ValueError(f"More than one TOD with obs ID {obs_id} found.")
    depth_one_maps = [tod.maps for tod in tods]
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
    for obs_id in obs_ids:
        try:
            map_dict[obs_id] = maps_containing_obs(obs_id=obs_id, session=session)
        except ValueError:
            no_map_list.append(obs_id)

    return tuple((map_dict, no_map_list))
