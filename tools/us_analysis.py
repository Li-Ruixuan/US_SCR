"""
Analyses of the US images and of the reconstruction's shape (no learning), one command each:

  inplane  U1 / U2: in-plane registration of US frame pairs (ECC) against Polaris, and speckle
           decorrelation against the out-of-plane distance
  speckle  U3: out-of-plane motion from per-patch speckle decorrelation, against Polaris and the
           camera system, and their fusion
  shape    shape of a reconstruction from poses.py exports: error after a rigid fit of each sweep,
           and the relative error between nearby frames

  python tools/us_analysis.py inplane --root $DATA/train_3XX --out runs/us-3XX
  python tools/us_analysis.py speckle --root $DATA/train_2XX --system "runs/volume3d/2XX/poses/*_scr-track.json" --out runs/us-speckle-2XX
  python tools/us_analysis.py shape --json runs/volume3d/*/poses/*.json --out runs/shape-final.md

Each command's details: python tools/us_analysis.py <command> -h, and the docstring of main_<command>.
Formerly tools/us_inplane.py, tools/us_speckle.py and tools/shape_error.py (runs before 28 Oct 2026).
"""

import argparse
import glob
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import cv2                                                               # noqa: E402
import numpy as np                                                       # noqa: E402
from tqdm import tqdm                                                    # noqa: E402

from dataloader import RPRConfig, RPRDataset, load_hand_eye, load_us_roi, test_sweeps   # noqa: E402

# ================================================================= inplane (U1, U2)

CALIB_HW = (480, 640)
ISO_MM = 0.25                       # mm per pixel of the isotropic registration grid
PX = np.array([[320, 240], [160, 120], [480, 120], [160, 400], [480, 400]], float)   # anchoring.py us_points


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


