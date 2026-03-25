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
plt.imshow(pad_map, vmin=-300, vmax=300, origin="lower")
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

tmap_path = "/home/jack/dev/mapcat/.pytest_cache/d1maps/15056/depth1_1505603190_pa4_f150_map.fits"
tmap = enmap.read_map(str(tmap_path))
coverage_tiles = get_sky_coverage(tmap)

tbox = tmap.box()

tdec_min, tra_max = np.rad2deg(tbox[0])
tdec_max, tra_min = np.rad2deg(tbox[1])

tpad_low_dec = int((90 + tdec_min) * 6 * 2)
tpad_high_dec = int((90 - tdec_max) * 6 * 2)

tpad_low_ra = int((180 + tra_min) * 6 * 2)
tpad_high_ra = int((180 - tra_max) * 6 * 2)

tmap = tmap[0][::10, ::10]
tpad_map = np.pad(
    tmap,
    ((tpad_low_dec, tpad_high_dec), (tpad_low_ra, tpad_high_ra)),
    mode="constant",
    constant_values=0,
)

plt.imshow(tpad_map, vmin=-300, vmax=300, origin="lower", alpha=0.5, cmap="seismic")

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
