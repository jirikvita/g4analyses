#!/usr/bin/env python3
"""Matplotlib version of analyze_energies.py: overlay 1D distributions for all energies."""
import glob
import os
import re
import sys

import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
import uproot

pattern = sys.argv[1] if len(sys.argv) > 1 else "timepix_*keV.root"
files = {}
for path in glob.glob(pattern):
    m = re.search(r"_(\d+(?:\.\d+)?)keV\.root$", os.path.basename(path))
    if m:
        files[float(m.group(1))] = path
energies = sorted(files)
if not energies:
    sys.exit(f"no files match {pattern}")

alpha = 1.0 / (0.2 + len(energies))
colors = plt.cm.tab10(np.arange(len(energies)) % 10)
qmax = max(energies) * 1000 / 3.6 * 1.1  # electrons

fig, ax = plt.subplots(1, 3, figsize=(16, 5))
titles = ["Summed charge per event", "Hit pixels per event", "Charge per hit pixel"]
xlabels = ["charge [e]", "pixels with signal", "charge [e]"]
ylabels = ["events", "events", "pixels"]

for e, col in zip(energies, colors):
    a = uproot.open(files[e])["pixels"].arrays(["i", "charge"], library="ak")
    nhits = ak.to_numpy(ak.num(a["i"]))
    qsum = ak.to_numpy(ak.sum(a["charge"], axis=1))[nhits > 0]
    pq = ak.to_numpy(ak.flatten(a["charge"]))
    data = [(qsum, dict(bins=300, range=(0, qmax))),
            (nhits, dict(bins=np.arange(-0.5, 11.5, 1))),
            (pq, dict(bins=300, range=(0, qmax)))]
    for axis, (x, kw) in zip(ax, data):
        axis.hist(x, histtype="stepfilled", facecolor=(*col[:3], alpha), edgecolor=col,
                  label=f"{e:g} keV, mean {np.mean(x):.4g}", **kw)

for axis, t, xl, yl in zip(ax, titles, xlabels, ylabels):
    axis.set(title=t, xlabel=xl, ylabel=yl, yscale="log")
    axis.legend()

fig.tight_layout()
plt.show()
