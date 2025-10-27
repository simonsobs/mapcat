"""
Table for atomic maps.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .links import AtomicMapToCoaddTable

if TYPE_CHECKING:
    from .atomic_coadd import AtomicMapCoaddTable


class AtomicMapTable(SQLModel, table=True):
    __tablename__ = "atomic_maps"

    atomic_map_id: int = Field(primary_key=True)

    obs_id: str = Field()
    telescope: str = Field()
    freq_channel: str = Field()
    wafer: str = Field()
    ctime: int = Field()
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

    coadds: list["AtomicMapCoaddTable"] = Relationship(
        back_populates="atomic_maps",
        link_model=AtomicMapToCoaddTable,
    )
