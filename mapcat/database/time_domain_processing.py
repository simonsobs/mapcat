"""
Table containing information about processing status of the Depth-1 maps
and depth-1 map coadds.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:  # pragma: no cover
    from .depth_one_coadd import DepthOneCoaddTable
    from .depth_one_map import DepthOneMapTable


class TimeDomainProcessingTable(SQLModel, table=True):
    """
    Table for tracking processing status of depth-1 maps and depth-1 map
    coadds, providing SQLModel functionality. You can export a base model,
    for example for responding to a query with using the `to_model` method.
    Note some attributes are inherited from TimeDomainProcessingTable.

    Exactly one of `map_id`/`coadd_id` is set per row (enforced by a DB
    CHECK constraint) -- a row tracks either a depth-1 map or a coadd,
    never both and never neither.

    Attributes
    ----------
    processing_status_id : int
        Internal ID of the processing status. A plain autoincrement PK,
        independent of the map/coadd being tracked.
    map_id : UUID | None
        Depth-1 map being tracked, if this row is for a map.
    coadd_id : UUID | None
        Depth-1 map coadd being tracked, if this row is for a coadd.
    processing_start : float | None
        Time processing started. None if not started.
    processing_end : float | None
        Time processing ended. None if not ended.
    processing_status : str
        Status of processing
    """

    __tablename__ = "time_domain_processing"

    processing_status_id: int = Field(primary_key=True)

    map_id: UUID | None = Field(
        default=None,
        index=True,
        nullable=True,
        foreign_key="depth_one_maps.map_id",
        ondelete="CASCADE",
        sa_type=Uuid,
    )
    coadd_id: UUID | None = Field(
        default=None,
        index=True,
        nullable=True,
        foreign_key="depth_one_coadds.coadd_id",
        ondelete="CASCADE",
        sa_type=Uuid,
    )
    map: "DepthOneMapTable" = Relationship(back_populates="processing_status")
    coadd: "DepthOneCoaddTable" = Relationship(back_populates="processing_status")

    processing_start: float = Field(nullable=True)
    processing_end: float = Field(nullable=True)
    processing_status: str = Field(index=True, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "(map_id IS NOT NULL) != (coadd_id IS NOT NULL)",
            name="ck_time_domain_processing_exactly_one_target",
        ),
    )
