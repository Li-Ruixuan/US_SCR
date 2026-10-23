"""
U1: how well does US measure the probe's IN-PLANE motion? (diagnostic, no learning)

The camera gives the absolute pose; US could add what the camera measures worst, the motion in the
US image plane itself, at 0.22 mm per pixel. Before building that into the pose graph, measure it:
for US frames k apart in a sweep, a rigid 2D registration (OpenCV ECC, Euclidean, two-level
pyramid, speckle blurred) against the Polaris truth.

Geometry: calib_matrix.csv (rgbd-us, TUS-REC format) maps 1-based pixels of the US crop resized
to 640 x 480 to US-plane mm (scaling) and on to the marker (rigid). Frames are resampled to an
isotropic 0.25 mm grid so a rigid motion in mm is a rigid motion in pixels. For frames i and j
the truth is T_ji = inv(T_world_us_j) @ T_world_us_i; a point p on frame i's plane lands at
(T_ji p)[:2] in frame j's plane (in-plane) and (T_ji p)[2] off it (out-of-plane, invisible to US).
Errors are mean point errors over the US fan:
  in-plane error   |ECC estimate - truth| in the image plane (what US measures)
  zero motion      |no motion - truth| in the image plane (the true in-plane motion)
  out-of-plane     |truth| along the plane normal (what US cannot see; it also changes the
                   cross-section, which is what limits the registration)
Static screen overlays and the background are masked by their low variance over the sweep.

U2 in the same run: the correlation left after the in-plane alignment against the true
out-of-plane distance (speckle decorrelation), and how well that curve, built on the other
sweeps, predicts the distance of a held-out sweep. The out-of-plane motion is where these sweeps
move; if US can measure it, it can join the pose graph there.

Frames: usable sweep rows of rgbd-us RPRDataset (Polaris pose, not in the air, US present), new
US frames only (us_repeat = 0), every --every-th one as a start, partners k new US frames later
within the same segment.

  python tools/us_inplane.py --root $DATA/train_3XX --out runs/us-inplane-3XX
  python tools/us_inplane.py --root $DATA/train_3XX --runs run-316 --out runs/us-inplane-316
"""

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "rgbdus"))

import cv2                                                               # noqa: E402
import numpy as np                                                       # noqa: E402
from tqdm import tqdm                                                    # noqa: E402

from dataloader import RPRConfig, RPRDataset, load_hand_eye, load_us_roi, test_sweeps   # noqa: E402

CALIB_HW = (480, 640)
ISO_MM = 0.25                       # mm per pixel of the isotropic registration grid


def read_calib(path):
    """calib_matrix.csv -> (scaling, rigid): pixels (1-based, 640x480) -> US mm -> marker mm."""
    rows = [l.strip().split(",") for l in open(path)]
    return np.array(rows[1:5], float), np.array(rows[6:10], float)


