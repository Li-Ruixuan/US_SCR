"""
Export our sweeps in the TUS-REC format, to run Li et al.'s US-only method (the TUS-REC
baseline code of the same group) on our data as the literature US baseline.

TUS-REC layout, one root per split (train / val / test, so their code cannot mix our split):
    <out>/<split>/frames_transfs/<subject>/<scan>.h5     frames (N, 480, 640) uint8
                                                         tforms (N, 4, 4) float32: tracker tool -> tracker
                                                                ("camera") space, mm = our marker pose
    <out>/<split>/calib_matrix.csv                       our calibration for the US crop, TUS-REC format
    <out>/export_info.json                               what went where, frame rates, settings

frames: the US crop ([121,80]-[619,440] of the 800x600 screen grab) resized to the native 640x480
grid that calib_matrix.csv refers to. Only distinct US frames (grabber repeats dropped) and none
with the probe in the air at the start or end of the sweep. tforms: the marker pose interpolated
at each US frame's own timestamp (the measured pose clock offset applied, as in match_streams.py).
Wherever the marker was lost, the sweep is split into separate scans (<run>_s<k>.h5, at least
--min-frames frames each). The baseline loader requires exactly 2 scans per subject folder, so the
scans of a split are grouped in pairs into pseudo-subjects 000, 001, ... (with an odd count the
longest scan is cut into two continuous halves); export_info.json lists which sweep is where.

Their train.py splits all subjects of DATA_PATH randomly into 5 folds; to keep our split, replace
the fold lines in their train.py by (see note_RPR.md §6.7):
    dset_train = Dataset(data_path=<out>/train/frames_transfs, num_samples=opt.NUM_SAMPLES, sample_range=opt.SAMPLE_RANGE)
    dset_val   = Dataset(data_path=<out>/val/frames_transfs,   num_samples=opt.NUM_SAMPLES, sample_range=opt.SAMPLE_RANGE)

  python tools/export_tusrec.py --out data/tusrec_ours \\
      --train data/train_2XX --val-runs run-205 run-211 --test data/train_3XX
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

import cv2
import h5py
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from match_streams import dedup_pose, interp_pose, us_frame_flags   # noqa: E402

CALIB_HW = (480, 640)


def pose_matrix(p):
    from scipy.spatial.transform import Rotation
    T = np.eye(4)
    T[:3, :3] = Rotation.from_quat(p[3:]).as_matrix()
    T[:3, 3] = p[:3]
    return T


def export_run(run_dir, out_dir, subject, args):
    """One sweep -> one or more TUS-REC scans. Returns a summary dict."""
    us = pd.read_csv(run_dir / "us.csv").sort_values("timestamp").reset_index(drop=True)
    pose = dedup_pose(pd.read_csv(run_dir / "pose.csv").sort_values("timestamp").reset_index(drop=True))
    rep = json.load(open(run_dir / "match_report.json")) if (run_dir / "match_report.json").exists() else {}
    if rep.get("pose_offset_applied") and rep.get("pose_offset_ms") is not None:
        pose["timestamp"] = pose["timestamp"] - rep["pose_offset_ms"] / 1e3
    r = json.load(open(run_dir / "us_roi.json"))
    roi = (*r["start"], *r["end"])
    repeat, air = us_frame_flags(run_dir, us, roi, args.repeat_thr)

    keep, T = [], []
    for i in range(len(us)):
        if repeat[i] or air[i]:
            continue
        p = interp_pose(pose, float(us["timestamp"].iloc[i]), args.pose_max_gap)
        keep.append(i if p is not None else -1)
        T.append(pose_matrix(np.asarray(p)) if p is not None else None)
    # split where the marker was lost
    scans, cur = [], []
    for i, t in zip(keep, T):
        if i < 0:
            if cur:
                scans.append(cur)
            cur = []
        else:
            cur.append((i, t))
    if cur:
        scans.append(cur)
    scans = [s for s in scans if len(s) >= args.min_frames]

    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for k, sc in enumerate(scans):
        frames = np.stack([cv2.resize(cv2.imread(str(run_dir / us["file"].iloc[i]), cv2.IMREAD_GRAYSCALE)
                                      [roi[1]:roi[3], roi[0]:roi[2]], CALIB_HW[::-1], interpolation=cv2.INTER_AREA)
                           for i, _ in sc]).astype(np.uint8)
        tforms = np.stack([t for _, t in sc]).astype(np.float32)
        name = run_dir.name if len(scans) == 1 else f"{run_dir.name}_s{k}"
        with h5py.File(out_dir / f"{name}.h5", "w") as h:
            h.create_dataset("frames", data=frames, compression="gzip", compression_opts=4)
            h.create_dataset("tforms", data=tforms)
        ts = us["timestamp"].to_numpy()[[i for i, _ in sc]]
        written.append({"scan": f"{name}.h5", "collection": subject, "frames": len(sc), "fps": float((len(ts) - 1) / (ts[-1] - ts[0]))})
    n_us = len(us)
    print(f"  {run_dir.name}: {n_us} grabbed, {int(np.sum(repeat))} repeats, {int(np.sum(air))} in air -> "
          + ", ".join(f"{w['scan']} ({w['frames']} frames, {w['fps']:.1f} fps)" for w in written))
    return {"run": run_dir.name, "grabbed": n_us, "repeats": int(np.sum(repeat)), "air": int(np.sum(air)),
            "scans": written}


def pair_into_subjects(tmp, dst):
    """Scans in tmp/ -> dst/000/, dst/001/, ... with exactly 2 scans each. Returns {subject: [scans]}."""
    scans = sorted(tmp.glob("*.h5"))
    if len(scans) % 2:                         # odd: cut the longest scan into two continuous halves
        big = max(scans, key=lambda p: h5py.File(p, "r")["frames"].shape[0])
        with h5py.File(big, "r") as h:
            f, t = h["frames"][()], h["tforms"][()]
        mid = len(f) // 2
        for k, sl in enumerate((slice(0, mid), slice(mid, None))):
            with h5py.File(tmp / f"{big.stem}_h{k}.h5", "w") as h:
                h.create_dataset("frames", data=f[sl], compression="gzip", compression_opts=4)
                h.create_dataset("tforms", data=t[sl])
        big.unlink()
        scans = sorted(tmp.glob("*.h5"))
    groups = {}
    for i in range(0, len(scans), 2):
        sub = dst / f"{i // 2:03d}"
        sub.mkdir(parents=True, exist_ok=True)
        groups[sub.name] = []
        for p in scans[i:i + 2]:
            shutil.move(str(p), str(sub / p.name))
            groups[sub.name].append(p.name)
    tmp.rmdir()
    return groups


def sweeps_of(root):
    return sorted(p for p in Path(root).iterdir()
                  if p.name.startswith("run-") and (p / "us.csv").exists() and (p / "us_roi.json").exists())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="export root (one sub-root per split)")
    ap.add_argument("--train", nargs="+", required=True, help="collection folders for training (+ validation)")
    ap.add_argument("--val-runs", nargs="+", default=[], help="sweeps of --train that go to the val split")
    ap.add_argument("--test", nargs="*", default=[], help="collection folders for the test split")
    ap.add_argument("--calib", default=str(ROOT / "calib_matrix.csv"), help="TUS-REC-format calibration of our crop")
    ap.add_argument("--repeat-thr", type=float, default=0.5)
    ap.add_argument("--pose-max-gap", type=float, default=0.080, help="s, as in match_streams.py")
    ap.add_argument("--min-frames", type=int, default=40, help="shorter pieces (marker loss) are dropped")
    args = ap.parse_args()
    out = Path(args.out)

    info = {"settings": vars(args), "splits": {}}
    jobs = [("train", r, sw) for r in args.train for sw in sweeps_of(r) if sw.name not in args.val_runs]
    jobs += [("val", r, sw) for r in args.train for sw in sweeps_of(r) if sw.name in args.val_runs]
    jobs += [("test", r, sw) for r in args.test for sw in sweeps_of(r)]
    for split, root, sw in jobs:
        subject = Path(root).name                                    # e.g. train_2XX
        d = out / split / "_scans"
        if split not in info["splits"]:
            print(f"{split}:")
            (out / split).mkdir(parents=True, exist_ok=True)
            shutil.copy(args.calib, out / split / "calib_matrix.csv")
        info["splits"].setdefault(split, []).append(export_run(sw, d, subject, args))
    info["subjects"] = {split: pair_into_subjects(out / split / "_scans", out / split / "frames_transfs")
                        for split in info["splits"]}
    json.dump(info, open(out / "export_info.json", "w"), indent=2)
    for split, runs in info["splits"].items():
        n = sum(w["frames"] for r in runs for w in r["scans"])
        print(f"{split}: {sum(len(r['scans']) for r in runs)} scans, {n} frames")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
