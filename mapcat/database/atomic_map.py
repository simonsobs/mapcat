"""
Table for atomic maps.
"""

from datetime import datetime
from typing import TYPE_CHECKING

import uuid7 as uuid
from astropy.time import Time
from astropydantic import AstroPydanticTime
from sqlmodel import Field, Relationship, SQLModel

from .links import AtomicMapToCoaddTable

if TYPE_CHECKING:
    from .atomic_coadd import AtomicMapCoaddTable  # pragma: no cover


class AtomicMap(SQLModel):
    atomic_map_id: uuid.UUID

    obs_id: str
    telescope: str
    freq_channel: str
    wafer: str
    ctime: AstroPydanticTime
    split_label: str

    map_path: str | None
    ivar_path: str | None

    valid: bool | None
    split_detail: str | None
    prefix_path: str | None
    azimuth: float | None
    pwv: float | None
    dpwv: float | None
    total_weight_qu: float | None
    mean_weight_qu: float | None
    median_weight_qu: float | None
    leakage_avg: float | None
    noise_avg: float | None
    ampl_2f_avg: float | None
    gain_avg: float | None
    f_hwp: float | None
    roll_angle: float | None
    scan_speed: float | None
    scan_acc: float | None
    sun_distance: float | None
    ambient_temperature: float | None
    uv: float | None
    ra_center: float | None
    dec_center: float | None
    number_dets: int | None
    moon_distance: float | None
    wind_speed: float | None
    wind_direction: float | None
    rqu_avg: float | None


class AtomicMapTable(SQLModel, table=True):
    __tablename__ = "atomic_maps"

    atomic_map_id: uuid.UUID = Field(default_factory=uuid.uuid7, primary_key=True)

    obs_id: str = Field()
    telescope: str = Field()
    freq_channel: str = Field()
    wafer: str = Field()
    ctime: datetime = Field()
    split_label: str = Field()

    map_path: str | None = Field()
    ivar_path: str | None = Field()

    valid: bool | None = Field()
    split_detail: str | None = Field()
    prefix_path: str | None = Field()
    elevation: float | None = Field()
    azimuth: float | None = Field()
    pwv: float | None = Field()
    dpwv: float | None = Field()
    total_weight_qu: float | None = Field()
    mean_weight_qu: float | None = Field()
    median_weight_qu: float | None = Field()
    leakage_avg: float | None = Field()
    noise_avg: float | None = Field()
    ampl_2f_avg: float | None = Field()
    gain_avg: float | None = Field()
    tau_avg: float | None = Field()
    f_hwp: float | None = Field()
    roll_angle: float | None = Field()
    scan_speed: float | None = Field()
    scan_acc: float | None = Field()
    sun_distance: float | None = Field()
    ambient_temperature: float | None = Field()
    uv: float | None = Field()
    ra_center: float | None = Field()
    dec_center: float | None = Field()
    number_dets: int | None = Field()
    moon_distance: float | None = Field()
    wind_speed: float | None = Field()
    wind_direction: float | None = Field()
    rqu_avg: float | None = Field()

    coadds: list["AtomicMapCoaddTable"] = Relationship(
        back_populates="atomic_maps",
        link_model=AtomicMapToCoaddTable,
    )

    def to_model(self) -> AtomicMap:
        """
        Return an AtomicMap model from this table entry.

        Returns
        -------
        AtomicMap : AtomicMap
            The AtmoicMap model corresponding to this table entry.
        """
        return AtomicMap(
            atomic_map_id=self.atomic_map_id,
            obs_id=self.obs_id,
            telescope=self.telescope,
            freq_channel=self.freq_channel,
            wafer=self.wafer,
            ctime=Time(self.ctime),
            split_label=self.split_label,
            map_path=self.map_path,
            ivar_path=self.ivar_path,
            valid=self.valid,
            split_detail=self.split_detail,
            prefix_path=self.prefix_path,
            azimuth=self.azimuth,
            pwv=self.pwv,
            dpwv=self.dpwv,
            total_weight_qu=self.total_weight_qu,
            mean_weight_qu=self.mean_weight_qu,
            leakage_avg=self.leakage_avg,
            noise_avg=self.noise_avg,
            ampl_2f_avg=self.ampl_2f_ave,
            gain_avg=self.gain_avg,
            f_hwp=self.f_hwp,
            roll_angle=self.roll_angle,
            scan_speed=self.scan_speed,
            scan_acc=self.scan_acc,
            sun_distance=self.sun_distance,
            ambient_temperature=self.ambient_temperature,
            uv=self.uv,
            ra_center=self.ra_center,
            dec_center=self.dec_center,
            number_dets=self.number_dets,
            moon_distance=self.moon_distance,
            wind_speed=self.wind_speed,
            wind_direction=self.wind_direction,
            rqu_avg=self.rqu_avg,
        )
