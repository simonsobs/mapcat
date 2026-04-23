"""
Base pointing model.
"""

from abc import ABC, abstractmethod
from typing import Literal

from astropy.coordinates import SkyCoord
from astropydantic import AstroPydanticQuantity
from astropy import units as u
from pydantic import BaseModel


class PointingModelStats(BaseModel):
    mean_ra_offset: AstroPydanticQuantity[u.deg] | None = None
    mean_dec_offset: AstroPydanticQuantity[u.deg] | None = None
    stddev_ra_offset: AstroPydanticQuantity[u.deg] | None = None
    stddev_dec_offset: AstroPydanticQuantity[u.deg] | None = None
    n_sources: int | None = None


class PointingModelProtocol(ABC, BaseModel):
    model_type: Literal["protocol"] = "protocol"

    @abstractmethod
    def predict(self, pos: SkyCoord) -> SkyCoord:
        """
        Use the pointing model to predict the underlying sky coordinate
        from the one initially predicted in the map.
        """
        ...
