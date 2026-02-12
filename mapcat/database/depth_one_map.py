"""
Depth one map table.
"""

from typing import TYPE_CHECKING, Any

from sqlmodel import JSON, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .depth_one_coadd import DepthOneCoaddTable
    from .pipeline_information import PipelineInformationTable
    from .pointing_residual import PointingResidualTable
    from .sky_coverage import SkyCoverageTable
    from .time_domain_processing import TimeDomainProcessingTable
    from .tod import TODDepthOneTable

from .links import DepthOneToCoaddTable, TODToMapTable


class DepthOneMapTable(SQLModel, table=True):
    """
    A depth-1 map.

    Attributes
    ----------
    id : int
        Unique map identifiers. Internal to SO
    map_name : str
        Name of depth 1 map
    map_path : str
        Non-localized path to intensity map
    ivar_path : str | None
        Non-localized path to inverse-variance map
    rho_path: str | None
        Non-localized path to the match-filtered 'rho' map
    kappa_path: str | None
        Non-localized path to the match-filtered 'kappa' map
    start_time_path : str
        Non-localized path to the start time map. Each pixel represents
        the earliest time the pixel was observed.
    mean_time_path : str
        Non-localized path to the mean time map. If there is only
        one time map available, this should be it.
    end_time_path : str
        Non-localized path to the start time map. Each pixel represents
        the earliest time the pixel was observed.
    tube_slot : str
        OT for map
    wafers : str
        Standardized names of wafers used in this map
    frequency : str
        Frequency channel of map
    ctime : float
        Mean unix time of map
    start_time : float
        Start unix time of map
    stop_time : float
        Stop unix time of map
    processing_status : list[TimeDomainProcessingTable]
        List of processing status tables associated with d1 map
    pointing_residual : list[PointingResidualTable]
        List of pointing residual table associated with d1 map
    tods: list[TODDepthOneTable]
        List of tods associated with d1 map
    pipeline_information: list[PipelineInformationTable]
        List of pipeline info associed with d1 map
    depth_one_sky_coverage : list[SkyCoverageTable]
        List of sky coverage patches for d1 map.
    box : list[float]
        Bounding box of map in format [[dec_min, ra_max], [dec_max, ra_min]], units in radians.
    notes: dict[str, Any]
        JSON entry that holds additional information about the d1 maps
    """

    __tablename__ = "depth_one_maps"

    map_id: int = Field(primary_key=True)
    map_name: str = Field(index=True, unique=True, nullable=False)

    map_path: str
    ivar_path: str | None
    rho_path: str | None = None
    kappa_path: str | None = None

    start_time_path: str | None = None
    mean_time_path: str | None
    end_time_path: str | None = None

    tube_slot: str = Field(index=True, nullable=False)
    frequency: str = Field(index=True, nullable=False)
    ctime: float = Field(index=True, nullable=False)
    start_time: float = Field(index=True, nullable=False)
    stop_time: float = Field(index=True, nullable=False)

    processing_status: list["TimeDomainProcessingTable"] = Relationship(
        back_populates="map",
        cascade_delete=True,
    )
    pointing_residual: list["PointingResidualTable"] = Relationship(
        back_populates="map",
        cascade_delete=True,
    )
    tods: list["TODDepthOneTable"] = Relationship(
        back_populates="maps",
        link_model=TODToMapTable,
    )
    pipeline_information: list["PipelineInformationTable"] = Relationship(
        back_populates="map",
        cascade_delete=True,
    )
    depth_one_sky_coverage: list["SkyCoverageTable"] = Relationship(
        back_populates="map",
        cascade_delete=True,
    )
    coadds: list["DepthOneCoaddTable"] = Relationship(
        back_populates="maps",
        link_model=DepthOneToCoaddTable,
    )
    box: list[float]
    notes: dict[str, Any] | None = Field(default=None, sa_type=JSON)
