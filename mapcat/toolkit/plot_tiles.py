import matplotlib.pyplot as plt
import numpy as np
from pixell import enmap

from mapcat.toolkit.update_sky_coverage import *

imap_path = "/home/jack/act_planck_s08_s22_f150_daynight_map.fits"
imap = enmap.read_map(str(imap_path))

box = imap.box()

dec_min, ra_max = np.rad2deg(box[0])
dec_max, ra_min = np.rad2deg(box[1])

pad_low = int((90 + dec_min) * 6 * 2)
pad_high = int((90 - dec_max) * 6 * 2)

imap = imap[0][::10, ::10]

pad_map = np.pad(
    imap, ((pad_low, pad_high), (0, 0)), mode="constant", constant_values=0
)
del imap

left_limit = pad_map.shape[1]
right_limit = 0
top_limit = pad_map.shape[0]
bottom_limit = 0
extent = [left_limit, right_limit, bottom_limit, top_limit]


plt.imshow(pad_map, vmin=-300, vmax=300, origin="lower", extent=extent)
plt.vlines(
    np.arange(0, 360 * 6 * 2, 10 * 6 * 2), ymin=0, ymax=180 * 6 * 2, color="black", lw=1
)
plt.hlines(
    np.arange(0, 180 * 6 * 2, 10 * 6 * 2), xmin=0, xmax=360 * 6 * 2, color="black", lw=1
)
plt.xticks(np.arange(0, 360 * 6 * 2, 20 * 6 * 2), labels=np.arange(0, 360, 20))
plt.yticks(np.arange(0, 180 * 6 * 2, 10 * 6 * 2), labels=np.arange(-90, 90, 10))
plt.xlabel("RA (degrees)")
plt.ylabel("Dec (degrees)")

d1map_path = "/home/jack/dev/mapcat/.pytest_cache/d1maps/15056/depth1_1505603190_pa4_f150_map.fits"
d1map = enmap.read_map(str(d1map_path))
coverage_tiles = get_sky_coverage(d1map)

d1box = d1map.box()

d1dec_min, d1ra_max = np.rad2deg(d1box[0])
d1dec_max, d1ra_min = np.rad2deg(d1box[1])

d1pad_low_dec = int((90 + d1dec_min) * 6 * 2)
d1pad_high_dec = int((90 - d1dec_max) * 6 * 2)

d1pad_low_ra = int((180 + d1ra_min) * 6 * 2)
d1pad_high_ra = int((180 - d1ra_max) * 6 * 2)

d1map = d1map[0][::10, ::10]
d1pad_map = np.pad(
    d1map,
    ((d1pad_low_dec, d1pad_high_dec), (d1pad_high_ra, d1pad_low_ra)),
    mode="constant",
    constant_values=0,
)

plt.imshow(
    d1pad_map,
    vmin=-300,
    vmax=300,
    origin="lower",
    alpha=0.5,
    cmap="seismic",
    extent=extent,
)

for tile in coverage_tiles:
    plt.gca().add_patch(
        plt.Rectangle(
            (tile[0] * 10 * 6 * 2, tile[1] * 10 * 6 * 2),
            10 * 6 * 2,
            10 * 6 * 2,
            fill=False,
            edgecolor="red",
            lw=2,
        )
    )

plt.savefig("/mnt/c/Users/Jack/Desktop/act_coverage.png", dpi=300)
