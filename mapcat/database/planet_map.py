"""
Table for planet maps.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any
import json

from astropy.time import Time
from astropydantic import AstroPydanticTime
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, JSON

class PlanetMap(SQLModel):
    planet_map_id: int

    obs_id: str
    telescope: str
    freq_channel: str
    wafer: str
    ctime: AstroPydanticTime
    source: str

    valid: bool | None
    prefix_path: str | None

    hit_path: str | None
    map_path: str | None
    weight_path: str | None
    weight_map_path: str | None

    azimuth: float | None
    elevation: float | None    
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


class PlanetMapTable(SQLModel, table=True):
    __tablename__ = "planet_maps"

    planet_map_id: int = Field(primary_key=True)

    obs_id: str = Field()
    telescope: str = Field()
    freq_channel: str = Field()
    wafer: str = Field()
    ctime: datetime = Field(nullable=False)
    source: str = Field()

    prefix_path: str | None = Field()
    hit_path: str | None = Field()
    map_path: str | None = Field()
    weight_path: str | None = Field()
    weight_map_path: str | None = Field()

    valid: bool | None = Field()
    elevation: float | None = Field()
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
   


    def to_model(self) -> PlanetMap:
        """
        Return an PlanetMap model from this table entry.

        Returns
        -------
        PlanetMap : PlanetMap
            The PlanetMap model corresponding to this table entry.
        """
        return PlanetMap(
            planet_map_id=self.planet_map_id,
            obs_id=self.obs_id,
            telescope=self.telescope,
            freq_channel=self.freq_channel,
            wafer=self.wafer,
            ctime=Time(self.ctime),
            source=self.source,
            valid=self.valid,
            prefix_path=self.prefix_path,
            hit_path=self.hit_path,
            map_path=self.map_path,
            weight_path=self.weight_path,
            weight_map_path=self.weight_map_path,
            azimuth=self.azimuth,
            elevation=self.elevation,
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
        )
