#!/usr/bin/env python3
"""Matplotlib version of analyze.py: per-event charge, pixel hit map, hits per event."""
import sys

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
import uproot

fname = sys.argv[1] if len(sys.argv) > 1 else "timepix.root"
npix = 256

a = uproot.open(fname)["pixels"].arrays(["i", "j", "charge"], library="ak")
nhits = ak.to_numpy(ak.num(a["i"]))
hit = nhits > 0
qsum = ak.to_numpy(ak.sum(a["charge"], axis=1))[hit]
pi = ak.to_numpy(ak.flatten(a["i"]))
pj = ak.to_numpy(ak.flatten(a["j"]))
pq = ak.to_numpy(ak.flatten(a["charge"]))

fig, ax = plt.subplots(2, 2, figsize=(12, 9))

ax[0, 0].hist(qsum, bins=200, range=(0, 8000), color="limegreen")
ax[0, 0].set(title="Summed charge per event", xlabel="charge [e]", ylabel="events", yscale="log")

h = ax[0, 1].hist2d(pi, pj, bins=npix, range=[[0, npix], [0, npix]], cmap="viridis")
fig.colorbar(h[3], ax=ax[0, 1], label="hits")
ax[0, 1].set(title="Pixel hit map", xlabel="i", ylabel="j", aspect="equal")

ax[1, 0].hist(nhits, bins=np.arange(-0.5, 11.5, 1), color="cyan", edgecolor="k")
ax[1, 0].set(title="Hit pixels per event", xlabel="pixels with signal", ylabel="events", yscale="log")

ax[1, 1].hist(pq, bins=200, range=(0, 8000), color="magenta")
ax[1, 1].set(title="Charge per hit pixel", xlabel="charge [e]", ylabel="pixels", yscale="log")

fig.tight_layout()
plt.show()
