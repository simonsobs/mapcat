"""
Table definitions
"""

from .atomic_coadd import AtomicMapCoaddTable
from .atomic_map import AtomicMapTable
from .depth_one_coadd import DepthOneCoaddTable
from .depth_one_map import DepthOneMapTable
from .pipeline_information import PipelineInformationTable
from .pointing_residual import PointingResidualTable
from .processing_status import ProcessingStatusTable
from .sky_coverage import SkyCoverageTable
from .tod import TODDepthOneTable

__all__ = [
    "AtomicMapTable",
    "AtomicMapCoaddTable",
    "DepthOneMapTable",
    "ProcessingStatusTable",
    "PointingResidualTable",
    "TODDepthOneTable",
    "PipelineInformationTable",
    "SkyCoverageTable",
]

ALL_TABLES = [
    AtomicMapTable,
    AtomicMapCoaddTable,
    DepthOneMapTable,
    DepthOneCoaddTable,
    ProcessingStatusTable,
    PointingResidualTable,
    TODDepthOneTable,
    PipelineInformationTable,
    SkyCoverageTable,
]
