"""
Table containing information about Depth-1 map coadds.
"""

from datetime import datetime

from astropy.time import Time
from sqlmodel import Field, Relationship, SQLModel

from .depth_one_map import DepthOneMapTable
from .links import DepthOneToCoaddTable


class DepthOneCoadd(SQLModel):
    coadd_id: int
    coadd_name: str
    coadd_type: str

    map_path: str
    ivar_path: str | None
    rho_path: str | None
    kappa_path: str | None

    start_time_path: str | None
    mean_time_path: str | None
    end_time_path: str | None

    frequency: str
    ctime: datetime
    start_time: datetime
    stop_time: datetime


class DepthOneCoaddTable(SQLModel, table=True):
    """
    A co-add of multiple depth-1 maps. This is the table model,
    but this many-to-many relationship relies on the join table.
    """

    __tablename__ = "depth_one_coadds"

    coadd_id: int = Field(primary_key=True)
    coadd_name: str = Field(nullable=False)
    coadd_type: str = Field(nullable=False)

    map_path: str
    ivar_path: str | None
    rho_path: str | None = None
    kappa_path: str | None = None

    start_time_path: str | None = None
    mean_time_path: str | None
    end_time_path: str | None = None

    frequency: str = Field(nullable=False)
    ctime: datetime = Field(nullable=False)
    start_time: datetime = Field(nullable=False)
    stop_time: datetime = Field(nullable=False)

    maps: list["DepthOneMapTable"] = Relationship(
        back_populates="coadds",
        link_model=DepthOneToCoaddTable,
    )

    def to_model(self) -> DepthOneCoadd:
        """
        Return an DepthOneCoadd model from this table entry.

        Returns
        -------
        DepthOneCoadd : DepthOneCoadd
             The DepthOneCoadd model corresponding to this table entry.
        """
        return DepthOneCoadd(
            coadd_id=self.coadd_id,
            coadd_name=self.coadd_name,
            coadd_type=self.coadd_type,
            map_path=self.map_path,
            ivar_path=self.ivar_path,
            rho_path=self.rho_path,
            kappa_path=self.kappa_path,
            start_time_path=self.start_time_path,
            mean_time_path=self.mean_time_path,
            end_time_path=self.end_time_path,
            frequency=self.frequency,
            ctime=Time(self.ctime),
            start_time=Time(self.start_time),
            stop_time=Time(self.end_time),
        )
