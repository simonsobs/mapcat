"""
Table definitions
"""

from .tod import TODToMapTable
from .depth_one_map import DepthOneMapTable
from .processing_status import ProcessingStatusTable
from .pointing_residual import PointingResidualTable
from .tod import TODDepthOneTable
from .pipeline_information import PipelineInformationTable
from .sky_coverage import SkyCoverageTable

__all__ = [
    "TODToMapTable",
    "DepthOneMapTable",
    "ProcessingStatusTable",
    "PointingResidualTable",
    "TODDepthOneTable",
    "PipelineInformationTable",
    "SkyCoverageTable",
]

ALL_TABLES = [
    TODToMapTable,
    DepthOneMapTable,
    ProcessingStatusTable,
    PointingResidualTable,
    TODDepthOneTable,
    PipelineInformationTable,
    SkyCoverageTable,
]
