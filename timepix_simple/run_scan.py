#!/usr/bin/env python3
"""Run the timepix simulation for a list of electron energies (keV)."""
import os
import subprocess
import sys

ENERGIES = [10, 15, 20, 30, 40, 50, 70, 100]
NEVENTS = 20000
G4_ENV = "/home/qitek/install/geant4-v11.1.1-install/bin/geant4.sh"

here = os.path.dirname(os.path.abspath(__file__))
nevents = int(sys.argv[1]) if len(sys.argv) > 1 else NEVENTS

for e in ENERGIES:
    print(f"=== {e} keV, {nevents} events ===", flush=True)
    cmd = f". {G4_ENV} && ./timepix run_novis_scan.mac energy={e} nevents={nevents}"
    subprocess.run(["bash", "-c", cmd], cwd=here, check=True)
