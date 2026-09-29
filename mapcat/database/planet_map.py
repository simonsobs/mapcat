"""
Table for planet maps.
"""

from datetime import datetime
from typing import Any, Optional

from astropy.time import Time
from astropydantic import AstroPydanticTime
from sqlalchemy import JSON, Column, ForeignKeyConstraint
from sqlmodel import Field, Relationship, SQLModel


class PlanetMap(SQLModel):
    obs_id: str
    telescope: str
    freq_channel: str
    wafer: str
    ctime: AstroPydanticTime
    source: str

    hit_path: str | None
    map_path: str | None
    weight_path: str | None
    weighted_map_path: str | None

    azimuth: float | None
    elevation: float | None    
    duration: float| None
    pwv: float | None
    pwv_std: float | None
    pwv_p2p: float | None
    pwv_apex: float | None
    pwv_apex_std: float | None
    pwv_apex_p2p: float | None

    f_hwp: float | None
    roll_angle: float | None
    scan_speed: float | None
    scan_acc: float | None
    sun_distance: float | None
    moon_distance: float | None
    wind_speed: float | None
    wind_direction: float | None
    ambient_temperature: float | None
    uv: float | None

    detnum_before_fitselection: int | None
    total_detnum: int | None
    recenter: bool | None
    yc: float | None
    xc: float | None

    Tmap_variance: float | None
    Qmap_variance: float | None
    Umap_variance: float | None

    proc: dict[str, Any] | list[Any] | None = None
    detnum: list[int] | None = None
    detid: list[str] | None = None
    # Main beam fit result
    amplitude: float | None
    peak: float | None
    xo: float | None
    yo: float | None
    sigmax: float | None
    sigmay: float | None
    theta: float | None
    redchit: float | None
    # Leakage beam fit result
    mq: float | None
    d0q: float | None
    d1q: float | None
    sigmaq: float | None
    redchiq: float | None
    mu: float | None
    d0u: float | None
    d1u: float | None
    sigmau: float | None
    redchiu: float | None
    

