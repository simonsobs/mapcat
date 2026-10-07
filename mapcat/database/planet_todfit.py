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
    """
        Table for a todfit result of planet observation.
    Attributes
    ----------
    obs_id : str
        observation id
    telescope : str
        Telescope 
    freq_channel : str
        Frequency band
    wafer : str
        Wafer slot
    source : str
        source. eg jupiter
    detid : str
        detector id
    ctime : datetime
        start unix time of map
    amplitude : float
        amplitude of planet signal normalized by solid angle with an unit of degree
    xo : float
        x offset of planet signal. Unit in degree
    yo : float
        y offset of planet signal. Unit in degree
    sigmax : float
        sigma of planet signal in x direction. Unit in degree
    sigmay : float
        sigma of planet signal in y direction. Unit in degree
    theta : float
        angle of elliptical gaussian. Unit in degree
    defla : float
        deflection amplitude. Unit in radian
    deflp : float
        deflection phase. Unit in radian
    amplitude_err : float
        error of amplitude
    xo_err : float
        error of xo
    yo_err : float
        error of yo
    sigmax_err : float
        error of sigmax
    sigmay_err : float
        error of sigmay
    theta_err : float
        error of theta
    defla_err : float
        error of defla
    deflp_err : float
        error of deflp
    chisq : float
        chi square
    dof : int
        degree of freedom
    xi : float
        detector xi position in focal plane coordinate. Unit in radian
    eta : float
        detector eta position in focal plane coordinate. Unit in radian
    gamma : float
        detector gamma angle in focal plane coordinate. Unit in radian
    
    """
    __tablename__ = "planet_todfit"

    obs_id: str = Field(primary_key=True)
    telescope: str = Field(primary_key=True)
    freq_channel: str = Field(primary_key=True)
    wafer: str = Field(primary_key=True)
    source: str = Field(primary_key=True)
    detid: str = Field(primary_key=True)

    ctime: datetime = Field(nullable=False)
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
