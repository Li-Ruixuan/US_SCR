"""
U3 diagnostic: out-of-plane motion of the US plane from speckle decorrelation, per patch, against
Polaris and against the pose system's own relative motion (diagnostic, no learning).

U2 (tools/us_inplane.py) gave one distance per frame pair. Here the fan is cut into patches; each
patch gives its own distance from its correlation, and a plane z = a + b x + c y fitted to them gives
the three out-of-plane degrees of freedom (elevational shift, tilt about the lateral and about the
axial axis). Correlation gives |z| only: the sign comes from the system (camera), or from Polaris
("oracle sign", an upper bound). The camera already measures nearby-frame motion well (median
out-of-plane error 0.07 mm at 1 row, 0.3 mm at 8 rows on run-316, tools/shape_error.py), so what US
can add is catching the system's rare large errors: the fused estimate keeps the system unless US
disagrees by more than tau, then takes US.

Pairs: rows i and i + k of a segment, both new US frames (us_repeat = 0), every --every-th row as a
start. In-plane alignment: global ECC (as U1) on the blurred image; patch correlations on the raw image.
Curve: per depth band of patches, correlation deciles -> median |z| (and spread, the patch weight).
Without --curve, it is built here and applied leave-one-sweep-out; with --curve (e.g. built on 2XX),
it is applied as is. The curve and the fusion threshold are chosen on 2XX and then fixed.

Errors: out-of-plane error at the 5 US-image points of anchoring.py (mm, mean over the points), per
pair; median / mean / p90 / p99 over pairs, per k.

  python tools/us_speckle.py --root $DATA/train_2XX --system "runs/volume3d-final/2XX/poses/*anchored-pgo-scr-*.json" --out runs/us-speckle-2XX
  python tools/us_speckle.py --root $DATA/train_3XX --curve runs/us-speckle-2XX/curve.json \\
      --system "runs/volume3d-final/3XX/poses/*anchored-pgo-scr-*.json" --out runs/us-speckle-3XX
"""

import argparse
import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

import cv2                                                               # noqa: E402
import numpy as np                                                       # noqa: E402
from tqdm import tqdm                                                    # noqa: E402

from dataloader import RPRConfig, RPRDataset, load_hand_eye, test_sweeps  # noqa: E402
from shape_error import PX                                               # noqa: E402
from us_inplane import ISO_MM, USFrames, ecc, pd_num, read_calib        # noqa: E402

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


def main():
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
    if args.system and not system:
        raise SystemExit(f"--system: no exports of {sweeps} match {args.system}")
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


if __name__ == "__main__":
    main()
