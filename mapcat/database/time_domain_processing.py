"""
Table containing information about processing status of the Depth-1 maps.
"""

import uuid
from datetime import datetime

from astropy.time import Time
from astropydantic import AstroPydanticTime
from sqlmodel import Field, Relationship, SQLModel

from .depth_one_map import DepthOneMapTable


class TimeDomainProcessing(SQLModel):
    processing_status_id: uuid.UUID

    map_id: uuid.UUID

    processing_start: AstroPydanticTime | None
    processing_end: AstroPydanticTime | None
    processing_status: str


class TimeDomainProcessingTable(SQLModel, table=True):
    """
    Table for tracking processing status of depth-1 maps
    providing SQLModel functionality. You can export a base model, for example
    for responding to a query with using the `to_model` method. Note some attributes
    are inherited from TimeDomainProcessingTable.

    Attributes
    ----------
    processing_status_id : uuid.UUID
        Internal ID of the processing status
    map_name : uuid.UUID
        Name of depth 1 map being tracked. Foreign into DepthOneMap
    processing_start : datetime | None
        Time processing started. None if not started.
    processing_end : datetime | None
        Time processing ended. None if not ended.
    processing_status : str
        Status of processing
    """

    __tablename__ = "time_domain_processing"

    processing_status_id: uuid.UUID = Field(
        prdefault_factory=uuid.uuid7, primary_key=True
    )

    map_id: uuid.UUID = Field(
        index=True,
        nullable=False,
        foreign_key="depth_one_maps.map_id",
        ondelete="CASCADE",
    )
    map: DepthOneMapTable = Relationship(back_populates="processing_status")

    processing_start: datetime = Field(nullable=True)
    processing_end: datetime = Field(nullable=True)
    processing_status: str = Field(index=True, nullable=False)

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
