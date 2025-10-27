"""
Link tables.
"""

from sqlmodel import Field, SQLModel


class DepthOneToCoaddTable(SQLModel, table=True):
    """
    Link table for many-to-many relationship between depth-1 maps and coadds.
    """

    __tablename__ = "link_depth_one_map_to_coadd"

    map_id: int = Field(
        foreign_key="depth_one_maps.map_id",
        primary_key=True,
        nullable=False,
        index=True,
        ondelete="CASCADE",
    )
    coadd_id: int = Field(
        foreign_key="depth_one_coadds.coadd_id",
        primary_key=True,
        nullable=False,
        index=True,
        ondelete="CASCADE",
    )


class TODToMapTable(SQLModel, table=True):
    """
    Link table for many-to-many relationship between TODs and depth-1 maps.
    """

    __tablename__ = "link_tod_to_depth_one_map"

    tod_id: int = Field(
        foreign_key="tod_depth_one.tod_id",
        primary_key=True,
        nullable=False,
        index=True,
        ondelete="CASCADE",
    )
    map_id: int = Field(
        foreign_key="depth_one_maps.map_id",
        primary_key=True,
        nullable=False,
        index=True,
        ondelete="CASCADE",
    )
