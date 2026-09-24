"""
Table for planet todfit.
"""

from datetime import datetime

from astropy.time import Time
from astropydantic import AstroPydanticTime
from sqlmodel import Field, SQLModel

class PlanetTodFit(SQLModel):
    obs_id: str
    telescope: str
    freq_channel: str
    wafer: str
    ctime: AstroPydanticTime
    dtime: datetime
    source: str
    detid: str

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

    obs_id: str = Field(primary_key=True)
    telescope: str = Field(primary_key=True)
    freq_channel: str = Field(primary_key=True)
    wafer: str = Field(primary_key=True)
    ctime: float = Field(nullable=False, primary_key=True)
    source: str = Field(primary_key=True)
    detid: str = Field(primary_key=True)
    dtime: datetime = Field()

    amplitude: float | None = Field()
    xo: float | None = Field()
    yo: float | None = Field()
    sigmax: float | None = Field()
    sigmay: float | None = Field()
    theta: float | None = Field()
    defla: float | None = Field()
    deflp: float | None = Field()
    amplitude_err: float | None = Field()
    xo_err: float | None = Field()
    yo_err: float | None = Field()
    sigmax_err: float | None = Field()
    sigmay_err: float | None = Field()
    theta_err: float | None = Field()
    defla_err: float | None = Field()
    deflp_err: float | None = Field()
    chisq: float | None = Field()
    dof: int | None = Field()
    xi: float | None = Field()
    eta: float | None = Field()
    gamma: float | None = Field()


    def to_model(self) -> PlanetTodFit:
        """
        Return an PlanetTodFit model from this table entry.

        Returns
        -------
        PlanetTodFit : PlanetTodFit
            The PlanetTodFit model corresponding to this table entry.
        """
        return PlanetTodFit(
            obs_id=self.obs_id,
            telescope=self.telescope,
            freq_channel=self.freq_channel,
            wafer=self.wafer,
            ctime=Time(self.ctime, format="unix", scale="utc"),
            dtime=self.dtime,
            source=self.source,
            detid=self.detid,
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
