"""
Depth one map table.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

import uuid7 as uuid
from astropy.time import Time
from astropydantic import AstroPydanticTime
from sqlmodel import JSON, Field, Relationship, SQLModel

if TYPE_CHECKING:  # pragma: no cover
    from .depth_one_coadd import DepthOneCoaddTable
    from .pipeline_information import PipelineInformationTable
    from .pointing_residual import PointingResidualTable
    from .sky_coverage import SkyCoverageTable
    from .time_domain_processing import TimeDomainProcessingTable
    from .tod import TODDepthOneTable

from .links import DepthOneToCoaddTable, TODToMapTable


class DepthOneMap(SQLModel):
    map_id: uuid.UUID
    map_name: str

    map_path: str | None
    ivar_path: str | None
    rho_path: str | None
    kappa_path: str | None
    flux_path: str | None
    snr_path: str | None

    start_time_path: str | None
    mean_time_path: str | None
    end_time_path: str | None

    tube_slot: str
    frequency: str
    ctime: AstroPydanticTime
    start_time: AstroPydanticTime
    stop_time: AstroPydanticTime


class DepthOneMapTable(SQLModel, table=True):
    """
    A depth-1 map.

    Attributes
    ----------
    id : uuid.UUID
        Unique map identifiers. Internal to SO
    map_name : str
        Name of depth 1 map
    map_path : str | None
        Non-localized path to intensity map
    ivar_path : str | None
        Non-localized path to inverse-variance map
    rho_path: str | None
        Non-localized path to the match-filtered 'rho' map
    kappa_path: str | None
        Non-localized path to the match-filtered 'kappa' map
    flux_path: str | None
        Non-localized path to the flux map.
    snr_path: str | None
        Non-localized path to the signal-to-noise map.
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
    ctime : datetime
        Mean unix time of map
    start_time : datetime
        Start unix time of map
    stop_time : datetime
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

    notes: dict[str, Any]
        JSON entry that holds additional information about the d1 maps
    """

    __tablename__ = "depth_one_maps"

    map_id: uuid.UUID = Field(default_factory=uuid.create, primary_key=True)
    map_name: str = Field(index=True, unique=True, nullable=False)

    map_path: str | None = None
    ivar_path: str | None = None
    rho_path: str | None = None
    kappa_path: str | None = None
    flux_path: str | None = None
    snr_path: str | None = None

    start_time_path: str | None = None
    mean_time_path: str | None
    end_time_path: str | None = None

    tube_slot: str = Field(index=True, nullable=False)
    frequency: str = Field(index=True, nullable=False)
    ctime: datetime = Field(index=True, nullable=False)
    start_time: datetime = Field(index=True, nullable=False)
    stop_time: datetime = Field(index=True, nullable=False)

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
    notes: dict[str, Any] | None = Field(default=None, sa_type=JSON)

    @property
    def coverage_path(self) -> str:
        """
        Return a path to a map that can be used for coverage checking.
        This is required because we generally use the intensity map for
        coverage checking but it is not always available. We return the
        first available of: intensity, rho, flux.

        Raises
        ------
        ValueError
            If no coverage-compatible map path is available.
        """

        if self.map_path is not None:
            return self.map_path
        if self.rho_path is not None:
            return self.rho_path
        if self.flux_path is not None:
            return self.flux_path
        raise ValueError(
            f"No coverage map available for map {self.map_name} (id {self.map_id})"
        )

    def to_model(self) -> DepthOneMap:
        """
        Return an DepthOneMap model from this table entry.

        Returns
        -------
        DepthOneMap : DepthOneMap
             The DepthOneMap model corresponding to this table entry.
        """
        return DepthOneMap(
            map_id=self.map_id,
            map_name=self.map_name,
            map_path=self.map_path,
            ivar_path=self.ivar_path,
            rho_path=self.rho_path,
            kappa_path=self.kappa_path,
            flux_path=self.flux_path,
            snr_path=self.snr_path,
            start_time_path=self.start_time_path,
            mean_time_path=self.mean_time_path,
            end_time_path=self.end_time_path,
            tube_slot=self.tube_slot,
            frequency=self.frequency,
            ctime=Time(self.ctime),
            start_time=Time(self.start_time),
            stop_time=Time(self.stop_time),
        )
