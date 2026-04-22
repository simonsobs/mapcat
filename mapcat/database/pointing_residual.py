"""
Table containing pointing residuals.
"""

from collections.abc import Sequence
from typing import Any

from sqlmodel import JSON, Field, Relationship, SQLModel

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
    ra_offset : float | list[float]
        Calculated ra offset of PSes. Can be a scalar or array-like coefficients.
    dec_offset : float | list[float]
        Calculated dec offset of PSes. Can be a scalar or array-like coefficients.
    ra_offset_rms : float
        RMS of the ra residuals.
    dec_offset_rms : float
        RMS of the dec residuals.

    """

    __tablename__ = "depth_one_pointing_residuals"
    pointing_residual_id: int = Field(primary_key=True)

    map_id: int = Field(
        index=True,
        nullable=False,
        foreign_key="depth_one_maps.map_id",
        ondelete="CASCADE",
    )

    ra_offset: float | list[float] | None = Field(default=None, sa_type=JSON, nullable=True)
    dec_offset: float | list[float] | None = Field(default=None, sa_type=JSON, nullable=True)
    ra_offset_rms: float | None = Field(default=None, nullable=True)
    dec_offset_rms: float | None = Field(default=None, nullable=True)
    map: DepthOneMapTable = Relationship(back_populates="pointing_residual")

    def __init__(self, **data: Any):
        for key in ("ra_offset", "dec_offset"):
            value = data.get(key)
            if hasattr(value, "tolist"):
                data[key] = value.tolist()
            elif isinstance(value, Sequence) and not isinstance(
                value, str | bytes | bytearray
            ):
                data[key] = list(value)
        super().__init__(**data)
