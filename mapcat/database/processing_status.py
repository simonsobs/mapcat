"""
Table containing information about processing status of the Depth-1 maps.
"""

from sqlmodel import Field, Relationship, SQLModel

from .depth_one_map import DepthOneMapTable


class ProcessingStatusTable(SQLModel, table=True):
    """
    Table for tracking processing status of depth-1 maps
    providing SQLModel functionality. You can export a base model, for example
    for responding to a query with using the `to_model` method. Note some attributes
    are inherited from ProcessingStatus.

    Attributes
    ----------
    id : int
        Internal ID of the processing status
    map_name : str
        Name of depth 1 map being tracked. Foreign into DepthOneMap
    processing_start : float | None
        Time processing started. None if not started.
    processing_end : float | None
        Time processing ended. None if not ended.
    processing_status : str
        Status of processing
    """

    __tablename__ = "time_domain_processing"

    processing_status_id: int = Field(primary_key=True)

    map_id: int = Field(
        index=True,
        nullable=False,
        foreign_key="depth_one_maps.map_id",
        ondelete="CASCADE",
    )
    map: DepthOneMapTable = Relationship(back_populates="processing_status")

    processing_start: float = Field(nullable=True)
    processing_end: float = Field(nullable=True)
    processing_status: str = Field(index=True, nullable=False)
