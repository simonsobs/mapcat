"""
Atomic map coadds
"""

from datetime import datetime
from typing import TYPE_CHECKING

from astropy.time import Time
from astropydantic import AstroPydanticTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .atomic_map import AtomicMapTable

from .links import AtomicMapToCoaddTable, CoaddMapToCoaddTable  # pragma: no cover


class AtomicMapCoadd(SQLModel):
    coadd_id: int

    coadd_name: str
    prefix_path: str

    platform: str
    interval: str
    start_time: AstroPydanticTime
    stop_time: AstroPydanticTime
    freq_channel: str
    geom_file_path: str
    split_label: str


class AtomicMapCoaddTable(SQLModel, table=True):
    __tablename__ = "atomic_map_coadds"

    coadd_id: int = Field(primary_key=True)

    coadd_name: str = Field()
    prefix_path: str = Field()

    platform: str = Field()
    interval: str = Field()
    start_time: datetime = Field(nullable=False)
    stop_time: datetime = Field(nullable=False)
    freq_channel: str = Field()
    geom_file_path: str = Field()
    split_label: str = Field()

    atomic_maps: list["AtomicMapTable"] = Relationship(
        back_populates="coadds",
        link_model=AtomicMapToCoaddTable,
    )

    child_coadds: list["AtomicMapCoaddTable"] = Relationship(
        back_populates="parent_coadds",
        link_model=CoaddMapToCoaddTable,
        sa_relationship_kwargs={
            "primaryjoin": "AtomicMapCoaddTable.coadd_id == CoaddMapToCoaddTable.parent_coadd_id",
            "secondaryjoin": "AtomicMapCoaddTable.coadd_id == CoaddMapToCoaddTable.child_coadd_id",
        },
    )

    parent_coadds: list["AtomicMapCoaddTable"] = Relationship(
        back_populates="child_coadds",
        link_model=CoaddMapToCoaddTable,
        sa_relationship_kwargs={
            "primaryjoin": "AtomicMapCoaddTable.coadd_id == CoaddMapToCoaddTable.child_coadd_id",
            "secondaryjoin": "AtomicMapCoaddTable.coadd_id == CoaddMapToCoaddTable.parent_coadd_id",
        },
    )

    def to_model(self) -> AtomicMapCoadd:
        """
        Return an AtomicMapCoadd model from this table entry.

        Returns
        -------
        AtomicMapCoadd : AtomicMapCoadd
             The AtomicMapCoadd model corresponding to this table entry.
        """
        return AtomicMapCoadd(
            coadd_id=self.coadd_id,
            coadd_name=self.coadd_name,
            prefix_path=self.prefix_path,
            platform=self.platform,
            interval=self.interval,
            start_time=Time(self.start_time),
            stop_time=Time(self.stop_time),
            freq_channel=self.freq_channel,
            geom_file_path=self.geom_file_path,
            split_label=self.split_label,
        )
