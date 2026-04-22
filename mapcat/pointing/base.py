"""
Base pointing model.
"""

from abc import ABC, abstractmethod
from typing import Literal

from astropy.coordinates import SkyCoord
from pydantic import BaseModel


class PointingModelProtocol(ABC, BaseModel):
    model_type: Literal["protocol"] = "protocol"

    @abstractmethod
    def predict(self, pos: SkyCoord) -> SkyCoord:
        """
        Use the pointing model to predict the underlying sky coordinate
        from the one intiially predicted in the map.
        """
        ...
