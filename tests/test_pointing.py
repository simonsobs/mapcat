"""
Tests for the pointing residual models.
"""

from astropy.units import deg
from sqlmodel import select

from mapcat.database import DepthOneMapTable, PointingResidualTable
from mapcat.pointing.const import ConstantPointingModel


def test_add_retrieve_pointing(database_sessionmaker):
    model = ConstantPointingModel(ra_offset=0.5 * deg, dec_offset=0.5 * deg)

    with database_sessionmaker() as session:
        sample_map = DepthOneMapTable(
            map_name="PointingTestMap",
            map_path="DoesntExist/Map",
            tube_slot="i1",
            frequency="f090",
            ctime=1755787524.0,
            start_time=1755687524.0,
            stop_time=1755887524.0,
        )

        session.add(sample_map)
        session.commit()
        session.refresh(sample_map)

        pointing_residual = PointingResidualTable(
            residual_model=model, map_id=sample_map.map_id
        )

        session.add(pointing_residual)
        session.commit()

    with database_sessionmaker() as session:
        recovered_map = session.execute(
            select(DepthOneMapTable).filter_by(map_name="PointingTestMap")
        ).scalar()

        recovered_pointing = recovered_map.pointing_residual[0]
        residual_model = recovered_pointing.residual_model

        assert residual_model.ra_offset > 0.4 * deg
        assert residual_model.dec_offset > 0.4 * deg
