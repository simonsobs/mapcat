"""
Polynomial pointing model.
"""
from astropydantic import AstroPydanticUnit
import numpy as np
from pydantic import BaseModel
from typing import Literal

from astropy.coordinates import SkyCoord
from astropy import units as u
from mapcat.pointing.base import PointingModelProtocol, PointingModelStats


class PolynomialCoefficients(BaseModel):
    """
    Coefficients for a polynomial pointing model.
    for example a 2D polynomial of order 2,
    coeffs={'x^2':1,
            'y^2':1,
            'xy':1,
            'y': 2,
            'x':2,
            'constant':3
            }
    labels = {'x':'ra', 'y':'dec'}
    """
    coeffs: dict[str,float]
    labels: dict[str, str]
    unit: AstroPydanticUnit = AstroPydanticUnit(u.deg)
    poly_order: int



class PolynomialPointingModel(PointingModelProtocol):
    model_type: Literal["polynomial"] = "polynomial"

    poly_order: int
    ra_model_coefficients: PolynomialCoefficients | None = None
    dec_model_coefficients: PolynomialCoefficients | None = None

    ## Basis terms for 2D polynomial fit
    def _poly_terms(self, x, y):
        terms = []
        for i in range(self.poly_order + 1):
            for j in range(self.poly_order + 1 - i):
                terms.append((x**i) * (y**j))
        return np.vstack(terms).T

    def _poly_keys(self):
        keys = []
        for i in range(self.poly_order + 1):
            for j in range(self.poly_order + 1 - i):
                keys.append(f"x^{i}y^{j}")
        return keys

    def calculate_model(self, 
                        measured_positions: SkyCoord, 
                        expected_positions: SkyCoord, 
                        position_uncertainty: tuple[u.Quantity, u.Quantity] | u.Quantity | None = None,
                        weights: tuple[list[float], list[float]] | list[float] | None = None
                        ) -> SkyCoord:
        """
        Calculate the polynomial coefficients for the pointing model
        using the measured and expected positions.

        Optionally accept uncertainties in the measured positions
        and measurement weights to perform a weighted fit.

        position_uncertainty can be provided as a tuple of (ra_uncertainties, dec_uncertainties) 
        or a single quantity that applies to both.
        similarly, weights can be provided as a tuple of (ra_weights, dec_weights) 
        or a single list that applies to both.

        weights are resolved from uncertainties if not provided, using inverse variance weighting.
        """
        # Calculate offsets
        ra_offsets = measured_positions.ra - expected_positions.ra
        dec_offsets = measured_positions.dec - expected_positions.dec
        n = len(ra_offsets)
        if n == 0:
            raise ValueError("No positions provided for model calculation.")
        
        # Unpack position_uncertainty into ra_uncerts, dec_uncerts
        if isinstance(position_uncertainty, tuple):
            ra_uncerts, dec_uncerts = position_uncertainty
        else:
            ra_uncerts = dec_uncerts = position_uncertainty  # None or single Quantity applied to both

        # Unpack weights into ra_weights, dec_weights
        if isinstance(weights, tuple):
            ra_weights, dec_weights = weights
        else:
            ra_weights = dec_weights = weights  # None or single list applied to both

        # Lots of logic to check if weights exist, etc.
        # Resolve weights from uncertainties if not provided
        if ra_weights is None and dec_weights is None:
            if ra_uncerts is not None and dec_uncerts is not None:
                ra_weights = dec_weights = 1 / np.sqrt(ra_uncerts**2 + dec_uncerts**2)
            elif ra_uncerts is not None:
                dec_uncerts = np.ones(n) * np.mean(ra_uncerts)
                ra_weights = dec_weights = 1 / np.sqrt(ra_uncerts**2 + dec_uncerts**2)
            elif dec_uncerts is not None:
                ra_uncerts = np.ones(n) * np.mean(dec_uncerts)
                ra_weights = dec_weights = 1 / np.sqrt(ra_uncerts**2 + dec_uncerts**2)
            else:
                # No uncertainty or weights provided — uniform
                ra_weights = dec_weights = np.ones(n)
        elif ra_weights is None:
            ra_weights = dec_weights
        elif dec_weights is None:
            dec_weights = ra_weights

        ras = measured_positions.ra.to_value(u.deg)
        decs = measured_positions.dec.to_value(u.deg)
        ## RA polynomial fit
        A_ra = self._poly_terms(ras, decs)
        y_ra = ra_offsets.to_value(u.deg)
        w_ra = ra_weights

        ## Apply weights
        Aw = A_ra * w_ra[:, None]
        yw = y_ra * w_ra
        coeffs_ra, *_ = np.linalg.lstsq(Aw, yw, rcond=None)

        ## Dec polynomial fit
        A_dec = self._poly_terms(ras, decs)
        y_dec = dec_offsets.to_value(u.deg)
        w_dec = dec_weights

        Aw = A_dec * w_dec[:, None]
        yw = y_dec * w_dec
        coeffs_dec, *_ = np.linalg.lstsq(Aw, yw, rcond=None)
        
        ra_coeff_dict = {key: coeff for key, coeff in zip(self._poly_keys(), coeffs_ra)}
        dec_coeff_dict = {key: coeff for key, coeff in zip(self._poly_keys(), coeffs_dec)}

        self.ra_model_coefficients=PolynomialCoefficients(coeffs=ra_coeff_dict, labels={'x':'ra', 'y':'dec'}, unit=u.deg, poly_order=self.poly_order)
        self.dec_model_coefficients=PolynomialCoefficients(coeffs=dec_coeff_dict, labels={'x':'ra', 'y':'dec'}, unit=u.deg, poly_order=self.poly_order)
        

    def model_fn(
        self, x: u.Quantity, y: u.Quantity, coeffs: np.ndarray
    ) -> u.Quantity:
        x = np.atleast_1d(x.to_value(u.deg))
        y = np.atleast_1d(y.to_value(u.deg))
        T = self._poly_terms(x, y)
        return (T @ coeffs) * u.deg
    
    def extract_coefficients(self) -> np.ndarray:
        ra_coeff_array = np.zeros(len(self.ra_model_coefficients.coeffs))
        for i, key in enumerate(self._poly_keys()):
            ra_coeff_array[i] = self.ra_model_coefficients.coeffs.get(key, 0)
        
        dec_coeff_array = np.zeros(len(self.dec_model_coefficients.coeffs))
        for i, key in enumerate(self._poly_keys()):
            dec_coeff_array[i] = self.dec_model_coefficients.coeffs.get(key, 0)
        
        
        return ra_coeff_array, dec_coeff_array
    
    def predict(self, pos: SkyCoord) -> SkyCoord:
        racoeffs,deccoeffs = self.extract_coefficients()
        ra_offset = self.model_fn(pos.ra, pos.dec, racoeffs)[0]
        dec_offset = self.model_fn(pos.ra, pos.dec, deccoeffs)[0]
        ra = pos.ra - ra_offset
        dec = pos.dec - dec_offset

        return SkyCoord(ra=ra, dec=dec, frame=pos.frame)
    
    def calculate_statistics(self, positions: SkyCoord):
        new_positions = self.predict(positions)
        ra_residuals = (new_positions.ra - positions.ra).to(u.arcsec)
        dec_residuals = (new_positions.dec - positions.dec).to(u.arcsec)
        mean_ra = np.mean(ra_residuals)
        mean_dec = np.mean(dec_residuals)
        std_ra = np.std(ra_residuals)
        std_dec = np.std(dec_residuals)
        return PointingModelStats(
            mean_ra_offset=mean_ra,
            mean_dec_offset=mean_dec,
            stddev_ra_offset=std_ra,
            stddev_dec_offset=std_dec,
        )