#!/usr/bin/env python3
"""Overlay 1D distributions from timepix_<E>keV.root for all energies on one canvas."""
import glob
import os
import re
import sys

import ROOT

ROOT.gROOT.SetBatch(False)
ROOT.EnableImplicitMT(0)

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
colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen + 1, ROOT.kMagenta, ROOT.kCyan + 1,
          ROOT.kOrange + 1, ROOT.kViolet, ROOT.kBlack]

qmax = max(energies) * 1000 / 3.6 * 1.1  # electrons
hists = {"charge": [], "nhits": [], "pix": []}
for k, e in enumerate(energies):
    tag = f"{e:g}"
    df = ROOT.RDataFrame("pixels", files[e])
    h_charge = (df.Filter("i.size() > 0").Define("qsum", "Sum(charge)")
                .Histo1D((f"h_charge_{tag}", "Summed charge per event;charge [e];events",
                          300, 0, qmax), "qsum"))
    h_nhits = (df.Define("n", "(double)i.size()")
               .Histo1D((f"h_nhits_{tag}", "Hit pixels per event;pixels with signal;events",
                         11, -0.5, 10.5), "n"))
    h_pix = df.Histo1D((f"h_pix_{tag}", "Charge per hit pixel;charge [e];pixels",
                        300, 0, qmax), "charge")
    for key, h in (("charge", h_charge), ("nhits", h_nhits), ("pix", h_pix)):
        hh = h.GetValue().Clone()
        hh.SetDirectory(0)
        col = colors[k % len(colors)]
        hh.SetLineColor(col)
        hh.SetFillColorAlpha(col, alpha)
        hh.SetStats(False)
        hists[key].append(hh)

c = ROOT.TCanvas("c", "Timepix energy scan", 1500, 500)
c.Divide(3, 1)
legends = []
for pad, key in enumerate(("charge", "nhits", "pix"), start=1):
    c.cd(pad)
    ROOT.gPad.SetLogy()
    top = max(h.GetMaximum() for h in hists[key]) * 3
    leg = ROOT.TLegend(0.55, 0.55, 0.88, 0.88)
    for k, (e, h) in enumerate(zip(energies, hists[key])):
        h.SetMaximum(top)
        h.SetMinimum(0.5)
        h.Draw("HIST" if k == 0 else "HIST SAME")
        leg.AddEntry(h, f"{e:g} keV, mean {h.GetMean():.4g}", "f")
    leg.Draw()
    legends.append(leg)

c.Update()
input("Press Enter to close the canvas...")
