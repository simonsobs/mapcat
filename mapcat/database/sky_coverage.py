"""
Sky coverage table.
"""

from sqlmodel import Field, Relationship, SQLModel

from .depth_one_map import DepthOneMapTable


class SkyCoverageTable(SQLModel, table=True):
    """
    Table for tracking sky coverage for a depth one map. x and y are 0->36 and
    0-18 respectively for CAR patches with 10x10 degrees each.

    Attributes
    ----------
    id : str
        Internal ID of the sky coverage
    map_name : str
        Name of depth 1 map being tracked. Foreign into DepthOneMap
    patch_coverage : str
        String which represents the sky coverage of the d1map
    """

    __tablename__ = "depth_one_sky_coverage"

    patch_id: int = Field(primary_key=True)

    x: int = Field(index=True)
    y: int = Field(index=True)

    map_id: int = Field(
        foreign_key="depth_one_maps.map_id", nullable=False, ondelete="CASCADE"
    )
    map: DepthOneMapTable = Relationship(back_populates="depth_one_sky_coverage")
