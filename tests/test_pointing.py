"""
Tests for the pointing residual models.
"""

from astropy import units as u
from astropy.coordinates import SkyCoord
import numpy as np
from sqlmodel import select

from mapcat.database import DepthOneMapTable, PointingResidualTable
from mapcat.pointing.const import ConstantPointingModel
from mapcat.pointing.poly import PolynomialPointingModel



def test_add_retrieve_pointing(database_sessionmaker):
    model = ConstantPointingModel(ra_offset=0.5 * u.deg, dec_offset=0.5 * u.deg)

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

        assert residual_model.ra_offset > 0.4 * u.deg
        assert residual_model.dec_offset > 0.4 * u.deg


def test_make_constant_pointing_model():
    model = ConstantPointingModel(ra_offset=0.5 * u.deg, dec_offset=0.5 * u.deg)

    assert model.ra_offset == 0.5 * u.deg
    assert model.dec_offset == 0.5 * u.deg

    og_pos = SkyCoord(ra=10 * u.deg, dec=20 * u.deg
                      )
    offset_pos = SkyCoord(og_pos.ra + model.ra_offset, og_pos.dec + model.dec_offset)
    new_pos = model.predict(offset_pos)
    assert new_pos.ra == og_pos.ra
    assert new_pos.dec == og_pos.dec


def test_make_polynomial_pointing_model():
    model = PolynomialPointingModel(poly_order=2)
    ras = np.arange(0, 10, 1) * u.deg
    decs = np.arange(0, 10, 1) * u.deg
    offset = 1.0 * u.arcmin
    slope = 0.1 * u.arcmin / u.deg

    offset_positions = SkyCoord(
            ra=ras + offset + slope * ras, dec=decs + offset + slope * decs
        )
    model.calculate_model(measured_positions=offset_positions, expected_positions=SkyCoord(ras, decs))

    assert model.ra_model_coefficients is not None
    assert model.dec_model_coefficients is not None

    for i, offset_pos in enumerate(offset_positions):
        predicted_pos = model.predict(offset_pos)
        assert np.isclose(predicted_pos.ra.to_value(u.arcmin), ras[i].to_value(u.arcmin), atol=0.1)
        assert np.isclose(predicted_pos.dec.to_value(u.arcmin), decs[i].to_value(u.arcmin), atol=0.1)

    predicted_pos = model.predict(offset_positions)
    assert np.all(np.isclose(predicted_pos.ra.to_value(u.arcmin), ras.to_value(u.arcmin), atol=0.1))
    assert np.all(np.isclose(predicted_pos.dec.to_value(u.arcmin), decs.to_value(u.arcmin), atol=0.1))
