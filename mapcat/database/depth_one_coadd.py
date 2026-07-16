"""
Table containing information about Depth-1 map coadds.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Uuid
from sqlmodel import Field, Relationship, SQLModel
from uuid7 import create as uuid7_create

from .depth_one_map import DepthOneMapTable
from .links import DepthOneToCoaddTable

if TYPE_CHECKING:  # pragma: no cover
    from .time_domain_processing import TimeDomainProcessingTable


class DepthOneCoaddTable(SQLModel, table=True):
    """
    A co-add of multiple depth-1 maps. This is the table model,
    but this many-to-many relationship relies on the join table.
    """

    __tablename__ = "depth_one_coadds"

    coadd_id: UUID = Field(
        default_factory=uuid7_create, primary_key=True, sa_type=Uuid
    )
    coadd_name: str = Field(nullable=False)
    coadd_type: str = Field(nullable=False)

    map_path: str
    ivar_path: str | None
    rho_path: str | None = None
    kappa_path: str | None = None

    start_time_path: str | None = None
    mean_time_path: str | None
    end_time_path: str | None = None

    frequency: str = Field(nullable=False)
    ctime: float = Field(nullable=False)
    start_time: float = Field(nullable=False)
    stop_time: float = Field(nullable=False)

    maps: list["DepthOneMapTable"] = Relationship(
        back_populates="coadds",
        link_model=DepthOneToCoaddTable,
    )
    processing_status: list["TimeDomainProcessingTable"] = Relationship(
        back_populates="coadd",
        cascade_delete=True,
    )
