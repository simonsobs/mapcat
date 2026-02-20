"""
Information on the map making pipeline run.
"""

from typing import Any

from sqlmodel import JSON, Field, Relationship, SQLModel

from .depth_one_map import DepthOneMapTable


class PipelineInformationTable(SQLModel, table=True):
    """
    Table for tracking processing information for a depth one map.

    Attributes
    ----------
    id : str
        Internal ID of the pipeline info
    map_name : str
        Name of depth 1 map being tracked. Foreign into DepthOneMap
    sotodlib_version : str
        Version of sotodlib used to make the map
    map_maker : str
        Mapmaker used to make the map
    preprocess_info : dict[str, Any]
        JSON of any additional preprocessing info
    """

    __tablename__ = "pipeline_information"

    pipeline_information_id: int = Field(primary_key=True)
    map_id: int = Field(foreign_key="depth_one_maps.map_id", nullable=False)
    map: DepthOneMapTable = Relationship(back_populates="pipeline_information")

    sotodlib_version: str
    map_maker: str
    preprocess_info: dict[str, Any] = Field(sa_type=JSON)
