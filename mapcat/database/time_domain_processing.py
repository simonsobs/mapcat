"""
Table containing information about processing status of the Depth-1 maps
and depth-1 map coadds.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from astropy.time import Time
from astropydantic import AstroPydanticTime
from sqlalchemy import CheckConstraint, Uuid
from sqlmodel import Field, Relationship, SQLModel
from uuid7 import UUID as UUID7

if TYPE_CHECKING:  # pragma: no cover
    from .depth_one_coadd import DepthOneCoaddTable
    from .depth_one_map import DepthOneMapTable


class TimeDomainProcessing(SQLModel):
    processing_status_id: UUID7

    map_id: UUID7

    processing_start: AstroPydanticTime | None
    processing_end: AstroPydanticTime | None
    processing_status: str


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
    processing_status_id : UUID7
        Internal ID of the processing status. Yet another uuid,
        independent of the map/coadd being tracked.
    map_id : UUID7 | None
        Depth-1 map being tracked, if this row is for a map.
    coadd_id : UUID7 | None
        Depth-1 map coadd being tracked, if this row is for a coadd.
    processing_start : float | None
        Internal ID of the processing status
    processing_start : datetime | None
        Time processing started. None if not started.
    processing_end : datetime | None
        Time processing ended. None if not ended.
    processing_status : str
        Status of processing
    """

    __tablename__ = "time_domain_processing"

    processing_status_id: UUID7 = Field(primary_key=True,sa_type=Uuid)

    map_id: UUID7 | None = Field(
        default=None,
        index=True,
        nullable=True,
        foreign_key="depth_one_maps.map_id",
        ondelete="CASCADE",
        sa_type=Uuid,
    )
    coadd_id: UUID7 | None = Field(
        default=None,
        index=True,
        nullable=True,
        foreign_key="depth_one_coadds.coadd_id",
        ondelete="CASCADE",
        sa_type=Uuid,
    )
    map: "DepthOneMapTable" = Relationship(back_populates="processing_status")
    coadd: "DepthOneCoaddTable" = Relationship(back_populates="processing_status")

    processing_start: datetime = Field(nullable=True)
    processing_end: datetime = Field(nullable=True)
    processing_status: str = Field(index=True, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "(map_id IS NOT NULL) != (coadd_id IS NOT NULL)",
            name="ck_time_domain_processing_exactly_one_target",
        ),
    )
    def to_model(self) -> TimeDomainProcessing:
        """
        Return a TimeDomainProcessing model from this table entry

        Returns
        -------
        TimeDomainProcessing : TimeDomainProcessing
            The TimeDomainProcessing model corresponding to this table entry.
        """
        return TimeDomainProcessing(
            processing_status_id=self.processing_status_id,
            map_id=self.map_id,
            processing_start=Time(self.processing_start),
            processing_end=Time(self.processing_end),
            processing_status=self.processing_status,
        )
