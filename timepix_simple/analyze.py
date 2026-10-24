#!/usr/bin/env python3
"""Analyse timepix.root: per-event charge, pixel hit map, hits per event."""
import os
import sys

import ROOT

#ROOT.gStyle.SetOptTitle(0)

fname = sys.argv[1] if len(sys.argv) > 1 else "timepix.root"
f = ROOT.TFile.Open(fname)
tree = f.Get("pixels")

npix = 256
h_charge = ROOT.TH1D("h_charge", "Summed charge per event;charge [e];events", 200, 0, 8000)
h_map = ROOT.TH2D("h_map", "Pixel hit map;i;j", npix, 0, npix, npix, 0, npix)
h_nhits = ROOT.TH1D("h_nhits", "Hit pixels per event;pixels with signal;events", 11, -0.5, 10.5)
h_pix = ROOT.TH1D("h_pix", "Charge per hit pixel;charge [e];pixels", 200, 0, 8000)

for event in tree:
    n = len(event.i)
    h_nhits.Fill(n)
    if n == 0:
        continue
    h_charge.Fill(sum(event.charge))
    for i, j, q in zip(event.i, event.j, event.charge):
        h_map.Fill(i, j)
        h_pix.Fill(q)

ROOT.gStyle.SetOptStat(1110)
c = ROOT.TCanvas("c", "Timepix analysis", 1200, 900)
c.Divide(2, 2)

c.cd(1)
ROOT.gPad.SetLogy()
h_charge.SetFillColor(ROOT.kGreen)
h_charge.Draw()
c.cd(2)
h_map.Draw("COLZ")
c.cd(3)
ROOT.gPad.SetLogy()
h_nhits.SetFillColor(ROOT.kCyan)
h_nhits.Draw()
c.cd(4)
ROOT.gPad.SetLogy()
h_pix.SetFillColor(ROOT.kMagenta)
h_pix.Draw()

c.Update()
out = os.path.splitext(os.path.basename(fname))[0] + "_analysis"
for ext in ("png", "pdf"):
    c.SaveAs(f"{out}.{ext}")
input("Press Enter to close the canvas...")
