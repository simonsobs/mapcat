"""
Table for TODs
"""

from sqlmodel import Field, Relationship, SQLModel

from .depth_one_map import DepthOneMapTable
from .links import TODToMapTable


class TODDepthOneTable(SQLModel, table=True):
    """
    Table of TODs used in making depth 1 maps.

    Attributes
    ----------
    id : int
        Unique TOD identifier. Internal to SO
    map_name : str
        Name of map this TOD went into. Foreign key
    obs_id : str
        SO ID of TOD
    pwv : float
        Precipitable  water vapor at time of obs
    ctime : float
        Mean unix time of obs
    start_time : float
        Start time of obs
    stop_time : float
        End time of obs
    nsamples : int
        Number of samps in obs
    telescope : str
        Telescope making obs
    telescope_flavor : str
        Telescope LF/MF/UHF. Only for SATs
    tube_slot : str
        Tube of obs. Only for LAT
    tube_flavor : str
        LF/MF/UHF of tube. Only for LAT
    frequency : str
        Frequency of obs
    scan_type : str
        Type of scan.
    subtype : str
        Subtype of scan
    wafer_count : int
        Number of working wafers for scan
    duration : float
        Duration of scan in seconds
    az_center : float
        Az center of scan
    az_throw : float
        Az throw of scan
    el_center : float
        El center of scan
    el_throw : float
        El throw of scan
    roll_center : float
        Roll center of scan
    roll_throw : float
        Roll throw of scan
    wafer_slots_list : str
        List of live wafers for scan
    stream_ids_list : str
        Stream IDs live for scan
    """

    __tablename__ = "tod_depth_one"
    tod_id: int = Field(primary_key=True)
    obs_id: str = Field(nullable=False)
    pwv: float | None = Field(index=True, nullable=True)
    ctime: float = Field(index=True, nullable=False)
    start_time: float | None = Field(index=True, nullable=True)
    stop_time: float | None = Field(index=True, nullable=True)
    nsamples: int | None = Field()
    telescope: str = Field(index=True, nullable=False)
    telescope_flavor: str | None = Field()
    tube_slot: str = Field()
    tube_flavor: str | None = Field()
    frequency: str = Field(index=True, nullable=False)
    scan_type: str = Field()
    subtype: str = Field()
    wafer_count: int = Field(index=True, nullable=False)
    duration: float = Field()
    az_center: float = Field()
    az_throw: float = Field()
    el_center: float = Field()
    el_throw: float = Field()
    roll_center: float = Field()
    roll_throw: float = Field()
    wafer_slots_list: str = Field(nullable=False)
    stream_ids_list: str = Field(nullable=False)
    maps: list[DepthOneMapTable] = Relationship(
        back_populates="tods", link_model=TODToMapTable
    )
