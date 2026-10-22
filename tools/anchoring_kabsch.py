"""
The full rgbd-us system (anchoring.py evaluate: odometry + anchors every 1 s + pose graph, error at
the US image) with SCR anchors solved by Kabsch instead of PnP: scr_anchor.localize_kabsch, 3D-3D
RANSAC between the measured depth and the predicted room coordinates, and an inlier gate (fewer
than --scr-gate inliers = no anchor at that time).

anchoring.py is used unchanged: its SCR mode imports scr.localize when it runs and calls it right
after base.load_frame(run, row), so this wrapper replaces scr.localize and remembers which frame
load_frame read last, to fetch that frame's depth. Everything after --, plus nothing else, goes to
anchoring.py; run it from the rgbd-us folder, as anchoring.py expects.

  cd $RGBD_US
  python <US_SCR>/tools/anchoring_kabsch.py --scr-gate 400 -- evaluate --anchor scr \\
      --scr-ckpt <US_SCR>/runs/v1-3XX/best.pt --root data/train_3XX --scan-runs room-301 room-302 ... --pgo
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scr_anchor                                            # noqa: E402  (puts $RGBD_US first on sys.path)

import numpy as np                                           # noqa: E402

import dataloader                                            # noqa: E402
import scr                                                   # noqa: E402


def install(ours):
    """Replace scr.localize by the gated Kabsch solver; load_frame remembers the frame it read."""
    last = {}
    load_frame = dataloader.RPRDataset.load_frame

    def remember(self, name, i, bc=None):
        last.update(ds=self, name=name, row=int(i))
        return load_frame(self, name, i, bc)

    def localize(net, ck, rgb, K, full_w, device, px=10.0, min_inliers=30, iters=2000):
        ds, name, row = last["ds"], last["name"], last["row"]
        depth = scr.load_depth_mm(ds, ds.root, name, row)
        T, n = scr_anchor.localize_kabsch(net, ck, rgb, depth, K, full_w, device, ours.kabsch_thr,
                                          ours.kabsch_max_depth, min_inliers,
                                          rng=np.random.default_rng(ours.seed + row))
        if T is not None and n < ours.scr_gate:
            return None, n
        return T, n

    dataloader.RPRDataset.load_frame = remember
    scr.localize = localize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kabsch-thr", type=float, default=20.0, help="inlier threshold (mm)")
    ap.add_argument("--kabsch-max-depth", type=float, default=2000.0, help="leave out cells farther than this (mm)")
    ap.add_argument("--scr-gate", type=int, default=400, help="fewer Kabsch inliers = no anchor (0: no gate)")
    ap.add_argument("--seed", type=int, default=0)
    ours, rest = ap.parse_known_args()
    if rest and rest[0] == "--":
        rest = rest[1:]

    install(ours)
    print(f"SCR anchors by Kabsch ({ours.kabsch_thr:g} mm, cells < {ours.kabsch_max_depth:g} mm), "
          f"gate >= {ours.scr_gate} inliers", flush=True)

    import anchoring
    sys.argv = ["anchoring.py"] + rest
    anchoring.main()


if __name__ == "__main__":
    main()
