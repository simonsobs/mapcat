"""
Table for planet todfit.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any
import json

from astropy.time import Time
from astropydantic import AstroPydanticTime
from sqlmodel import Field, Relationship, SQLModel

class PlanetTodFit(SQLModel):
    planet_todfit_id: int

    obs_id: str
    telescope: str
    freq_channel: str
    wafer: str
    ctime: AstroPydanticTime
    source: str
    detid: str

    valid: bool | None
    amplitude: float | None
    xo: float | None
    yo: float | None
    sigmax: float | None
    sigmay: float | None
    theta: float | None
    defla: float | None
    deflp: float | None
    amplitude_err: float | None
    xo_err: float | None
    yo_err: float | None
    sigmax_err: float | None
    sigmay_err: float | None
    theta_err: float | None
    defla_err: float | None
    deflp_err: float | None
    chisq: float | None
    dof: int | None
    xi: float | None
    eta: float | None
    gamma: float | None


class PlanetTodFitTable(SQLModel, table=True):
    __tablename__ = "planet_todfit"

    planet_todfit_id: int = Field(primary_key=True)

    obs_id: str = Field()
    telescope: str = Field()
    freq_channel: str = Field()
    wafer: str = Field()
    ctime: datetime = Field(nullable=False)
    source: str = Field()
    detid: str = Field()

    valid: bool = Field()
    amplitude: float = Field()
    xo: float = Field()
    yo: float = Field()
    sigmax: float = Field()
    sigmay: float = Field()
    theta: float = Field()
    defla: float = Field()
    deflp: float = Field()
    amplitude_err: float = Field()
    xo_err: float = Field()
    yo_err: float = Field()
    sigmax_err: float = Field()
    sigmay_err: float = Field()
    theta_err: float = Field()
    defla_err: float = Field()
    deflp_err: float = Field()
    chisq: float = Field()
    dof: int = Field()
    xi: float = Field()
    eta: float = Field()
    gamma: float = Field()


    def to_model(self) -> PlanetTodFit:
        """
        Return an PlanetTodFit model from this table entry.

        Returns
        -------
        PlanetTodFit : PlanetTodFit
            The PlanetTodFit model corresponding to this table entry.
        """
        return PlanetTodFit(
            atomic_map_id=self.atomic_map_id,
            obs_id=self.obs_id,
            telescope=self.telescope,
            freq_channel=self.freq_channel,
            wafer=self.wafer,
            ctime=Time(self.ctime),
            source=self.source,
            detid=self.detid,
            valid=self.valid,
            amplitude=self.amplitude,
            xo=self.xo,
            yo=self.yo,
            sigmax=self.sigmax,
            sigmay=self.sigmay,
            theta=self.theta,
            defla=self.defla,
            deflp=self.deflp,
            amplitude_err=self.amplitude_err,
            xo_err=self.xo_err,
            yo_err=self.yo_err,
            sigmax_err=self.sigmax_err,
            sigmay_err=self.sigmay_err,
            theta_err=self.theta_err,
            defla_err=self.defla_err,
            deflp_err=self.deflp_err,
            chisq=self.chisq,
            dof=self.dof,
            xi=self.xi,
            eta=self.eta,
            gamma=self.gamma,
        )