class USFrames:
    """US frames of one sweep on the isotropic grid: pixel (j, l) is US-plane mm (ISO_MM j, ISO_MM l)."""

    def __init__(self, run_dir, df, scaling):
        self.dir, self.df = Path(run_dir), df
        self.x0, self.y0, self.x1, self.y1 = load_us_roi(self.dir)
        sx, sy = scaling[0, 0], scaling[1, 1]
        self.W, self.H = int(CALIB_HW[1] * sx / ISO_MM), int(CALIB_HW[0] * sy / ISO_MM)
        # iso pixel j <- calibration pixel u = ISO_MM j / sx (1-based) = index u - 1 (0-based)
        self.M = np.array([[ISO_MM / sx, 0, -1], [0, ISO_MM / sy, -1]], np.float64)

    def load(self, row):
        g = cv2.imread(str(self.dir / self.df["us"].iloc[row]), cv2.IMREAD_GRAYSCALE)
        g = cv2.resize(g[self.y0:self.y1, self.x0:self.x1], CALIB_HW[::-1], interpolation=cv2.INTER_LINEAR)
        return cv2.warpAffine(g.astype(np.float32), self.M, (self.W, self.H),
                              flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)

    def fan_mask(self, rows, n=60):
        """Pixels that change over the sweep: the US fan without static overlays and background."""
        stack = np.stack([self.load(r) for r in rows[:: max(1, len(rows) // n)]])
        m = ((stack.std(0) > 4) & (stack.mean(0) > 5)).astype(np.uint8)
        return cv2.erode(m, np.ones((9, 9), np.uint8))


def ecc(template, image, mask):
    """(2x3 Euclidean warp W in iso pixels with image(W x) ~ template(x), correlation coefficient
    after alignment), coarse-to-fine; (None, None) if ECC fails."""
    crit = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 100, 1e-5)
    W = np.eye(2, 3, dtype=np.float32)
    try:
        for f in (0.5, 1.0):
            t = cv2.resize(template, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
            i = cv2.resize(image, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
            m = cv2.resize(mask, t.shape[::-1], interpolation=cv2.INTER_NEAREST)
            if f == 1.0:
                W[:, 2] *= 2
            cc, W = cv2.findTransformECC(t, i, W, cv2.MOTION_EUCLIDEAN, crit, m, 5)
    except cv2.error:
        return None, None
    return W.astype(np.float64), float(cc)


def summarise(recs):
    if not recs:
        return {"pairs": 0}
    a = lambda k: np.array([r[k] for r in recs if r.get(k) is not None], float)
    err, zero, oop = a("inplane_err_mm"), a("zero_motion_mm"), a("out_of_plane_mm")
    med = lambda v: float(np.median(v)) if len(v) else None
    p90 = lambda v: float(np.percentile(v, 90)) if len(v) else None
    return {"pairs": len(recs), "failed_pct": 100 * float(np.mean([r["inplane_err_mm"] is None for r in recs])),
            "inplane_err_median": med(err), "inplane_err_p90": p90(err),
            "zero_motion_median": med(zero), "zero_motion_p90": p90(zero),
            "out_of_plane_median": med(oop),
            "rot_err_deg_median": med(a("rot_err_deg")), "true_rot_deg_median": med(a("true_rot_deg"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="collection folder with the sweeps, e.g. $DATA/train_3XX")
    ap.add_argument("--runs", nargs="+", default=None, help="sweeps (default: every run-* in --root)")
    ap.add_argument("--gaps", type=int, nargs="+", default=[1, 3, 10], help="k: new US frames between the pair")
    ap.add_argument("--every", type=int, default=5, help="every n-th new US frame as a start")
    ap.add_argument("--out", required=True)
    ap.add_argument("--hand-eye", default=str(REPO / "T_marker_cam.npy"))
    ap.add_argument("--calib", default=str(REPO / "calib_matrix.csv"), help="US calibration (TUS-REC format)")
    args = ap.parse_args()

    T_mc = load_hand_eye(args.hand_eye, "mm")
    scaling, rigid = read_calib(args.calib)
    sweeps = test_sweeps(args.root, args.runs)
    ds = RPRDataset(args.root, sweeps, [], RPRConfig(T_marker_cam=T_mc))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    recs = []
    for sw in sweeps:
        r = ds.runs[sw]
        df = r["df"]
        new = (pd_num(df, "us_repeat") != 1)
        T_world_us = r["T_world_cam"] @ np.linalg.inv(T_mc) @ rigid              # US-plane mm -> world
        us = USFrames(Path(args.root) / sw, df, scaling)
        segs = [s[new[s]] for s in r["segments"]]
        mask = us.fan_mask(np.concatenate(segs))
        jj, ll = np.nonzero(mask[::8, ::8])
        P = np.stack([ll * 8 * ISO_MM, jj * 8 * ISO_MM, np.zeros(len(jj)), np.ones(len(jj))])   # fan points, mm
        cache = {}

        def img(row):
            if row not in cache:
                if len(cache) > 64:
                    cache.clear()
                cache[row] = cv2.GaussianBlur(us.load(row), (0, 0), 1.5)
            return cache[row]

        pairs = [(s[a], s[a + k], k) for s in segs for a in range(0, len(s), args.every) for k in args.gaps
                 if a + k < len(s)]
        for i, j, k in tqdm(pairs, desc=sw, leave=False):
            T_ji = np.linalg.inv(T_world_us[j]) @ T_world_us[i]
            q = T_ji @ P                                                          # frame-i fan points in frame j
            W, cc = ecc(img(i), img(j), mask)
            rec = {"run": sw, "i": int(i), "j": int(j), "k": k,
                   "zero_motion_mm": float(np.linalg.norm(q[:2] - P[:2], axis=0).mean()),
                   "out_of_plane_mm": float(np.abs(q[2]).mean()),
                   "true_rot_deg": float(np.degrees(np.arctan2(T_ji[1, 0] - T_ji[0, 1], T_ji[0, 0] + T_ji[1, 1]))),
                   "inplane_err_mm": None, "rot_err_deg": None, "ncc": cc}
            if W is not None:
                Wmm = W.copy()
                Wmm[:, 2] *= ISO_MM                                               # iso pixels -> mm
                est = Wmm @ np.vstack([P[:2], np.ones(P.shape[1])])
                rec["inplane_err_mm"] = float(np.linalg.norm(est - q[:2], axis=0).mean())
                rec["rot_err_deg"] = abs(float(np.degrees(np.arctan2(W[1, 0], W[0, 0]))) - rec["true_rot_deg"])
            recs.append(rec)
        s = summarise([x for x in recs if x["run"] == sw])
        print(f"  {sw}: {s['pairs']} pairs, fan {mask.sum()} px", flush=True)

    per = {(sw, k): summarise([x for x in recs if x["run"] == sw and x["k"] == k]) for sw in sweeps for k in args.gaps}
    allk = {k: summarise([x for x in recs if x["k"] == k]) for k in args.gaps}
    f = lambda v, d=1: "–" if v is None else f"{v:.{d}f}"
    md = [f"# U1: in-plane US registration vs Polaris ({Path(args.root).name})", "",
          "Mean point error over the US fan (mm), median / p90 over frame pairs; ECC Euclidean on a 0.25 mm grid. "
          "'zero motion' = the true in-plane motion; 'out-of-plane' = the motion US cannot see.", "",
          "| sweep | k | pairs | ECC failed | **in-plane error** | zero motion | out-of-plane | in-plane rotation error ° (true) |",
          "|---|---|---|---|---|---|---|---|"]
    for (sw, k), s in list(per.items()) + [(("**all**", k), s) for k, s in allk.items()]:
        if not s["pairs"]:
            continue
        md.append(f"| {sw} | {k} | {s['pairs']} | {s['failed_pct']:.0f} % | **{f(s['inplane_err_median'], 2)} / "
                  f"{f(s['inplane_err_p90'], 2)}** | {f(s['zero_motion_median'], 2)} / {f(s['zero_motion_p90'], 2)} | "
                  f"{f(s['out_of_plane_median'], 2)} | {f(s['rot_err_deg_median'], 2)} ({f(s['true_rot_deg_median'], 2)}) |")
    md += decorrelation(recs)
    json.dump({"args": vars(args), "summary": {str(k): v for k, v in allk.items()}, "pairs": recs},
              open(out / "us_inplane.json", "w"), indent=1)
    (out / "us_inplane.md").write_text("\n".join(md) + "\n")
    print("\n" + "\n".join(md[4:]) + f"\n-> {out / 'us_inplane.md'}")


OOP_BINS = [0, 0.5, 1, 2, 4, 8, np.inf]       # mm out of plane


def decorrelation(recs):
    """U2: the correlation left after in-plane alignment against the true out-of-plane distance
    (the speckle decorrelation curve), and how well that curve predicts the distance for a sweep
    it was not built from (leave one sweep out, ncc deciles -> median distance)."""
    r = [x for x in recs if x["ncc"] is not None]
    if not r:
        return []
    ncc, oop = np.array([x["ncc"] for x in r]), np.array([x["out_of_plane_mm"] for x in r])
    runs = np.array([x["run"] for x in r])
    rank = lambda v: np.argsort(np.argsort(v))
    rho = float(np.corrcoef(rank(ncc), rank(oop))[0, 1])
    md = ["", "## U2: speckle decorrelation against the out-of-plane distance", "",
          f"Correlation coefficient after the in-plane alignment (ECC), all gaps pooled; Spearman ρ(ncc, out-of-plane) = {rho:.2f}.", "",
          "| out-of-plane (mm) | pairs | ncc median (p10–p90) |", "|---|---|---|"]
    for lo, hi in zip(OOP_BINS[:-1], OOP_BINS[1:]):
        c = ncc[(oop >= lo) & (oop < hi)]
        rng = f"{lo:g}–{hi:g}" if np.isfinite(hi) else f"> {lo:g}"
        md.append(f"| {rng} | {len(c)} | " + (f"{np.median(c):.3f} ({np.percentile(c, 10):.3f}–{np.percentile(c, 90):.3f}) |"
                                             if len(c) else "– |"))
    err, base = [], []
    for sw in np.unique(runs):
        tr, te = runs != sw, runs == sw
        if tr.sum() < 20:
            continue
        edges = np.unique(np.percentile(ncc[tr], np.linspace(0, 100, 11)))
        b_tr, b_te = np.digitize(ncc[tr], edges[1:-1]), np.digitize(ncc[te], edges[1:-1])
        curve = {b: np.median(oop[tr][b_tr == b]) for b in np.unique(b_tr)}
        pred = np.array([curve.get(b, np.median(oop[tr])) for b in b_te])
        err += list(np.abs(pred - oop[te]))
        base += list(np.abs(np.median(oop[tr]) - oop[te]))
    if err:
        md += ["", f"Leave one sweep out, out-of-plane distance predicted from ncc: median error **{np.median(err):.2f} mm** "
               f"(p90 {np.percentile(err, 90):.2f}); predicting the median distance instead: {np.median(base):.2f} mm "
               f"(p90 {np.percentile(base, 90):.2f})."]
    return md


def pd_num(df, col):
    import pandas as pd
    return pd.to_numeric(df[col], errors="coerce").to_numpy() if col in df.columns else np.zeros(len(df))


if __name__ == "__main__":
    main()
