"""
Atomic map coadds
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .atomic_map import AtomicMapTable

from .links import AtomicMapToCoaddTable, CoaddMapToCoaddTable


class AtomicMapCoaddTable(SQLModel, table=True):
    __tablename__ = "atomic_map_coadds"

    coadd_id: int = Field(primary_key=True)

    coadd_name: str = Field()
    coadd_path: str = Field()

    platform: str = Field()
    interval: str = Field()
    start_time: float = Field()
    end_time: float = Field()
    frequency: str = Field()

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
