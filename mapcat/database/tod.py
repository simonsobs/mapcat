"""
Table for TODs
"""

from datetime import datetime

import uuid7 as uuid
from astropy.time import Time
from astropydantic import AstroPydanticTime
from sqlmodel import Field, Relationship, SQLModel

from .depth_one_map import DepthOneMapTable
from .links import TODToMapTable


class TODDepthOne(SQLModel):
    tod_id: uuid.UUID
    obs_id: str
    pwv: float | None
    ctime: AstroPydanticTime
    start_time: AstroPydanticTime | None
    stop_time: AstroPydanticTime | None
    nsamples: int | None
    telescope: str
    telescope_flavor: str | None
    tube_slot: str
    tube_flavor: str | None
    frequency: str
    scan_type: str
    subtype: str
    wafer_count: int
    duration: float
    az_center: float
    az_throw: float
    el_center: float
    el_throw: float
    roll_center: float
    roll_throw: float
    wafer_slots_list: str
    stream_ids_list: str


class TODDepthOneTable(SQLModel, table=True):
    """
    Table of TODs used in making depth 1 maps.

    Attributes
    ----------
    tod_id : uuid.UUID
        Unique TOD identifier. Internal to SO
    map_name : str
        Name of map this TOD went into. Foreign key
    obs_id : str
        SO ID of TOD
    pwv : float
        Precipitable  water vapor at time of obs
    ctime : datetime
        Mean unix time of obs
    start_time : datetime
        Start time of obs
    stop_time : datetime
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
    tod_id: uuid.UUID = Field(default_factory=uuid.create, primary_key=True)
    obs_id: str = Field(nullable=False)
    pwv: float | None = Field(index=True, nullable=True)
    ctime: datetime = Field(index=True, nullable=False)
    start_time: datetime | None = Field(index=True, nullable=True)
    stop_time: datetime | None = Field(index=True, nullable=True)
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

    def to_model(self) -> TODDepthOne:
        """
        Return an TODDepthOne model from this table entry.

        Returns
        -------
        TODDepthOne : TODDepthOne
             The TODDepthOne model corresponding to this table entry.
        """
        return TODDepthOne(
            tod_id=self.tod_id,
            obs_id=self.obs_id,
            pwv=self.pwv,
            ctime=Time(self.ctime),
            start_time=Time(self.start_time),
            stop_time=Time(self.stop_time),
            nsamples=self.nsamples,
            telescope=self.telescope,
            telescope_flavor=self.telescope_flavor,
            tube_slot=self.tube_slot,
            tube_flavor=self.tube_flavor,
            frequency=self.frequency,
            scan_type=self.scan_type,
            subtype=self.subtype,
            wafer_count=self.wafer_count,
            duration=self.duration,
            az_center=self.az_center,
            az_throw=self.az_throw,
            el_center=self.el_center,
            el_throw=self.el_throw,
            roll_center=self.roll_center,
            roll_throw=self.roll_throw,
            wafer_slots_list=self.wafer_slots_list,
            stream_ids_list=self.stream_ids_list,
        )
