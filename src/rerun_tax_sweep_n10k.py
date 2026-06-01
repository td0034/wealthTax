"""Just rerun the N=10k tax sweep (which is the long part) with the
mortality-corrected metric so we can do the regressive-trap analysis."""
from __future__ import annotations
import json
import time
from pathlib import Path
import numpy as np

from scale_up import run_tax_sweep, plot_tax_sweep, OUT, OUT_DATA


def main():
    t0 = time.time()
    sweep = run_tax_sweep()
    print(f"sweep done in {time.time() - t0:.1f}s")
    plot_tax_sweep(sweep)
    np.savez_compressed(OUT_DATA / "tax_sweep_n10k.npz",
                        thresholds=sweep["thresholds"],
                        rates=sweep["rates"],
                        **{k: v for k, v in sweep["grids"].items()})
    print("\n== top1_share RAW ==")
    print(sweep["grids"]["top1_share"].mean(axis=2).round(3))
    print("\n== top1_share CORRECTED ==")
    print(sweep["grids"]["top1_share_corrected"].mean(axis=2).round(3))


if __name__ == "__main__":
    main()