class PlanetMapTable(SQLModel, table=True):
    """
    A planet map.

    Attributes
    ----------
    obs_id : str
        observation id
    telescope : str
        Telescope 
    freq_channel : str
        frequency channel of map
    wafer : str
        wafer slot
    source : str
        source. eg jupiter
    ctime : datetime
        unix time of map
    hit_path : str
        path of hit map
    map_path : str
        path of map
    weight_path : str
        path of weight
    weighted_map_path : str
        path of weighted_map
    elevation : float
        elevation of telescope
    azimuth : float
        azimuth of telescope
    pwv: float
        mean of precipitable water vapor
    pwv_std: float
        standard deviation of pwv
    pwv_p2p: float
        peak-to-peak of pwv
    pwv_apex: float
        mean of pwv taken by apex
    pwv_apex_std: float
        standard deviation of pwv apex
    pwv_apex_p2p: float
        peak-to-peak of pwv apex
    f_hwp: float
        hwp rotation frequency
    roll_angle: float
        roll angle
    scan_speed: float
        scan speed in deg/s
    scan_acc: float
        scan acceleration in deg/s^2
    sun_distance: float
        distance to sun
    moon_distance: float
        distance to moon
    wind_speed: float
        wind speed
    wind_direction: float
        wind direction
    ambient_temperature: float
        ambient temperature
    uv: float
        uv index
    detnum_before_fitselection: int
        number of detectors before fit selection
    total_detnum: int
        total number of detectors
    recenter: bool
        recenter flag
    yc: float
        center of map in y direction
    xc: float
        center of map in x direction
    Tmap_variance: float
        variance of T map in pW
    Qmap_variance: float
        variance of Q map in pW
    Umap_variance: float
        variance of U map in pW
    proc: dict
        preprocessing names
    detnum: list
        list of detector numbers on each proc
    detid: list
        list of detector ids
    """
    
    __tablename__ = "planet_map"

    obs_id: str = Field(primary_key=True)
    telescope: str = Field(primary_key=True)
    freq_channel: str = Field(primary_key=True)
    wafer: str = Field(primary_key=True)
    source: str = Field(primary_key=True)

    ctime: datetime = Field(nullable=False)
    hit_path: str | None = Field()
    map_path: str | None = Field()
    weight_path: str | None = Field()
    weighted_map_path: str | None = Field()

    elevation: float | None = Field()
    duration: float | None = Field()
    azimuth: float | None = Field()
    pwv: float | None = Field()
    pwv_std: float | None = Field()
    pwv_p2p: float | None = Field()
    pwv_apex: float | None = Field()
    pwv_apex_std: float | None = Field()
    pwv_apex_p2p: float | None = Field()
    f_hwp: float | None = Field()
    roll_angle: float | None = Field()
    scan_speed: float | None = Field()
    scan_acc: float | None = Field()
    sun_distance: float | None = Field()
    moon_distance: float | None = Field()
    wind_speed: float | None = Field()
    wind_direction: float | None = Field()
    ambient_temperature: float | None = Field()
    uv: float | None = Field()

    detnum_before_fitselection: int | None = Field()
    total_detnum: int | None = Field()
    recenter: bool | None = Field()
    yc: float | None = Field()
    xc: float | None = Field()

    Tmap_variance: float | None = Field()
    Qmap_variance: float | None = Field()
    Umap_variance: float | None = Field()

    proc: dict[str, Any] | list[Any] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    detnum: list[int] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    detid: list[str] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )

    fit: Optional["PlanetMapFitTable"] = Relationship(
        back_populates="map",
        cascade_delete=True,
        sa_relationship_kwargs={
        "uselist": False,
        },
    )

    def to_model(self) -> PlanetMap:
        """
        Return an PlanetMap model from this table entry.

        Returns
        -------
        PlanetMap : PlanetMap
            The PlanetMap model corresponding to this table entry.
        """
        return PlanetMap(
            obs_id=self.obs_id,
            telescope=self.telescope,
            freq_channel=self.freq_channel,
            wafer=self.wafer,
            ctime=Time(self.ctime, format="unix", scale="utc"),
            source=self.source,
            hit_path=self.hit_path,
            map_path=self.map_path,
            weight_path=self.weight_path,
            weighted_map_path=self.weighted_map_path,
            azimuth=self.azimuth,
            elevation=self.elevation,
            duration=self.duration,
            pwv=self.pwv,
            pwv_std=self.pwv_std,
            pwv_p2p=self.pwv_p2p,
            pwv_apex=self.pwv_apex,
            pwv_apex_std=self.pwv_apex_std,
            pwv_apex_p2p=self.pwv_apex_p2p,
            f_hwp=self.f_hwp,
            roll_angle=self.roll_angle,
            scan_speed=self.scan_speed,
            scan_acc=self.scan_acc,
            sun_distance=self.sun_distance,
            moon_distance=self.moon_distance,
            wind_speed=self.wind_speed,
            wind_direction=self.wind_direction,
            ambient_temperature=self.ambient_temperature,
            uv=self.uv,
            detnum_before_fitselection=self.detnum_before_fitselection,
            total_detnum=self.total_detnum,
            recenter=self.recenter,
            yc=self.yc,
            xc=self.xc,
            Tmap_variance=self.Tmap_variance,
            Qmap_variance=self.Qmap_variance,
            Umap_variance=self.Umap_variance,
            proc=self.proc,
            detnum=self.detnum,
            detid=self.detid,
            amplitude=self.fit.amplitude,
            xo=self.fit.xo,
            yo=self.fit.yo,
            sigmax=self.fit.sigmax,
            sigmay=self.fit.sigmay,
            theta=self.fit.theta,
            redchit=self.fit.redchit,
            mq=self.fit.mq,
            d0q=self.fit.d0q,
            d1q=self.fit.d0u,
            sigmaq=self.fit.sigmaq,
            redchiq=self.fit.redchiq,
            mu=self.fit.mu,
            d0u=self.fit.d0u,
            d1u=self.fit.d1u,
            sigmau=self.fit.sigmau,
            redchiu=self.fit.redchiu
        )

class PlanetMapFitTable(SQLModel, table=True):
    """
    Table for Main-beam and leakage-beam fit results for a planet map.

    Attributes
    ----------
    map_id : int
        Internal ID of the depth one map
    residual_model: ConstantPointingModel | PolynomialPointingModel
        The pointing model to actually store in the database.
    residual_stats: PointingModelStats
        Statistics about the pointing residuals, such as mean and stddev of RA and Dec offsets
    """

    __tablename__ = "planet_map_fits"
    __table_args__ = (
        ForeignKeyConstraint(
            [
                "obs_id",
                "telescope",
                "freq_channel",
                "wafer",
                "source",
            ],
            [
                "planet_map.obs_id",
                "planet_map.telescope",
                "planet_map.freq_channel",
                "planet_map.wafer",
                "planet_map.source",
            ],
            ondelete="CASCADE",
        ),
    )

    # Same primary key as PlanetMapTable 
    obs_id: str = Field(primary_key=True)
    telescope: str = Field(primary_key=True)
    freq_channel: str = Field(primary_key=True)
    wafer: str = Field(primary_key=True)
    source: str = Field(primary_key=True)
    
    # Main-beam fit result (T map)
    peak: float | None = Field()
    amplitude: float | None = Field()
    xo: float | None = Field()
    yo: float | None = Field()
    sigmax: float | None = Field()
    sigmay: float | None = Field()
    theta: float | None = Field()
    redchit: float | None = Field()

    # Leakage-beam fit result (Q map)
    mq: float | None = Field()
    d0q: float | None = Field()
    d1q: float | None = Field()
    sigmaq: float | None = Field()
    redchiq: float | None = Field()

    # Leakage-beam fit result (U map)
    mu: float | None = Field()
    d0u: float | None = Field()
    d1u: float | None = Field()
    sigmau: float | None = Field()
    redchiu: float | None = Field()

    map: "PlanetMapTable" = Relationship(
        back_populates="fit",
    )
