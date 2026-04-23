"""
Constant pointing model.
"""

from typing import Literal

from astropy.coordinates import SkyCoord
from astropy import units as u
from astropydantic import AstroPydanticQuantity
from mapcat.pointing.base import PointingModelProtocol


class ConstantPointingModel(PointingModelProtocol):
    model_type: Literal["constant"] = "constant"

    ra_offset: AstroPydanticQuantity[u.deg]
    dec_offset: AstroPydanticQuantity[u.deg]

    def predict(self, pos: SkyCoord) -> SkyCoord:
        ra = pos.ra + self.ra_offset
        dec = pos.dec + self.dec_offset

        return SkyCoord(ra=ra, dec=dec, frame=pos.frame)
