"""
Classical anchor baseline on the (keyframe, frame) pairs of an `anchoring.py evaluate` result,
next to the anchor network on the same pairs, plus a depth check of each predicted pose.

Classical: SIFT on both RGB images (full resolution), ratio-test matches, keyframe keypoints
lifted to 3D with the keyframe's depth, frame pose from PnP + RANSAC (reprojection error
--ransac-px), refined on the inliers. RANSAC drops what does not fit one rigid motion, e.g.
objects that moved since the room scan; the anchor network has no such outlier rejection
(note §6.4). A pair fails with fewer than --min-inliers inliers.

Depth check (no learning): the frame's depth is moved into the keyframe with the PREDICTED pose
and compared with the keyframe's depth (as in anchor_saliency.py); "depth agreement" = share
of the pixels seen in both whose depth agrees. A wrong pose gives low agreement; if it
separates good from bad network anchors, it can serve as a reject rule.

Errors are translation (mm) and rotation (deg) of the keyframe -> frame pose against the
Polaris truth, for the network (xi_pred of the result file) and the classical estimate.

  python tools/anchor_classical.py --eval runs/anchoring-final/anchor_eval_anchor-rgbd-e20-odometry-train_3XX.json \\
      --out runs/classical/3XX_2XXmap
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "baselines"))
from anchor_saliency import CHANGED, SAME, change_labels, spearman   # noqa: E402
from anchoring import load_depth                                      # noqa: E402
from dataloader import RPRConfig, RPRDataset                          # noqa: E402
from eval import load_val_set                                         # noqa: E402
from geometry import invert_se3, se3_exp                              # noqa: E402
from trajectory import gt_chains                                      # noqa: E402


def pose_error(T, T_gt):
    """Translation (mm) and rotation (deg) difference of two 4x4 poses."""
    dR = T[:3, :3].T @ T_gt[:3, :3]
    ang = np.degrees(np.arccos(np.clip((np.trace(dR) - 1) / 2, -1, 1)))
    return float(np.linalg.norm(T[:3, 3] - T_gt[:3, 3])), float(ang)


def sift_features(gray, depth, sift):
    """(keypoints (N, 2) px, descriptors (N, 128), depth at the keypoints (N,) mm or None)."""
    kp, desc = sift.detectAndCompute(gray, None)
    if desc is None:
        return np.zeros((0, 2)), np.zeros((0, 128), np.float32), None
    pts = np.array([k.pt for k in kp], np.float64).reshape(-1, 2)
    z = None
    if depth is not None:
        u, v = np.round(pts[:, 0]).astype(int), np.round(pts[:, 1]).astype(int)
        z = depth[np.clip(v, 0, depth.shape[0] - 1), np.clip(u, 0, depth.shape[1] - 1)].astype(np.float64)
    return pts, desc, z


def pnp_pose(fa, fb, K, ratio, ransac_px, min_inliers, dmin, dmax):
    """Pose T_a_b (frame b's camera in frame a's coordinates) from SIFT features fa (with depth)
    and fb: ratio-test matches, a's keypoints lifted to 3D, PnP-RANSAC, refined on the inliers.
    Returns (T or None, matches, inliers)."""
    pa, da, za = fa
    pb, db, _ = fb
    if len(pa) < 8 or len(pb) < 8:
        return None, 0, 0
    m = cv2.BFMatcher(cv2.NORM_L2).knnMatch(da, db, k=2)
    good = [a for a, b in (p for p in m if len(p) == 2) if a.distance < ratio * b.distance]
    ia = np.array([g.queryIdx for g in good], int)
    ib = np.array([g.trainIdx for g in good], int)
    if len(ia) < min_inliers:
        return None, len(ia), 0
    z = za[ia]
    ok = (z > dmin) & (z < dmax)
    if ok.sum() < min_inliers:
        return None, len(ia), 0
    p = pa[ia[ok]]
    X = np.stack([(p[:, 0] - K[0, 2]) / K[0, 0] * z[ok], (p[:, 1] - K[1, 2]) / K[1, 1] * z[ok], z[ok]], 1)
    q = pb[ib[ok]]
    found, rvec, tvec, inl = cv2.solvePnPRansac(X, q, K, None, iterationsCount=2000,
                                                reprojectionError=ransac_px, confidence=0.999,
                                                flags=cv2.SOLVEPNP_EPNP)
    if not found or inl is None or len(inl) < min_inliers:
        return None, len(ia), 0 if inl is None else len(inl)
    inl = inl.ravel()
    rvec, tvec = cv2.solvePnPRefineLM(X[inl], q[inl], K, None, rvec, tvec)
    T_b_a = np.eye(4)
    T_b_a[:3, :3], T_b_a[:3, 3] = cv2.Rodrigues(rvec)[0], tvec.ravel()   # a's coordinates -> b's
    return invert_se3(T_b_a[None])[0], len(ia), len(inl)


def classical_pose(gk, dk, gq, K, sift, ratio, ransac_px, min_inliers, dmin, dmax):
    """Keyframe -> frame pose T_k_q (4x4, frame camera in keyframe coordinates) from SIFT +
    PnP-RANSAC, or None. Also returns the number of matches and inliers."""
    return pnp_pose(sift_features(gk, dk, sift), sift_features(gq, None, sift), K, ratio, ransac_px,
                    min_inliers, dmin, dmax)


def depth_agreement(dq, dk, T_k_q, K, dmin, dmax, tol_mm, tol_rel):
    """Share of the pixels seen in both whose depth agrees, with the frame placed at T_k_q."""
    lab = change_labels(dq, T_k_q, dk, np.eye(4), K, dmin, dmax, tol_mm, tol_rel)
    seen = (lab == SAME) | (lab == CHANGED)
    return float((lab == SAME).sum() / max(seen.sum(), 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", required=True, help="anchor_eval_*.json of anchoring.py evaluate")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-anchors", type=int, default=150, help="anchors used, spread over all (0: all)")
    ap.add_argument("--pairs-per-anchor", type=int, default=3)
    ap.add_argument("--features", type=int, default=4000)
    ap.add_argument("--ratio", type=float, default=0.8)
    ap.add_argument("--ransac-px", type=float, default=4.0, help="at full resolution (1280x720)")
    ap.add_argument("--min-inliers", type=int, default=20)
    ap.add_argument("--check-scale", type=int, default=4, help="depth check on a grid this many times coarser")
    ap.add_argument("--tol-mm", type=float, default=30.0)
    ap.add_argument("--tol-rel", type=float, default=0.03)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    E = json.load(open(args.eval))
    ea = E["args"]
    map_root, map_scans = ea["map_root"] or ea["root"], ea["map_scans"] or ea["scan_runs"]
    test_root = ea["test_root"] or ea["root"]
    ack = torch.load(ea["ckpts"][0], map_location="cpu", weights_only=False)
    ock = torch.load(Path(ea["odometry"]) / f"fold{ack['args']['fold']}" / "best.pt", map_location="cpu", weights_only=False)
    ds_val, T_mc, val_runs = load_val_set(ock, ea["test_root"], ea["test_runs"])
    chains = gt_chains(ds_val)
    cfg = RPRConfig(T_marker_cam=T_mc)
    base_map = RPRDataset(map_root, map_scans, map_scans, cfg)
    base = RPRDataset(test_root, val_runs, [], cfg)
    sift = cv2.SIFT_create(nfeatures=args.features)
    dmin, dmax = cfg.min_depth, cfg.max_depth

    def frame(ds, root, name, row):
        g = cv2.imread(str(Path(root) / name / ds.runs[name]["df"]["rgb"].iloc[row]), cv2.IMREAD_GRAYSCALE)
        return g, load_depth(name, row, ds.runs, root), np.array(ds.runs[name]["K"], float)

    def coarse(d, K):
        s = args.check_scale
        Kc = K.copy()
        Kc[:2] /= s
        return cv2.resize(d, (d.shape[1] // s, d.shape[0] // s), interpolation=cv2.INTER_NEAREST), Kc

    rows = E["anchors"]
    if args.max_anchors and len(rows) > args.max_anchors:
        rows = [rows[i] for i in np.linspace(0, len(rows) - 1, args.max_anchors).round().astype(int)]
    print(f"{len(rows)} anchors x up to {args.pairs_per_anchor} keyframes | map {map_root}: {'+'.join(map_scans)} | sweeps {test_root}")

    res = []
    for n_a, r in enumerate(rows):
        c = chains[(r["run"], r["segment"])]
        row_q = int(c["frames"][r["index"]])
        gq, dq, K = frame(base, test_root, r["run"], row_q)
        dqc, Kc = coarse(dq, K)
        for j, kf in enumerate(r["keyframes"][: args.pairs_per_anchor]):
            kn, kr = kf.rsplit(":", 1)
            gk, dk, _ = frame(base_map, map_root, kn, int(kr))
            dkc, _ = coarse(dk, K)
            T_gt = se3_exp(np.asarray(r["xi_gt"][j])[None])[0]
            T_net = se3_exp(np.asarray(r["xi_pred"][j])[None])[0]
            T_cl, n_match, n_inl = classical_pose(gk, dk, gq, K, sift, args.ratio, args.ransac_px, args.min_inliers, dmin, dmax)
            e_net = pose_error(T_net, T_gt)
            e_cl = pose_error(T_cl, T_gt) if T_cl is not None else (None, None)
            agree = lambda T: depth_agreement(dqc, dkc, T, Kc, dmin, dmax, args.tol_mm, args.tol_rel)
            res.append({"run": r["run"], "frame": row_q, "keyframe": kf,
                        "key_dist_mm": float(np.linalg.norm(T_gt[:3, 3])),
                        "net_err_mm": e_net[0], "net_err_deg": e_net[1],
                        "classical_ok": T_cl is not None, "matches": n_match, "inliers": n_inl,
                        "classical_err_mm": e_cl[0], "classical_err_deg": e_cl[1],
                        "agree_true": agree(T_gt), "agree_net": agree(T_net),
                        "agree_classical": agree(T_cl) if T_cl is not None else None})
        if (n_a + 1) % 25 == 0:
            print(f"  {n_a + 1}/{len(rows)} anchors", flush=True)

    g = lambda k, sel=None: np.array([x[k] for x in res if sel is None or sel(x)], float)
    ok = lambda x: x["classical_ok"]
    net, agree_net, agree_true = g("net_err_mm"), g("agree_net"), g("agree_true")
    hybrid = np.array([x["classical_err_mm"] if x["classical_ok"] else x["net_err_mm"] for x in res])
    good, bad = net < 15, net > 40
    S = {"pairs": len(res), "classical_success_pct": 100 * float(np.mean([ok(x) for x in res])),
         "net_err_median": float(np.median(net)), "net_err_deg_median": float(np.median(g("net_err_deg"))),
         "classical_err_median_where_ok": float(np.median(g("classical_err_mm", ok))) if any(map(ok, res)) else None,
         "classical_err_deg_median_where_ok": float(np.median(g("classical_err_deg", ok))) if any(map(ok, res)) else None,
         "net_err_median_same_pairs": float(np.median(g("net_err_mm", ok))) if any(map(ok, res)) else None,
         "hybrid_err_median": float(np.median(hybrid)),
         "agree_true_median": float(np.median(agree_true)),
         "agree_net_median_good": float(np.median(agree_net[good])) if good.any() else None,
         "agree_net_median_bad": float(np.median(agree_net[bad])) if bad.any() else None,
         "spearman_net_err_vs_agree_net": spearman(net, -agree_net),
         "spearman_net_err_vs_agree_drop": spearman(net, agree_true - agree_net)}
    json.dump({"eval": args.eval, "settings": vars(args), "summary": S, "pairs": res}, open(out / "classical.json", "w"), indent=1)
    f = lambda v, d=1: "–" if v is None else f"{v:.{d}f}"
    md = [f"# Classical anchors (SIFT + PnP-RANSAC with depth) vs the anchor network: {Path(args.eval).name}", "",
          f"{len(res)} (keyframe, frame) pairs from {len(rows)} anchors; map {map_root} ({'+'.join(map_scans)}), sweeps {test_root}. "
          f"Errors of the keyframe -> frame pose against the Polaris truth.", "",
          "| measure | value |", "|---|---|",
          f"| anchor network: translation / rotation error, median | {f(S['net_err_median'])} mm / {f(S['net_err_deg_median'], 2)} deg |",
          f"| classical: pairs solved (>= {args.min_inliers} RANSAC inliers) | {f(S['classical_success_pct'], 0)} % |",
          f"| classical vs network on the solved pairs, translation median | {f(S['classical_err_median_where_ok'])} vs {f(S['net_err_median_same_pairs'])} mm |",
          f"| classical, rotation median (solved pairs) | {f(S['classical_err_deg_median_where_ok'], 2)} deg |",
          f"| hybrid (classical where solved, else network), translation median | {f(S['hybrid_err_median'])} mm |",
          f"| depth agreement at the true pose, median (how much of the scene still matches) | {f(100 * S['agree_true_median'], 0)} % |",
          f"| depth agreement at the network pose: good (< 15 mm) / bad (> 40 mm) pairs, median | {f(None if S['agree_net_median_good'] is None else 100 * S['agree_net_median_good'], 0)} % / "
          f"{f(None if S['agree_net_median_bad'] is None else 100 * S['agree_net_median_bad'], 0)} % |",
          f"| rank correlation: network error vs low agreement / vs agreement drop from the true pose | "
          f"{f(S['spearman_net_err_vs_agree_net'], 2)} / {f(S['spearman_net_err_vs_agree_drop'], 2)} |"]
    (out / "classical.md").write_text("\n".join(md) + "\n")
    print("\n" + "\n".join(md[4:]) + f"\n-> {out / 'classical.md'}")


if __name__ == "__main__":
    main()
