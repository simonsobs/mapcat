"""
Table containing pointing residuals.
"""

from sqlmodel import Field, Relationship, SQLModel

from mapcat.pointing.const import ConstantPointingModel

from mapcat.pointing.base import PointingModelStats

from .depth_one_map import DepthOneMapTable
from .json import JSONEncodedPydantic


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
    residual_model: ConstantPointingModel
        The pointing model to actually store in the database.
    residual_stats: PointingModelStats
        Statistics about the pointing residuals, such as mean and stddev of RA and Dec offsets
    """

    __tablename__ = "depth_one_pointing_residuals"
    pointing_residual_id: int = Field(primary_key=True)

    map_id: int = Field(
        index=True,
        nullable=False,
        foreign_key="depth_one_maps.map_id",
        ondelete="CASCADE",
    )

    residual_model: ConstantPointingModel = Field(
        discriminator="model_type", sa_type=JSONEncodedPydantic(ConstantPointingModel)
    )
    residual_stats: PointingModelStats = Field(
        sa_type=JSONEncodedPydantic(PointingModelStats)
    )
    map: DepthOneMapTable = Relationship(back_populates="pointing_residual")
