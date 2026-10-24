"""
The full system (anchoring.py evaluate: odometry + anchors every 1 s + pose graph, error at the US
image) with SCR anchors solved by Kabsch instead of PnP: scr_anchor.localize_kabsch, 3D-3D RANSAC
between the measured depth and the predicted room coordinates, and an inlier gate (fewer than
--scr-gate inliers = no anchor at that time).

anchoring.py's SCR mode imports scr.localize when it runs and calls it right after
base.load_frame(run, row), so this wrapper replaces scr.localize and remembers which frame load_frame
read last, to fetch that frame's depth; it also provides scr.localize_multi for --scr-frames.
Everything after -- goes to anchoring.py (in this repo). Run from this repo's folder; the odometry run
(--odometry) and the anchor pairs (--pairs) are data from rgbd-us, given by path.

  python tools/anchoring_kabsch.py -- evaluate --anchor scr --scr-ckpt runs/v1-3XX/best.pt \\
      --root $DATA/train_3XX --scan-runs room-301 room-302 --test-root $DATA/train_3XX \\
      --odometry-source classical-vo-train_3XX --odometry $ODO/rpr-rgb-gap8-12XX-gru8 \\
      --pairs $ODO/anchor-pairs/pairs_3XX.json --pgo --start anchor --out runs/sys-final-3XX

anchoring.py options added in this repo: --gate-recover N (accept an anchor again when N consecutive
rejected anchors agree), --scr-frames M (one anchor from M chain frames, solved by localize_multi).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scr_anchor                                            # noqa: E402

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

    def localize_multi(net, ck, ds, run, rows, rels, K, full_w, device, min_inliers=30):
        """anchoring.py --scr-frames > 1: one anchor from several chain frames. Each frame's cell
        correspondences are moved into the newest frame's camera with rels (from the odometry), then
        pooled into one Kabsch RANSAC; the inlier gate scales with the number of frames."""
        Cs, Ps = [], []
        for row, rel in zip(rows, rels):
            C, P = scr_anchor.cell_correspondences(net, ck, load_frame(ds, run, row)[0],
                                                   scr.load_depth_mm(ds, ds.root, run, row), K, full_w, device,
                                                   ours.kabsch_max_depth)
            Cs.append(C @ rel[:3, :3].T + rel[:3, 3])
            Ps.append(P)
        T, n = scr_anchor.kabsch_ransac(np.concatenate(Cs), np.concatenate(Ps), ours.kabsch_thr, min_inliers,
                                        rng=np.random.default_rng(ours.seed + rows[0]))
        if T is not None and n < ours.scr_gate * len(rows):
            return None, n
        return T, n

    dataloader.RPRDataset.load_frame = remember
    scr.localize = localize
    scr.localize_multi = localize_multi
    scr.load_scr = scr_anchor.load_model          # checkpoints with either head


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
