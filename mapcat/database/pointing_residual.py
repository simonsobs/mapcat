"""
Table containing pointing residuals.
"""

from sqlmodel import Field, Relationship, SQLModel

from .depth_one_map import DepthOneMapTable


class PointingResidualTable(SQLModel, table=True):
    """
    Table for tracking Pointing error for a depth one map,
    computed by comparing positions of PSes in that map to
    their known possitions

    Attributes
    ----------
    id : str
        Internal ID of the pointing error
    map_name : str
        Name of depth 1 map being tracked. Foreign into DepthOneMap
    ra_offset : float
        Calculated ra offset of PSes
    dec_offset : float
        Calculated dec offset of PSes

    """

    __tablename__ = "depth_one_pointing_residuals"
    pointing_residual_id: int = Field(primary_key=True)

    map_id: int = Field(
        index=True,
        nullable=False,
        foreign_key="depth_one_maps.map_id",
        ondelete="CASCADE",
    )

    ra_offset: float = Field(nullable=True)
    dec_offset: float = Field(nullable=True)
    map: DepthOneMapTable = Relationship(back_populates="pointing_residual")
