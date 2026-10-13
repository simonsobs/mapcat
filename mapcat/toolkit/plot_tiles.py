import argparse as ap
from itertools import pairwise
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from pixell import enmap

from mapcat.toolkit.update_sky_coverage import _separable_car_axes, get_sky_coverage


def _show_map(map_data, step=10, **kwargs):
    """Display sampled CAR pixels in celestial coordinates, splitting at RA=0.

    Raises
    ------
    ValueError
        If the map is not an unrotated equatorial CAR map.
    """
    axes = _separable_car_axes(map_data)
    if axes is None:
        raise ValueError("plot_tiles requires an unrotated equatorial CAR map")
    dec, ra = axes
    # Use the original pixel centers: striding an enmap changes its WCS centers.
    dec, ra = dec[::step], ra[::step] % 360
    pixels = np.asarray(map_data.preflat[0])[::step, ::step]
    matrix = map_data.wcs.wcs.get_pc()
    dra, ddec = map_data.wcs.wcs.cdelt * np.diag(matrix) * step
    boundaries = np.r_[0, np.flatnonzero(np.abs(np.diff(ra)) > 180) + 1, len(ra)]
    for start, stop in pairwise(boundaries):
        extent = [
            ra[start] - dra / 2,
            ra[stop - 1] + dra / 2,
            dec[0] - ddec / 2,
            dec[-1] + ddec / 2,
        ]
        plt.imshow(pixels[:, start:stop], origin="lower", extent=extent, **kwargs)
        # A pixel footprint straddling RA=0 also appears at the other sky edge.
        for shift in ([360] if min(extent[:2]) < 0 else []) + (
            [-360] if max(extent[:2]) > 360 else []
        ):
            plt.imshow(
                pixels[:, start:stop],
                origin="lower",
                extent=[extent[0] + shift, extent[1] + shift, *extent[2:]],
                **kwargs,
            )


def main():
    parser = ap.ArgumentParser()
    parser.add_argument("--imap_path", type=str, required=True)
    parser.add_argument("--d1map_path", type=str, required=True)
    parser.add_argument("--opath", type=str, required=True)
    args = parser.parse_args()

    # Preserve the existing palette and optional notebook style.
    try:
        import socolors  # noqa: F401
    except ImportError:
        pass
    if "notebook" in plt.style.available:
        plt.style.use("notebook")

    imap = enmap.read_map(str(args.imap_path), preflat=True, sel=0)
    _show_map(imap, vmin=-200, vmax=200, zorder=-1000, cmap="grey")
    del imap

    plt.vlines(np.arange(0, 360, 10), ymin=-90, ymax=90, color="black", lw=1)
    plt.hlines(np.arange(-90, 90, 10), xmin=0, xmax=360, color="black", lw=1)
    plt.xticks(np.arange(0, 360, 20), labels=np.arange(0, 360, 20))
    plt.yticks(np.arange(-90, 90, 10), labels=np.arange(-90, 90, 10))
    plt.xlabel("RA (degrees)")
    plt.ylabel("Dec (degrees)")

    d1map = enmap.read_map(str(args.d1map_path))
    coverage_tiles = get_sky_coverage(d1map)
    sampled = np.asarray(d1map.preflat[0])[::10, ::10]
    observed = sampled[np.isfinite(sampled) & (sampled != 0)]
    vmin, vmax = np.percentile(observed, (1, 99)) if observed.size else (0, 1)
    _show_map(d1map, vmin=vmin, vmax=vmax, alpha=0.9, cmap="twilight_shifted")

    for tile in coverage_tiles:
        plt.gca().add_patch(
            plt.Rectangle(
                (tile[0] * 10, tile[1] * 10 - 90),
                10,
                10,
                fill=False,
                edgecolor="C0",
                lw=2,
            )
        )

    plt.xlim(360, 0)
    plt.ylim(-90, 90)
    opath = Path(args.opath)
    opath.mkdir(parents=True, exist_ok=True)
    plt.savefig(opath / "act_coverage.png", dpi=300)
    plt.close()


if __name__ == "__main__":
    main()