def main_inplane():
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

      python tools/us_analysis.py inplane --root $DATA/train_3XX --out runs/us-inplane-3XX
      python tools/us_analysis.py inplane --root $DATA/train_3XX --runs run-316 --out runs/us-inplane-316
    """
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


# ================================================================= speckle (U3)
TAUS = [1.0, 2.0, 3.0]          # mm: fusion thresholds reported (chosen on 2XX)


def patch_grid(mask, size):
    """Patches of size x size iso pixels with >= 80 % fan: list of (r0, c0) and centres (x, y) in mm."""
    tl, ctr = [], []
    for r0 in range(0, mask.shape[0] - size + 1, size):
        for c0 in range(0, mask.shape[1] - size + 1, size):
            if mask[r0:r0 + size, c0:c0 + size].mean() >= 0.8:
                tl.append((r0, c0))
                ctr.append(((c0 + size / 2) * ISO_MM, (r0 + size / 2) * ISO_MM))
    return tl, np.array(ctr)


def patch_ncc(a, b, tl, size):
    out = np.empty(len(tl))
    for n, (r0, c0) in enumerate(tl):
        x, y = a[r0:r0 + size, c0:c0 + size].ravel(), b[r0:r0 + size, c0:c0 + size].ravel()
        x, y = x - x.mean(), y - y.mean()
        out[n] = (x @ y) / np.sqrt((x @ x) * (y @ y) + 1e-9)
    return out


def build_curve(ncc, z, band, n_bands):
    """Per depth band: ncc decile edges -> median |z| and spread (half the p25-p75 range)."""
    cur = {}
    for b in range(n_bands):
        m = band == b
        if m.sum() < 50:
            continue
        edges = np.unique(np.percentile(ncc[m], np.linspace(0, 100, 11)))
        idx = np.digitize(ncc[m], edges[1:-1])
        med = [float(np.median(z[m][idx == q])) if (idx == q).any() else float(np.median(z[m])) for q in range(len(edges) - 1)]
        sd = [float(max(0.1, np.subtract(*np.percentile(z[m][idx == q], [75, 25])) / 2)) if (idx == q).sum() > 3 else 5.0
              for q in range(len(edges) - 1)]
        cur[b] = {"edges": edges.tolist(), "median": med, "spread": sd}
    return cur


def apply_curve(cur, ncc, band):
    d, s = np.full(len(ncc), np.nan), np.full(len(ncc), np.nan)
    for b, c in cur.items():
        m = band == int(b)
        q = np.digitize(ncc[m], np.asarray(c["edges"])[1:-1])
        d[m], s[m] = np.asarray(c["median"])[q], np.asarray(c["spread"])[q]
    return d, s


def fit_plane(xy, z, w):
    """Weighted least squares z = a + b x + c y, one reweighting pass against outlying patches."""
    A = np.column_stack([np.ones(len(z)), xy])
    for _ in range(2):
        sw = np.sqrt(w)
        coef = np.linalg.lstsq(A * sw[:, None], z * sw, rcond=None)[0]
        r = np.abs(A @ coef - z)
        w = w / np.maximum(1.0, r / (1.5 * np.median(r) + 0.1))
    return coef


def stats(e):
    e = np.asarray(e)
    return {"n": len(e), "median": float(np.median(e)), "mean": float(e.mean()),
            "p90": float(np.percentile(e, 90)), "p99": float(np.percentile(e, 99))}


def main_speckle():
    """
    U3 diagnostic: out-of-plane motion of the US plane from speckle decorrelation, per patch, against
    Polaris and against the pose system's own relative motion (diagnostic, no learning).

    U2 (us_analysis.py inplane) gave one distance per frame pair. Here the fan is cut into patches; each
    patch gives its own distance from its correlation, and a plane z = a + b x + c y fitted to them gives
    the three out-of-plane degrees of freedom (elevational shift, tilt about the lateral and about the
    axial axis). Correlation gives |z| only: the sign comes from the system (camera), or from Polaris
    ("oracle sign", an upper bound). The camera already measures nearby-frame motion well (median
    out-of-plane error 0.07 mm at 1 row, 0.3 mm at 8 rows on run-316, us_analysis.py shape), so what US
    can add is catching the system's rare large errors: the fused estimate keeps the system unless US
    disagrees by more than tau, then takes US.

    Pairs: rows i and i + k of a segment, both new US frames (us_repeat = 0), every --every-th row as a
    start. In-plane alignment: global ECC (as U1) on the blurred image; patch correlations on the raw image.
    Curve: per depth band of patches, correlation deciles -> median |z| (and spread, the patch weight).
    Without --curve, it is built here and applied leave-one-sweep-out; with --curve (e.g. built on 2XX),
    it is applied as is. The curve and the fusion threshold are chosen on 2XX and then fixed.

    Errors: out-of-plane error at the 5 US-image points of anchoring.py (mm, mean over the points), per
    pair; median / mean / p90 / p99 over pairs, per k.

      python tools/us_analysis.py speckle --root $DATA/train_2XX --system "runs/volume3d/2XX/poses/*_scr-track.json" --out runs/us-speckle-2XX
      python tools/us_analysis.py speckle --root $DATA/train_3XX --curve runs/us-speckle-2XX/curve.json \\
          --system "runs/volume3d/3XX/poses/*_scr-track.json" --out runs/us-speckle-3XX
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="collection folder with the sweeps, e.g. $DATA/train_2XX")
    ap.add_argument("--runs", nargs="+", default=None, help="sweeps (default: every run-* in --root)")
    ap.add_argument("--gaps", type=int, nargs="+", default=[1, 4, 8], help="rows between the frames of a pair")
    ap.add_argument("--every", type=int, default=5, help="every n-th row as a start")
    ap.add_argument("--patch", type=float, default=12.0, help="patch size, mm")
    ap.add_argument("--curve", default=None, help="curve.json from a calibration run (default: build here, leave one sweep out)")
    ap.add_argument("--system", default=None, help="glob of poses.py exports of the pose system (one per sweep); "
                    "without it only Polaris signs are evaluated")
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
    P5 = scaling @ np.stack([PX[:, 0], PX[:, 1], np.zeros(5), np.ones(5)])   # the 5 points, US-plane mm

    system = {}
    for p in sorted(glob.glob(args.system)) if args.system else []:
        d = json.load(open(p))
        if d["run"] in sweeps and d["run"] not in system:
            system[d["run"]] = {(f["segment"], f["row"]): np.asarray(f["T_world_us_pred"]) for f in d["frames"] if f["us"]}
    system = {sw: T for sw, T in system.items() if T}
    if args.system:
        if not system:
            raise SystemExit(f"--system: no exports of {sweeps} match {args.system}")
        if set(sweeps) - set(system):
            print(f"no system export for {sorted(set(sweeps) - set(system))}: skipped")
        sweeps = [sw for sw in sweeps if sw in system]
    size = int(round(args.patch / ISO_MM))

    recs = []                                       # one per pair: per-patch ncc, z; system z at patches and points
    for sw in sweeps:
        r = ds.runs[sw]
        df = r["df"]
        new = pd_num(df, "us_repeat") != 1
        T_world_us = r["T_world_cam"] @ np.linalg.inv(T_mc) @ rigid
        us = USFrames(Path(args.root) / sw, df, scaling)
        mask = us.fan_mask(np.concatenate([s[new[s]] for s in r["segments"]]))
        tl, ctr = patch_grid(mask, size)
        Pc = np.stack([ctr[:, 0], ctr[:, 1], np.zeros(len(ctr)), np.ones(len(ctr))])
        n_bands = 4
        band = np.minimum(n_bands - 1, (ctr[:, 1] / (mask.shape[0] * ISO_MM) * n_bands).astype(int))
        sysT = system.get(sw)
        cache = {}

        def img(row):
            if row not in cache:
                if len(cache) > 64:
                    cache.clear()
                raw = us.load(row)
                cache[row] = (raw, cv2.GaussianBlur(raw, (0, 0), 1.5))
            return cache[row]

        pairs = []
        for sid, s in enumerate(r["segments"]):
            rows = set(s.tolist())
            for i in s[::args.every]:
                for k in args.gaps:
                    j = i + k
                    if j in rows and new[i] and new[j] and (sysT is None or ((sid, i) in sysT and (sid, j) in sysT)):
                        pairs.append((sid, int(i), int(j), k))
        if sysT is not None and not pairs:
            print(f"  {sw}: no pairs inside the system export, skipped")
            continue
        for sid, i, j, k in tqdm(pairs, desc=sw, leave=False):
            (ri, bi), (rj, bj) = img(i), img(j)
            W, _ = ecc(bi, bj, mask)
            if W is None:
                continue
            rj_al = cv2.warpAffine(rj, W.astype(np.float32), rj.shape[::-1], flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
            T_ji = np.linalg.inv(T_world_us[j]) @ T_world_us[i]
            rec = {"run": sw, "seg": sid, "i": i, "j": j, "k": k, "band": band, "ctr": ctr,
                   "ncc": patch_ncc(ri, rj_al, tl, size), "z": (T_ji @ Pc)[2], "z5": (T_ji @ P5)[2]}
            if sysT is not None:
                S_ji = np.linalg.inv(sysT[(sid, j)]) @ sysT[(sid, i)]
                rec["zs"], rec["zs5"] = (S_ji @ Pc)[2], (S_ji @ P5)[2]
            recs.append(rec)
        print(f"  {sw}: {len(pairs)} pairs, {len(tl)} patches of {args.patch:g} mm", flush=True)

    if not recs:
        raise SystemExit("no pairs")
    cat = lambda key, rr: np.concatenate([x[key] for x in rr])
    curve_here = build_curve(cat("ncc", recs), np.abs(cat("z", recs)), cat("band", recs), 4)
    json.dump({"patch_mm": args.patch, "bands": 4, "root": args.root, "curve": curve_here}, open(out / "curve.json", "w"), indent=1)
    fixed = {int(b): c for b, c in json.load(open(args.curve))["curve"].items()} if args.curve else None
    if fixed is None:
        loso = {}
        for sw in {x["run"] for x in recs}:
            rr = [x for x in recs if x["run"] != sw]
            loso[sw] = build_curve(cat("ncc", rr), np.abs(cat("z", rr)), cat("band", rr), 4) if rr else curve_here

    has_sys = all("zs" in x for x in recs)
    err = {}                                         # (k, method) -> list of per-pair errors at the 5 points
    for x in recs:
        d, s = apply_curve(fixed if fixed is not None else loso[x["run"]], x["ncc"], x["band"])
        ok = np.isfinite(d)
        if ok.sum() < 4:
            continue
        A5 = np.column_stack([np.ones(5), P5[:2].T])
        add = lambda m, z5: err.setdefault((x["k"], m), []).append(float(np.abs(z5 - x["z5"]).mean()))
        oracle = A5 @ fit_plane(x["ctr"][ok], (np.sign(x["z"]) * d)[ok], 1 / s[ok] ** 2)
        add("US, Polaris sign (upper bound)", oracle)
        if has_sys:
            zu = A5 @ fit_plane(x["ctr"][ok], (np.where(x["zs"] >= 0, 1, -1) * d)[ok], 1 / s[ok] ** 2)
            add("system", x["zs5"])
            add("US, system sign", zu)
            for tau in TAUS:
                add(f"fused, tau {tau:g} mm", zu if np.abs(zu - x["zs5"]).mean() > tau else x["zs5"])

    f = lambda v: f"{v:.2f}"
    src = (f"curve from {json.load(open(args.curve))['root']}" if args.curve else "curve built here, leave one sweep out"
           if len({x["run"] for x in recs}) > 1 else "curve built on this sweep (in-sample, optimistic)")
    md = [f"# U3: out-of-plane motion from per-patch speckle decorrelation ({Path(args.root).name})", "",
          f"{len(recs)} pairs, patches {args.patch:g} mm, {src}. Out-of-plane error at the 5 US-image points (mm), "
          "over pairs. True motion in the header. 'fused': the system unless US differs by more than tau (mean over "
          "the points), then US.", "",
          "| k (rows) | method | pairs | median | mean | p90 | p99 |", "|---|---|---|---|---|---|---|"]
    for k in args.gaps:
        true = [float(np.abs(x["z5"]).mean()) for x in recs if x["k"] == k]
        if not true:
            continue
        md.append(f"| **{k}** (true {np.median(true):.1f} mm) | | | | | | |")
        for (kk, m), e in err.items():
            if kk == k:
                s = stats(e)
                md.append(f"| | {m} | {s['n']} | {f(s['median'])} | {f(s['mean'])} | {f(s['p90'])} | {f(s['p99'])} |")
    if not has_sys:
        md += ["", "No --system: only the Polaris-sign upper bound is shown."]
    (out / "us_speckle.md").write_text("\n".join(md) + "\n")
    json.dump({"args": vars(args), "errors": {f"{k}|{m}": stats(e) for (k, m), e in err.items()}},
              open(out / "us_speckle.json", "w"), indent=1)
    print("\n" + "\n".join(md[4:]) + f"\n-> {out / 'us_speckle.md'}")


# ================================================================= shape
def kabsch(P, Q):
    """Rigid (R, t) minimising |R P + t - Q| for (N, 3) point sets."""
    mp, mq = P.mean(0), Q.mean(0)
    U, _, Vt = np.linalg.svd((P - mp).T @ (Q - mq))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    return R, mq - R @ mp


def sweep_metrics(doc, gaps):
    S = np.asarray(doc["S_us_px_to_mm"])
    P = S @ np.stack([PX[:, 0], PX[:, 1], np.zeros(5), np.ones(5)])           # (4, 5) US-plane mm
    fr = [f for f in doc["frames"] if f["us"] and np.all(np.isfinite(f["T_world_us_pred"]))
          and np.all(np.isfinite(f["T_world_us_gt"]))]
    if len(fr) < 2:
        return None
    Tp = np.array([f["T_world_us_pred"] for f in fr], float)
    Tg = np.array([f["T_world_us_gt"] for f in fr], float)
    Xp, Xg = (Tp @ P)[:, :3].transpose(0, 2, 1), (Tg @ P)[:, :3].transpose(0, 2, 1)   # (N, 5, 3)
    m = {"absolute": float(np.median(np.linalg.norm(Xp - Xg, axis=2).mean(1)))}
    R, t = kabsch(Xp.reshape(-1, 3), Xg.reshape(-1, 3))
    m["shape"] = float(np.median(np.linalg.norm(Xp @ R.T + t - Xg, axis=2).mean(1)))
    idx = {(f["segment"], f["row"]): n for n, f in enumerate(fr)}
    for k in gaps:
        pairs = [(n, idx[(s, r + k)]) for (s, r), n in idx.items() if (s, r + k) in idx]
        if not pairs:
            continue
        i, j = np.array(pairs).T
        rel = lambda T: np.linalg.inv(T[j]) @ T[i]                              # frame i in frame j
        E = (rel(Tp) @ P - rel(Tg) @ P)[:, :3]                                  # (M, 3, 5), mm in frame j
        m[f"in_{k}"] = float(np.median(np.linalg.norm(E[:, :2], axis=1).mean(1)))
        m[f"out_{k}"] = float(np.median(np.abs(E[:, 2]).mean(1)))
        m[f"true_out_{k}"] = float(np.median(np.abs((rel(Tg) @ P)[:, 2]).mean(1)))
    return m


def short(source):
    if "-scr-" in source or source.startswith("anchored-pgo-scr"):
        return "SCR anchors + odometry"
    if "pgo-classical" in source:
        return "classical anchors + odometry"
    if source.startswith("classical-vo"):
        return "classical odometry only"
    return source


def main_shape():
    """
    Shape of the reconstruction: how much of the error at the US image a rigid motion explains, and
    how well each pose source gets the motion between nearby US frames (what US images could correct).

    Input: poses.py exports (<out>/poses/fold*_<run>_<source>.json, e.g. written by tools/volume_pages.py).
    Points: the 5 points of anchoring.py spanning the US image. Per sweep and source:
      absolute  mean point error against Polaris, median over frames (as anchoring.py's US-image error)
      shape     the same after the best rigid fit of the whole sweep (all frames, all points) to Polaris:
                the error a rigid offset of the room frame cannot explain; this is what distorts the volume
      relative  for frame pairs k rows apart (same segment), the error of the relative pose at the points,
                in the US frame of the later image: in-plane (what US registration would see) and
                out-of-plane (along the plane normal; what speckle decorrelation measures)
    Numbers are means over sweeps of the per-sweep medians. Rows are grouped by split (the folder that
    holds poses/) and source.

      python tools/us_analysis.py shape --json runs/volume3d/*/poses/*.json --out runs/shape-final.md
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", nargs="+", required=True, help="poses.py exports")
    ap.add_argument("--gaps", type=int, nargs="+", default=[1, 8, 30], help="rows between the frames of a pair "
                    "(8 = one odometry step, 30 = 1 s)")
    ap.add_argument("--out", required=True, help="markdown file (a .json with every sweep is written next to it)")
    args = ap.parse_args()

    res = defaultdict(dict)                                 # (split, source) -> {run: metrics}
    for p in sorted(args.json):
        d = json.load(open(p))
        split = Path(p).resolve().parent.parent.name
        if d["run"] in res[(split, d["source"])]:
            continue                                        # the same sweep from another fold
        try:
            m = sweep_metrics(d, args.gaps)
        except Exception as e:                              # report and go on with the other files
            m = None
            print(f"{p}: {type(e).__name__}: {e}")
        if m is None:
            print(f"{split} {d['run']} {short(d['source'])}: skipped (no valid frames)")
            continue
        res[(split, d["source"])][d["run"]] = m
        print(f"{split} {d['run']} {short(d['source'])}: " + ", ".join(
            f"{k} {v:.2f}" for k, v in res[(split, d['source'])][d['run']].items()), flush=True)

    mean = lambda runs, k: np.mean([m[k] for m in runs.values() if k in m]) if any(k in m for m in runs.values()) else np.nan
    md = ["# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames", "",
          "Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit "
          "of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / "
          "**out-of-plane**, true out-of-plane motion in brackets.", "",
          "| split | source | sweeps | absolute | **shape** | " + " | ".join(f"k = {k}: in / **out** (true)" for k in args.gaps) + " |",
          "|---|---|---|---|---|" + "---|" * len(args.gaps)]
    for (split, src), runs in sorted(((k, r) for k, r in res.items() if r), key=lambda x: (x[0][0], short(x[0][1]))):
        md.append(f"| {split} | {short(src)} | {len(runs)} | {mean(runs, 'absolute'):.2f} | **{mean(runs, 'shape'):.2f}** | "
                  + " | ".join(f"{mean(runs, f'in_{k}'):.2f} / **{mean(runs, f'out_{k}'):.2f}** ({mean(runs, f'true_out_{k}'):.1f})"
                               for k in args.gaps) + " |")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md) + "\n")
    json.dump({"args": vars(args), "sweeps": {f"{s}|{src}": r for (s, src), r in res.items()}},
              open(out.with_suffix(".json"), "w"), indent=1)
    print("\n" + "\n".join(md[4:]) + f"\n-> {out}")

# ================================================================= command line
COMMANDS = {"inplane": main_inplane, "speckle": main_speckle, "shape": main_shape}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        raise SystemExit(__doc__)
    cmd = sys.argv.pop(1)
    sys.argv[0] = f"{sys.argv[0]} {cmd}"
    COMMANDS[cmd]()


if __name__ == "__main__":
    main()
