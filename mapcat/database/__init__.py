"""
Table definitions
"""

from .atomic_coadd import AtomicMapCoaddTable
from .atomic_map import AtomicMapTable
from .depth_one_coadd import DepthOneCoaddTable
from .depth_one_map import DepthOneMapTable
from .pipeline_information import PipelineInformationTable
from .pointing_residual import PointingResidualTable
from .time_domain_processing import TimeDomainProcessingTable
from .sky_coverage import SkyCoverageTable
from .tod import TODDepthOneTable

__all__ = [
    "AtomicMapTable",
    "AtomicMapCoaddTable",
    "DepthOneMapTable",
    "TimeDomainProcessingTable",
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
    TimeDomainProcessingTable,
    PointingResidualTable,
    TODDepthOneTable,
    PipelineInformationTable,
    SkyCoverageTable,
]
