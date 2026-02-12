"""
Sky coverage table.
"""

from sqlalchemy import PrimaryKeyConstraint
from sqlmodel import Field, Relationship, SQLModel

from .depth_one_map import DepthOneMapTable


class SkyCoverageTable(SQLModel, table=True):
    """
    Table for tracking sky coverage patches with non-zero overlap with a given depth one map.
    x and y are 0->36 and 0-18 respectively for CAR patches with 10x10 degrees each.

    Attributes
    ----------
    sky_cov_id : PrimaryKeyConstraint
        Composite ID from map_id, x, and y
    map : DepthOneMapTable
       Depth 1 map being tracked. Foreign into DepthOneMap
    map_id : int
       ID of depth 1 map being tracked
    x : int
        x-index of coverage patch. x=0 runs from RA 0 to 10,, etc.
    y : in
        y-index of coverage patch. y=0 runs from dec = -90 to -80, etc.
    """

    __tablename__ = "depth_one_sky_coverage"

    x: int = Field(index=True, primary_key=True)
    y: int = Field(index=True, primary_key=True)

    map_id: int = Field(
        foreign_key="depth_one_maps.map_id",
        nullable=False,
        ondelete="CASCADE",
        primary_key=True,
    )
    map: DepthOneMapTable = Relationship(back_populates="depth_one_sky_coverage")

    __table_args__ = (PrimaryKeyConstraint("map_id", "x", "y", name="sky_cov_id"),)

    """
    __table_args__ = (
        Index(
        "ix_depth_one_sky_coverage_map_id_x_y",
        "map_id",
        "x",
        "y",
        unique=True,
        pimary_key=True,
    )
    )
    """
