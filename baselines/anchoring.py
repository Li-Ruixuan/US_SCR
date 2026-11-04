"""
Anchoring against the room scan (note_RPR.md §2): network, classical and SCR anchors.

  Data: every subcommand takes --root and --scan-runs, e.g.
  python anchoring.py coverage --root data/train_2XX --scan-runs room-201 room-202

  # feasibility (CPU)
  python anchoring.py coverage                          # distance to the best room-scan keyframe
  python anchoring.py simulate --runs runs/rpr-rgb-gap4 # odometry + simulated anchors
  # learned anchors: the same RPRNet on (room-scan keyframe, frame) pairs, trained in rgbd-us
  python anchoring.py pairs                             # CPU, once: runs/anchor-pairs/pairs_v2.json
  python anchoring.py evaluate --ckpts runs/anchor-rgbd-v2-reg/fold*/best.pt   # GPU: odometry + anchors
  # fixed split: train --val-runs ...; test sweeps from another folder, with their own map or another one:
  python anchoring.py evaluate --root data/train_2XX --scan-runs room-201 room-202 ... \
      --test-root data/train_3XX --map-root data/train_3XX --map-scans room-301 room-302

The anchor network is RPRNet on a 2-frame input [keyframe, current frame] -> xi of
T_key_cur, with an extra coarse correlation (model.py, coarse_radius) for the larger image
motion. Pairs are chosen by GT pose and co-visibility; the held-out sweep of a fold is
never a training query, and its pairs are the validation set ("anchor error with oracle
retrieval"). evaluate retrieves keyframes from the odometry pose estimate (no GT), and
writes the anchored trajectories as prediction caches that poses.py can export and plot.

coverage (oracle retrieval). The map is every --keyframe-every-th usable room-scan frame.
For every --query-every-th usable sweep frame, the --candidates nearest keyframes by pose
(distance + --mm-per-deg x angle) are scored by co-visibility: the fraction of the
query's valid depth points that project inside the keyframe image with consistent depth.
The best one is the anchor keyframe. Reported per sweep: its baseline (mm), rotation
(deg), co-visibility, and the share of frames with an anchor above 0.3 / 0.5 co-visibility.
For scale: the odometry network sees steps of about 1.3 mm and 0.4 deg (gap 4).

simulate. Per held-out sweep, the arm's cached predictions are chained as in eval.py,
except that every --intervals seconds (and at each segment start) the pose is replaced by
an anchor = GT pose perturbed by a random error of RMS --sigmas (mm, deg; camera frame).
  causal   chain from the latest anchor (live navigation)
  offline  also spread the discrepancy found at the next anchor back over the frames
           since the previous one (linear in time on SE(3); reconstruction)
Errors at the camera centre and at the US image (mean over 5 points spanning the image),
median over all frames of all sweeps, mean over --repeats noise draws. 'inf' = only the
segment start is anchored (as unanchored eval, but with a noisy start).
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # dataloader.py, geometry.py at the repo root
from dataloader import RPRConfig, RPRDataset, leave_one_sweep_out, load_hand_eye
from eval import load_val_set, read_calib_parts
from geometry import invert_se3, se3_exp, se3_log
from model import RPRNet
from trajectory import gt_chains, model_inputs

ROOT, SCANS = "data/train", []          # set from --root / --scan-runs in main()
HAND_EYE = str(Path(__file__).resolve().parents[1] / "T_marker_cam.npy")


# --- coverage ---

def rot_angle_deg(Ra, Rb):
    """Angle (deg) between rotations, broadcast over leading axes."""
    tr = np.einsum("...ij,...ij->...", Ra, Rb)            # trace(Ra^T Rb)
    return np.degrees(np.arccos(np.clip((tr - 1) / 2, -1, 1)))


def load_depth(run, row, ds_runs, root):
    r = ds_runs[run]
    d = cv2.imread(str(Path(root) / run / r["df"]["depth"].iloc[row]), cv2.IMREAD_UNCHANGED)
    return d.astype(np.float32) * r["depth_scale"]                         # mm


def covisibility(dq, T_q, K, depths_k, T_k, stride, dmin, dmax, tol):
    """Share of the query's valid depth points (stride grid) that land inside each
    keyframe image with depth within tol (relative) of the keyframe's own depth."""
    H, W = dq.shape
    v, u = np.mgrid[0:H:stride, 0:W:stride]
    z = dq[v, u]
    ok = (z > dmin) & (z < dmax)
    u, v, z = u[ok], v[ok], z[ok]
    if len(z) == 0:
        return np.zeros(len(T_k))
    X = np.stack([(u - K[0, 2]) / K[0, 0] * z, (v - K[1, 2]) / K[1, 1] * z, z, np.ones_like(z)])
    out = []
    for dk, Tk in zip(depths_k, T_k):
        Y = (invert_se3(Tk) @ T_q @ X)[:3]
        front = Y[2] > dmin
        uk = np.round(K[0, 0] * Y[0] / np.maximum(Y[2], 1) + K[0, 2]).astype(int)
        vk = np.round(K[1, 1] * Y[1] / np.maximum(Y[2], 1) + K[1, 2]).astype(int)
        inside = front & (uk >= 0) & (uk < W) & (vk >= 0) & (vk < H)
        zk = np.zeros_like(Y[2])
        zk[inside] = dk[vk[inside], uk[inside]]
        good = inside & (zk > dmin) & (np.abs(zk - Y[2]) < tol * Y[2])
        out.append(good.mean())
    return np.array(out)


def coverage(args):
    T_mc = load_hand_eye(HAND_EYE, "mm")
    cfg = RPRConfig(T_marker_cam=T_mc)
    runs = sorted({r for tr, va in leave_one_sweep_out(ROOT, SCANS) for r in tr + va})
    ds = RPRDataset(ROOT, runs, SCANS, cfg)
    usable = {n: np.concatenate(r["segments"]) for n, r in ds.runs.items()}

    key = [(n, row) for n in SCANS for row in usable[n][:: args.keyframe_every]]
    T_key = np.stack([ds.runs[n]["T_world_cam"][row] for n, row in key])
    print(f"map: {len(key)} keyframes from {', '.join(SCANS)}")
    K = ds.runs[SCANS[0]]["K"]
    depth_cache = {}

    def key_depth(i):
        if i not in depth_cache:
            depth_cache[i] = load_depth(*key[i], ds.runs, ROOT)
        return depth_cache[i]

    rows_out = {}
    for sweep in [r for r in runs if r not in SCANS]:
        res = []
        for row in usable[sweep][:: args.query_every]:
            T_q = ds.runs[sweep]["T_world_cam"][row]
            dist = np.linalg.norm(T_key[:, :3, 3] - T_q[:3, 3], axis=1)
            ang = rot_angle_deg(T_key[:, :3, :3], T_q[:3, :3][None])
            cand = np.argsort(dist + args.mm_per_deg * ang)[: args.candidates]
            cov = covisibility(load_depth(sweep, row, ds.runs, ROOT), T_q, K,
                               [key_depth(i) for i in cand], T_key[cand], args.stride,
                               cfg.min_depth, cfg.max_depth, args.depth_tol)
            b = cand[np.argmax(cov)]
            rel = invert_se3(T_key[b]) @ T_q                   # query in keyframe camera
            res.append({"row": int(row), "key": f"{key[b][0]}:{key[b][1]}",
                        "baseline_mm": float(dist[b]), "angle_deg": float(ang[b]),
                        "forward_mm": float(rel[2, 3]), "covis": float(cov.max()),
                        "nearest_mm": float(dist.min())})
        rows_out[sweep] = res
        c = np.array([x["covis"] for x in res])
        print(f"  {sweep}: {len(res)} queries | baseline median "
              f"{np.median([x['baseline_mm'] for x in res]):.0f} mm, angle "
              f"{np.median([x['angle_deg'] for x in res]):.1f} deg, covis median {np.median(c):.2f}, "
              f">=0.5: {100 * (c >= 0.5).mean():.0f}%")

    summ = {}
    for sw, res in rows_out.items():
        f = lambda k: np.array([x[k] for x in res])
        summ[sw] = {"queries": len(res),
                    **{f"{k}_median": float(np.median(f(k))) for k in
                       ("baseline_mm", "angle_deg", "covis", "nearest_mm")},
                    "baseline_mm_p90": float(np.percentile(f("baseline_mm"), 90)),
                    "angle_deg_p90": float(np.percentile(f("angle_deg"), 90)),
                    "abs_forward_mm_median": float(np.median(np.abs(f("forward_mm")))),
                    "covis_ge_0.3_pct": float(100 * (f("covis") >= 0.3).mean()),
                    "covis_ge_0.5_pct": float(100 * (f("covis") >= 0.5).mean())}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    json.dump({"args": vars(args), "keyframes": len(key), "summary": summ, "per_query": rows_out},
              open(out / "coverage.json", "w"), indent=1)
    md = ["# Anchoring coverage (oracle retrieval by GT pose + co-visibility)", "",
          f"Map: {len(key)} room-scan keyframes (every {args.keyframe_every}th usable frame of "
          f"{', '.join(SCANS)}). Queries: every {args.query_every}th usable sweep frame. "
          "Baseline/angle: query vs its best keyframe. Forward: |translation along the "
          "keyframe's viewing axis|. Odometry steps for comparison: ~1.3 mm, ~0.4 deg.", "",
          "| Sweep | queries | baseline (mm) median / p90 | angle (deg) median / p90 | "
          "forward (mm) | nearest by position (mm) | co-vis median | co-vis ≥ 0.3 | co-vis ≥ 0.5 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for sw, s in summ.items():
        md.append(f"| {sw} | {s['queries']} | {s['baseline_mm_median']:.0f} / {s['baseline_mm_p90']:.0f} | "
                  f"{s['angle_deg_median']:.1f} / {s['angle_deg_p90']:.1f} | "
                  f"{s['abs_forward_mm_median']:.0f} | {s['nearest_mm_median']:.0f} | "
                  f"{s['covis_median']:.2f} | {s['covis_ge_0.3_pct']:.0f} % | {s['covis_ge_0.5_pct']:.0f} % |")
    (out / "coverage.md").write_text("\n".join(md) + "\n")
    plot_coverage(rows_out, out / "coverage.png")
    print(f"wrote {out / 'coverage.md'}, coverage.json, coverage.png")


def plot_coverage(rows_out, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(14, 4))
    for sw, res in rows_out.items():
        for a, k in zip(ax, ("baseline_mm", "angle_deg", "covis")):
            x = np.sort([r[k] for r in res])
            a.plot(x, np.linspace(0, 1, len(x)), lw=1.2, label=sw)
    for a, lab in zip(ax, ("baseline to anchor keyframe (mm)", "rotation to anchor keyframe (deg)",
                           "co-visibility")):
        a.set_xlabel(lab)
        a.set_ylabel("share of sweep frames")
        a.grid(alpha=0.3)
    ax[0].legend(fontsize=7)
    fig.suptitle("Anchoring coverage, oracle retrieval (cumulative over sweep frames)")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


# --- simulate ---

def us_points(T_cam_us, S):
    """5 points spanning the US image (1-based pixels on 640x480) in the camera frame."""
    px = np.array([[320, 240], [160, 120], [480, 120], [160, 400], [480, 400]], float)
    P = np.stack([px[:, 0], px[:, 1], np.zeros(5), np.ones(5)])
    return T_cam_us @ S @ P                                            # (4, 5)


def anchor_pose(T_gt, sig_t, sig_r, rng):
    """GT pose perturbed in the camera frame; per-axis std = sigma / sqrt(3), so the
    RMS translation error is sig_t (mm) and the RMS rotation error sig_r (deg)."""
    xi = np.concatenate([rng.normal(0, sig_t / np.sqrt(3), 3),
                         np.radians(rng.normal(0, sig_r / np.sqrt(3), 3))])
    return T_gt @ se3_exp(xi[None])[0]


def anchor_times(el, interval):
    """Chain indices where an anchor is due: 0, then each time el crosses a multiple of interval."""
    if not np.isfinite(interval):
        return [0]
    return [0] + [int(i) for i in np.flatnonzero(np.diff(np.floor(el / interval)) > 0) + 1]


def apply_anchors(xi, el, anchors, offline):
    """Chain odometry steps xi (N-1, 6), restarting at every anchor {index: (4, 4)};
    anchors must contain 0. offline: also spread the discrepancy found at each anchor
    back over the frames since the previous one (linear in time on SE(3))."""
    N = len(xi) + 1
    steps = se3_exp(xi)
    T = np.empty((N, 4, 4))
    for i in range(N):
        T[i] = anchors[i] if i in anchors else T[i - 1] @ steps[i - 1]
    if offline:
        idx = sorted(anchors)
        for a, b in zip(idx[:-1], idx[1:]):
            T_b = T[b - 1] @ steps[b - 1]                        # chain value reached at b
            C = se3_log((anchors[b] @ invert_se3(T_b))[None])[0]  # world-frame correction
            s = (el[a:b] - el[a]) / max(el[b] - el[a], 1e-9)
            T[a:b] = se3_exp(s[:, None] * C[None]) @ T[a:b]
    return T


def chain_anchored(T_gt, xi, el, interval, sig_t, sig_r, rng, offline):
    """(N, 4, 4) trajectory with simulated anchors (GT + random error)."""
    A = {i: anchor_pose(T_gt[i], sig_t, sig_r, rng) for i in anchor_times(el, interval)}
    return apply_anchors(xi, el, A, offline)


def simulate(args):
    rigid, S = read_calib_parts()
    intervals = [float(x) for x in args.intervals]
    sigmas = [tuple(map(float, s.split(","))) for s in args.sigmas]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for run_dir in args.runs:
        arm = Path(run_dir).name
        data = []                                              # (T_gt, xi, el, P_us)
        for p in sorted(Path(run_dir).glob("fold*/best.pt")):
            k = int(p.parent.name[4:])
            cache = Path(run_dir) / "preds" / f"fold{k}.npz"
            if not cache.exists():
                raise SystemExit(f"{cache} missing: run diagnostics.py or poses.py first (GPU)")
            ck = torch.load(p, map_location="cpu", weights_only=False)
            ds, T_mc, _ = load_val_set(ck)
            z = np.load(cache, allow_pickle=True)
            preds = {(str(r), int(s)): v for (r, s), v in zip(z["keys"], z["values"])}
            P_us = us_points(invert_se3(T_mc) @ rigid, S)
            for key, c in gt_chains(ds).items():
                data.append((c["T_gt"], preds[key], c["t"] - c["t"][0], P_us))
        print(f"\n=== {arm}: {len(data)} segments")
        table = {}
        for mode in ("causal", "offline"):
            for st, sr in sigmas:
                for iv in intervals:
                    cam, us = [], []
                    for rep in range(args.repeats):
                        rng = np.random.default_rng(rep)
                        for T_gt, xi, el, P in data:
                            T = chain_anchored(T_gt, xi, el, iv, st, sr, rng, mode == "offline")
                            cam.append(np.linalg.norm(T[:, :3, 3] - T_gt[:, :3, 3], axis=1))
                            us.append(np.linalg.norm((T @ P - T_gt @ P)[:, :3], axis=1).mean(1))
                    cam, us = np.concatenate(cam), np.concatenate(us)
                    table[f"{mode}|{st:g},{sr:g}|{iv:g}"] = {
                        "cam_median": float(np.median(cam)), "cam_p95": float(np.percentile(cam, 95)),
                        "us_median": float(np.median(us)), "us_p95": float(np.percentile(us, 95))}
                print(f"  {mode:7s} sigma {st:g} mm / {sr:g} deg: US image median error (mm) " +
                      "  ".join(f"{iv:g}s {table[f'{mode}|{st:g},{sr:g}|{iv:g}']['us_median']:6.2f}"
                                for iv in intervals))
        json.dump({"arm": arm, "intervals_s": intervals, "sigmas": sigmas, "repeats": args.repeats,
                   "table": table}, open(out / f"simulate_{arm}.json", "w"), indent=2)
        write_sim_md(arm, table, intervals, sigmas, out / f"simulate_{arm}.md")
        plot_sim(arm, table, intervals, sigmas, out / f"simulate_{arm}.png")
        print(f"wrote {out / f'simulate_{arm}.md'}, .json, .png")


def write_sim_md(arm, table, intervals, sigmas, path):
    md = [f"# Simulated anchoring: {arm}", "",
          "Real odometry predictions; anchors = GT pose + random error of the given RMS. "
          "Median error over all frames of all held-out sweeps, at the US image "
          "(mean of 5 points spanning the image) and at the camera centre. "
          "'inf' = only each segment start is anchored.", ""]
    for mode in ("causal", "offline"):
        md += [f"## {mode}", "",
               "| anchor error (RMS) | " + " | ".join(f"every {iv:g} s" for iv in intervals) + " |",
               "|---|" + "---|" * len(intervals)]
        for st, sr in sigmas:
            cells = [table[f"{mode}|{st:g},{sr:g}|{iv:g}"] for iv in intervals]
            md.append(f"| {st:g} mm, {sr:g}° | " + " | ".join(
                f"{c['us_median']:.1f} (cam {c['cam_median']:.1f})" for c in cells) + " |")
        md.append("")
    md.append("Cells: US image median error in mm (camera centre in brackets). Target ~2 mm.")
    path.write_text("\n".join(md) + "\n")


def plot_sim(arm, table, intervals, sigmas, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fin = [iv for iv in intervals if np.isfinite(iv)]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3), sharey=True)
    for a, mode in zip(ax, ("causal", "offline")):
        for n, (st, sr) in enumerate(sigmas):
            y = [table[f"{mode}|{st:g},{sr:g}|{iv:g}"]["us_median"] for iv in fin]
            a.plot(fin, y, "-o", color=f"C{n}", label=f"anchor error {st:g} mm, {sr:g}°")
            if np.inf in intervals:
                a.axhline(table[f"{mode}|{st:g},{sr:g}|inf"]["us_median"], color=f"C{n}", ls=":", lw=0.8)
        a.axhline(2.0, color="gray", ls="--", lw=0.8)
        a.set_xscale("log")
        a.set_xticks(fin)
        a.set_xticklabels([f"{x:g}" for x in fin])
        a.set_xlabel("anchor interval (s)")
        a.set_title(mode)
        a.grid(alpha=0.3)
    ax[0].set_ylabel("median error at the US image (mm)")
    ax[0].legend(fontsize=8)
    fig.suptitle(f"Simulated anchoring on {arm} odometry (dotted: segment start only; dashed: 2 mm)")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


# --- learned anchors: training pairs ---

def map_keyframes(ds, every, scans=None):
    """The anchor map: every `every`-th usable room-scan row, as [(run, row)]."""
    return [(n, int(row)) for n in (scans or SCANS)
            for row in np.concatenate(ds.runs[n]["segments"])[::every]]


def build_pairs(args):
    """Wide-baseline training pairs (keyframe, query frame) that see the same scene.
    kind "scan": keyframe from a room scan, the deployment case. Queries come from every
      run: sweeps, and the room scans themselves (against keyframes of another scan, or
      of the same scan more than --min-gap-s apart).
    kind "sweep" (--sweep-pairs-per-query > 0): keyframe from a *different* sweep, as
      extra wide-baseline training data across sessions. The anchor map at run time stays
      room-scan only; these pairs only teach the network.
    Folds are applied at training time: a pair is used for training only if neither frame
    is from the held-out sweep, and for validation only if its query is (kind "scan")."""
    T_mc = load_hand_eye(HAND_EYE, "mm")
    cfg = RPRConfig(T_marker_cam=T_mc)
    runs = sorted({r for tr, va in leave_one_sweep_out(ROOT, SCANS) for r in tr + va})
    ds = RPRDataset(ROOT, runs, SCANS, cfg)
    K = ds.runs[SCANS[0]]["K"]
    key = map_keyframes(ds, args.keyframe_every)
    sets = {"scan": key}
    if args.sweep_pairs_per_query:
        sets["sweep"] = [(n, int(r)) for n in runs if n not in SCANS
                         for r in np.concatenate(ds.runs[n]["segments"])[:: args.keyframe_every]]
    sets = {k: {"key": v, "T": np.stack([ds.runs[n]["T_world_cam"][r] for n, r in v]),
                "run": np.array([n for n, _ in v]),
                "t": np.array([ds.runs[n]["stamps"][r] for n, r in v])} for k, v in sets.items()}
    per_query = {"scan": args.pairs_per_query, "sweep": args.sweep_pairs_per_query}
    depth_cache = {}

    def key_depth(k):                          # float16 halves the memory; 5 % depth tolerance
        if k not in depth_cache:
            depth_cache[k] = np.minimum(load_depth(*k, ds.runs, ROOT), 60000).astype(np.float16)
        return depth_cache[k]

    pairs = []
    for q_run in runs:
        n0 = len(pairs)
        rows = np.concatenate(ds.runs[q_run]["segments"])[:: args.query_every]
        for row in rows:
            T_q = ds.runs[q_run]["T_world_cam"][row]
            t_q = ds.runs[q_run]["stamps"][row]
            dq = load_depth(q_run, row, ds.runs, ROOT)
            for kind, S in sets.items():
                dist = np.linalg.norm(S["T"][:, :3, 3] - T_q[:3, 3], axis=1)
                ang = rot_angle_deg(S["T"][:, :3, :3], T_q[:3, :3][None])
                score = dist + args.mm_per_deg * ang
                if kind == "scan":
                    score[(S["run"] == q_run) & (np.abs(S["t"] - t_q) < args.min_gap_s)] = np.inf
                else:
                    score[S["run"] == q_run] = np.inf          # other sessions only
                cand = np.argsort(score)[: args.candidates]
                cand = cand[np.isfinite(score[cand])]
                if not len(cand):
                    continue
                cov = covisibility(dq, T_q, K, [key_depth(S["key"][i]) for i in cand], S["T"][cand],
                                   args.stride, cfg.min_depth, cfg.max_depth, args.depth_tol)
                for j in np.argsort(-cov)[: per_query[kind]]:
                    if cov[j] < args.min_covis:
                        break
                    b = cand[j]
                    pairs.append({"kind": kind, "key_run": S["key"][b][0], "key_row": S["key"][b][1],
                                  "q_run": q_run, "q_row": int(row), "covis": round(float(cov[j]), 3),
                                  "baseline_mm": round(float(dist[b]), 1),
                                  "angle_deg": round(float(ang[b]), 2)})
        new = pairs[n0:]
        counts = {k: sum(p["kind"] == k for p in new) for k in sets}
        print(f"  {q_run}: {len(rows)} queries -> " + ", ".join(f"{v} {k}" for k, v in counts.items())
              + " pairs" + (f" | baseline median {np.median([p['baseline_mm'] for p in new]):.0f} mm, "
                            f"angle {np.median([p['angle_deg'] for p in new]):.1f} deg" if new else ""))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"args": vars(args), "keyframes": key, "pairs": pairs}, open(out, "w"))
    counts = ", ".join(f"{sum(p['kind'] == k for p in pairs)} {k}" for k in sets)
    print(f"wrote {len(pairs)} pairs ({counts}), {len(key)} room-scan keyframes -> {out}")


def anchor_net(a, pretrained):
    return RPRNet(use_depth=a["use_depth"], use_us=False, pretrained=pretrained,
                  corr_radius=a["corr_radius"], coarse_radius=a["coarse_radius"])


# --- learned anchors: training ---

@torch.no_grad()
def mean_pose(Ts):
    """Average of rigid transforms: mean translation, mean rotation projected onto SO(3)."""
    U, _, Vt = np.linalg.svd(Ts[:, :3, :3].mean(0))
    R = U @ Vt
    if np.linalg.det(R) < 0:
        U[:, -1] *= -1
        R = U @ Vt
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, Ts[:, :3, 3].mean(0)
    return T


def predict_keyframe_pairs(net, a, ks, q, device):
    """Anchor network on the pairs (keyframe ks[j], frame q) -> (len(ks), 6) normalised xi."""
    batch = {"rgb": torch.from_numpy(np.stack([np.stack([f[0], q[0]]) for f in ks]).astype(np.float32))}
    if a["use_depth"]:
        batch["depth"] = torch.from_numpy(np.stack([np.stack([f[1], q[1]]) for f in ks]).astype(np.float32))
        batch["depth_mask"] = torch.from_numpy(np.stack([np.stack([f[2], q[2]]) for f in ks]).astype(np.float32))
    with torch.no_grad():
        return net(**model_inputs(batch, device))["xi"].double().cpu().numpy().reshape(-1, 6)


def start_pose(net, a, base_map, key, T_key, q, mean, std, device, max_keys=200, batch=16, tol_mm=30.0, tol_deg=10.0):
    """Start pose with no prior, as in use (--start anchor): pair the first frame with up to
    max_keys keyframes spread over the whole map, turn each prediction into an absolute pose,
    and keep the largest group that agrees within tol_mm and tol_deg of one member; its mean
    is the start pose. Keyframes that do not see the same scene give scattered poses and
    drop out. Returns (pose, group size)."""
    sel = np.linspace(0, len(key) - 1, min(max_keys, len(key))).round().astype(int)
    A = []
    for s in range(0, len(sel), batch):
        ks = [base_map.load_frame(*key[j]) for j in sel[s:s + batch]]
        A.append(T_key[sel[s:s + batch]] @ se3_exp(predict_keyframe_pairs(net, a, ks, q, device) * std + mean))
    A = np.concatenate(A)
    near = ((np.linalg.norm(A[:, None, :3, 3] - A[None, :, :3, 3], axis=-1) < tol_mm)
            & (rot_angle_deg(A[:, None, :3, :3], A[None, :, :3, :3]) < tol_deg))
    best = near[np.argmax(near.sum(1))]
    return mean_pose(A[best]), int(best.sum())


def tracker_free_keyframes(map_dir, key):
    """The keyframes' poses from a scr_map.py map (poses_<scan>.json, already aligned to Polaris for the
    evaluation) times its camera calibration X, so that keyframe pose @ relative pose = camera pose, as with
    Polaris. Keyframes the map did not place are dropped. -> (key, T_key)."""
    m = Path(map_dir)
    X = json.load(open(m / "map.json")).get("cam_calib")
    X = np.eye(4) if X is None else np.asarray(X, float)
    pose = {}
    for n in {n for n, _ in key}:
        for f in json.load(open(m / f"poses_{n}.json"))["frames"]:
            pose[(n, int(f["row"]))] = np.asarray(f["T_world_cam_pred"], float)
    kept = [(n, int(r)) for n, r in key if (n, int(r)) in pose and np.isfinite(pose[(n, int(r))]).all()]
    print(f"keyframes posed by the map {m} (no tracker): {len(kept)} of {len(key)}; camera calibration "
          f"{np.linalg.norm(X[:3, 3]):.1f} mm")
    return kept, np.stack([pose[k] @ X for k in kept])


def smooth_pgo(T_odo, el, anchors, sig_t, q_t, sig_r_deg, q_r_deg, fix_start=True):
    """Offline joint smoothing of one segment (a linearised pose graph).
    Unknowns: a world-frame position correction d_i (mm) and rotation correction phi_i
    (about the camera centre) per frame, applied to the pure odometry chain T_odo.
    Cost = sum over steps |d_i+1 - d_i|^2 / (q_t dt) + sum over anchors |d_a - c_a|^2 / sig_t^2
    (same for phi with q_r_deg, sig_r_deg), where c_a is the anchor's offset from odometry.
    Index 0 (the segment's start pose) is held with a tiny sigma (fix_start; otherwise it is
    an ordinary anchor, for a start pose from the anchors). Position and rotation are
    solved separately: the rotation corrections are ~1 deg, so their effect on the chained
    positions (well under 0.1 mm per second) is ignored."""
    N = len(T_odo)
    dt = np.maximum(np.diff(el), 1e-3)
    idx = sorted(anchors)
    out = T_odo.copy()
    for part, sig, q in (("t", sig_t, q_t), ("r", np.radians(sig_r_deg), np.radians(np.sqrt(q_r_deg)) ** 2)):
        H = np.zeros((N, N))
        w = 1.0 / (q * dt)                                   # odometry step weights
        H[np.arange(N - 1), np.arange(N - 1)] += w
        H[np.arange(1, N), np.arange(1, N)] += w
        H[np.arange(N - 1), np.arange(1, N)] -= w
        H[np.arange(1, N), np.arange(N - 1)] -= w
        b = np.zeros((N, 3))
        for a in idx:
            wa = 1e6 if a == 0 and fix_start else 1.0 / sig ** 2
            if part == "t":
                c = anchors[a][:3, 3] - T_odo[a][:3, 3]
            else:
                Rc = np.eye(4)
                Rc[:3, :3] = anchors[a][:3, :3] @ T_odo[a][:3, :3].T
                c = se3_log(Rc[None])[0][3:]
            H[a, a] += wa
            b[a] += wa * c
        x = np.linalg.solve(H, b)                            # (N, 3)
        if part == "t":
            out[:, :3, 3] = T_odo[:, :3, 3] + x
        else:
            Rx = se3_exp(np.concatenate([np.zeros((N, 3)), x], 1))[:, :3, :3]
            out[:, :3, :3] = Rx @ T_odo[:, :3, :3]
    return out


def save_preds(path, trajs):
    """{(run, seg): (N, 4, 4)} -> per-step xi in the prediction-cache format, so
    poses.py can export / plot / compound it like the model; plus each segment's start
    pose, which is not the true pose with --start anchor."""
    keys = list(trajs)
    values = np.empty(len(keys), dtype=object)
    values[:] = [se3_log(invert_se3(trajs[k][:-1]) @ trajs[k][1:]) for k in keys]
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, keys=np.array(keys, dtype=object), values=values, starts=np.stack([trajs[k][0] for k in keys]))


def evaluate_anchors(args):
    """Odometry (cached predictions of the odometry arm) + anchors from the anchor network.
    Each segment starts at its GT pose, as in every other evaluation, or with --start anchor
    at a pose from the anchor network with no prior (start_pose), as in use. Then every
    --interval s: retrieve --k room-scan keyframes near the current pose estimate
    (--retrieval odometry; 'oracle' uses the GT pose instead, to separate retrieval from
    pose regression), predict the keyframe -> current-frame pose for each, average the
    resulting absolute poses, and accept the anchor unless it jumps more than --gate mm
    from the current estimate. Accepted anchors reset the pose, or with --blend move it
    only part of the way: weight = odometry variance / (odometry + anchor variance), where
    the odometry variance grows by --odo-q per second and shrinks at each anchor (a scalar
    Kalman update; it assumes independent anchor errors, which the systematic part of the
    current anchors violates, so read it as a heuristic)."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    P = json.load(open(args.pairs))
    map_root, map_scans = args.map_root or ROOT, args.map_scans or SCANS
    own_map = Path(map_root) == Path(ROOT) and list(map_scans) == list(SCANS)
    test = Path(args.test_root).name if args.test_root else ""
    rigid, S = read_calib_parts()
    odo = Path(args.odometry)
    classical, scr_mode = args.anchor == "classical", args.anchor == "scr"
    if args.anchor == "network" and not args.ckpts:
        raise SystemExit("--ckpts (anchor network) is needed with --anchor network")
    if scr_mode and not args.scr_ckpt:
        raise SystemExit("--scr-ckpt is needed with --anchor scr")
    name = ("classical" if classical else f"scr-{Path(args.scr_ckpt).parent.name}" if scr_mode
            else Path(args.ckpts[0]).parent.parent.name)
    tag = (f"{name}-{args.retrieval}" + ("-blend" if args.blend else "")
           + (f"-odo-{args.odometry_source}" if args.odometry_source != "model" else "")
           + (f"-refine{args.refine}" if args.refine else "")
           + (f"-spread{args.accept_spread:g}" if args.accept_spread else "")
           + (f"-keydist{args.max_key_dist:g}" if args.max_key_dist else "")
           + (f"-every{args.interval:g}s" if args.interval != 1.0 else "") + (f"-k{args.k}" if args.k != 3 else "")
           + (f"-pgo{args.pgo_sigma:g}mm{args.pgo_sigma_deg:g}deg" if args.pgo and (args.pgo_sigma, args.pgo_sigma_deg) != (11.0, 1.0) else "")
           + (f"-recover{args.gate_recover}" if args.gate_recover else "")
           + (f"-scrframes{args.scr_frames}" if args.scr_frames > 1 else "")
           + ("-startanchor" if args.start == "anchor" else "") + (f"-trackerfree-{Path(args.map).name}" if args.map else "")
           + (f"-{test}" if test else "") + ("" if own_map else f"-map-{'+'.join(map_scans)}"))
    rows_out, starts, per_sweep = [], [], {}
    for ck_path in (args.ckpts if args.anchor == "network" else [None]):
        if classical or scr_mode:           # no anchor network: data settings as the anchor network's
            a, fold, mean, std = {"use_depth": True, "image_size": [360, 640]}, 0, None, None
        else:
            ack = torch.load(ck_path, map_location=device, weights_only=False)
            a, fold = ack["args"], ack["args"]["fold"]
            mean, std = np.asarray(ack["target_mean"]), np.asarray(ack["target_std"])
        ock = torch.load(odo / f"fold{fold}" / "best.pt", map_location="cpu", weights_only=False)
        ds_val, T_mc, val_runs = load_val_set(ock, args.test_root, args.test_runs)
        if args.odometry_source == "zero":    # no odometry: the pose only changes at anchors (anchors-only ablation)
            preds = {k: np.zeros((len(c["frames"]) - 1, 6)) for k, c in gt_chains(ds_val).items()}
        else:
            cache = odo / "preds" / (f"fold{fold}{'_' + test if test else ''}.npz" if args.odometry_source == "model"
                                     else f"{args.odometry_source}_fold{fold}.npz")
            if not cache.exists():
                raise SystemExit(f"{cache} missing: run eval.py / diagnostics.py / poses.py on {odo} first")
            z = np.load(cache, allow_pickle=True)
            preds = {(str(r), int(s)): v for (r, s), v in zip(z["keys"], z["values"])}
        cfg = RPRConfig(T_marker_cam=T_mc, use_depth=a["use_depth"], image_size=tuple(a["image_size"]))
        base_map = RPRDataset(map_root, map_scans, map_scans, cfg)        # the room scans (anchor map)
        base = RPRDataset(args.test_root or ROOT, val_runs, [], cfg)       # the evaluated sweeps
        key = ([tuple(k) for k in P["keyframes"]] if own_map
               else map_keyframes(base_map, args.keyframe_every, map_scans))
        T_key = np.stack([base_map.runs[n]["T_world_cam"][r] for n, r in key])
        if args.map:                        # keyframes posed by a map without a tracker (US_SCR scr_map.py), not Polaris
            key, T_key = tracker_free_keyframes(args.map, key)
        net = None
        if scr_mode:                        # scene coordinates + PnP-RANSAC (scr.py)
            from scr import load_scr, localize
            scr_net, scr_ck = load_scr(args.scr_ckpt, device)

            def scr_pose(run, row):
                r = base.runs[run]
                return localize(scr_net, scr_ck, base.load_frame(run, row)[0], np.asarray(r["K"], float),
                                r["hw"][1], device, args.scr_px, args.scr_min_inliers)

            def scr_pose_multi(run, rows, rels):
                """--scr-frames > 1: one anchor from the correspondences of several chain frames, each
                brought into the newest frame's camera with the odometry (rels[k]: frame k -> newest).
                localize_multi is provided by US_SCR tools/anchoring_kabsch.py."""
                from scr import localize_multi
                r = base.runs[run]
                return localize_multi(scr_net, scr_ck, base, run, rows, rels, np.asarray(r["K"], float),
                                      r["hw"][1], device, args.scr_min_inliers)
        elif not classical:
            net = anchor_net(a, pretrained=False).to(device)
            net.load_state_dict(ack["model"])
            net.eval()
        else:
            sys.path.insert(0, str(Path(__file__).resolve().parent))      # baselines/
            from anchor_classical import pnp_pose, sift_features
            sift = cv2.SIFT_create(nfeatures=args.cl_features)
            K_full = np.array(base_map.runs[map_scans[0]]["K"], float)
            feat_cache = {}

            def raw_feats(ds, root, n, row, with_depth):
                g = cv2.imread(str(Path(root) / n / ds.runs[n]["df"]["rgb"].iloc[row]), cv2.IMREAD_GRAYSCALE)
                return sift_features(g, load_depth(n, row, ds.runs, root) if with_depth else None, sift)

            def key_feats(j):
                if j not in feat_cache:
                    feat_cache[j] = raw_feats(base_map, map_root, *key[j], True)
                return feat_cache[j]

            def solve(j, fq):              # keyframe j -> frame pose T_k_q, or None
                return pnp_pose(key_feats(j), fq, K_full, args.cl_ratio, args.cl_ransac_px,
                                args.cl_min_inliers, cfg.min_depth, cfg.max_depth)
        P_us = us_points(invert_se3(T_mc) @ rigid, S)
        failed = {}                         # --anchor classical: anchors due but not solved, per sweep
        print(f"\n=== fold {fold}: {val_runs} | anchors {'classical (SIFT + PnP-RANSAC)' if classical else ck_path} | "
              f"odometry {odo.name} ({args.odometry_source}) | map {'+'.join(map_scans)} ({len(key)} keyframes)")

        trajs = {"none": {}, "causal": {}, "offline": {}}
        if args.pgo:
            trajs["pgo"] = {}
        chains = gt_chains(ds_val)
        for n_seg, ((run, sid), c) in enumerate(chains.items()):
            if args.max_segments and n_seg >= args.max_segments:
                break
            T_gt, xi, el, frames = c["T_gt"], preds[(run, sid)], c["t"] - c["t"][0], c["frames"]
            due = set(anchor_times(el, args.interval)[1:])
            steps = se3_exp(xi)
            T0 = T_gt[0]
            if args.start == "anchor" and scr_mode:      # absolute pose directly, no prior needed
                T0, n_agree = scr_pose(run, int(frames[0]))
                T0 = T0 if T0 is not None else T_key[0]
            elif args.start == "anchor" and classical:   # the keyframe (of 200 across the map) with most inliers
                fq0 = raw_feats(base, args.test_root or ROOT, run, int(frames[0]), False)
                tries = [(solve(j, fq0), j) for j in np.linspace(0, len(key) - 1, min(200, len(key))).round().astype(int)]
                (T_kq, _, n_agree), j0 = max(tries, key=lambda x: x[0][2])
                T0 = T_key[j0] @ T_kq if T_kq is not None else T_key[j0]
            elif args.start == "anchor":
                T0, n_agree = start_pose(net, a, base_map, key, T_key, base.load_frame(run, int(frames[0])),
                                         mean, std, device)
                starts.append({"run": run, "segment": sid, "agree": n_agree,
                               "err_mm": float(np.linalg.norm(T0[:3, 3] - T_gt[0][:3, 3])),
                               "err_deg": float(rot_angle_deg(T_gt[0][:3, :3], T0[:3, :3]))})
                print(f"  {run} segment {sid}: start pose from the anchors, error {starts[-1]['err_mm']:.1f} mm / "
                      f"{starts[-1]['err_deg']:.1f} deg ({n_agree} {'inliers' if classical else 'keyframes agree'})")
            T = np.empty_like(T_gt)
            T[0] = T0
            anchors = {0: T0}
            raw = {0: T0}                   # accepted anchor poses before any blending (--pgo)
            pending = []                    # --gate-recover: anchors rejected since the last accepted one
            var, t_last = 0.0, 0.0          # --blend: expected odometry error variance (mm^2)
            for i in range(1, len(T_gt)):
                T[i] = T[i - 1] @ steps[i - 1]
                if i not in due:
                    continue
                var += args.odo_q * (el[i] - t_last)
                t_last = el[i]
                ref = T_gt[i] if args.retrieval == "oracle" else T[i]
                if classical:
                    fq = raw_feats(base, args.test_root or ROOT, run, int(frames[i]), False)
                elif not scr_mode:
                    q = base.load_frame(run, int(frames[i]))
                for _ in range(0 if scr_mode else 1 + args.refine):  # --refine: re-pair with keyframes near the estimate
                    dist = np.linalg.norm(T_key[:, :3, 3] - ref[:3, 3], axis=1)
                    cand = np.argsort(dist + args.mm_per_deg * rot_angle_deg(T_key[:, :3, :3], ref[:3, :3][None]))[: args.k]
                    if classical:                 # keep the keyframes PnP-RANSAC solves
                        sol = [(j, solve(j, fq)[0]) for j in cand]
                        cand = np.array([j for j, T_kq in sol if T_kq is not None], int)
                        if not len(cand):
                            break
                        xp = se3_log(np.stack([T_kq for _, T_kq in sol if T_kq is not None]))
                    else:
                        ks = [base_map.load_frame(*key[j]) for j in cand]
                        xp = predict_keyframe_pairs(net, a, ks, q, device) * std + mean
                    A = mean_pose(T_key[cand] @ se3_exp(xp))
                    ref = A
                if scr_mode:                      # absolute pose, no keyframes
                    if args.scr_frames > 1:       # pool the previous chain frames, linked by odometry only
                        rows, rels, S = [int(frames[i])], [np.eye(4)], np.eye(4)
                        for j in range(i - 1, max(i - args.scr_frames, -1), -1):
                            S = steps[j] @ S      # pose of frame i in frame j
                            rows.append(int(frames[j]))
                            rels.append(invert_se3(S[None])[0])
                        A, _ = scr_pose_multi(run, rows, rels)
                    else:
                        A, _ = scr_pose(run, int(frames[i]))
                    cand, xp = np.zeros(0, int), np.zeros((0, 6))
                    if A is None:
                        failed[run] = failed.get(run, 0) + 1
                        continue
                elif not len(cand):               # no keyframe solved: no anchor this time
                    failed[run] = failed.get(run, 0) + 1
                    continue
                jump = float(np.linalg.norm(A[:3, 3] - T[i][:3, 3]))
                spread = float(np.linalg.norm((T_key[cand] @ se3_exp(xp))[:, :3, 3] - A[:3, 3], axis=1).mean()) if len(cand) else 0.0
                key_dist = float(np.linalg.norm(T_key[cand][:, :3, 3] - A[:3, 3], axis=1).min()) if len(cand) else 0.0
                ok = (jump <= args.gate and (not args.accept_spread or spread <= args.accept_spread)
                      and (not args.max_key_dist or key_dist <= args.max_key_dist))
                # --gate-recover: once a wrong anchor has been accepted, every correct one jumps more than
                # the gate and is rejected for good. If the last N rejected anchors agree with each other
                # (each carried forward to now with the odometry since it was rejected), accept the newest.
                recovered = False
                if not ok and args.gate_recover:
                    pending = (pending + [(i, A)])[-args.gate_recover:]
                    if len(pending) == args.gate_recover and all(
                            np.linalg.norm((Aj @ invert_se3(T[j][None])[0] @ T[i])[:3, 3] - A[:3, 3])
                            <= args.gate_recover_mm for j, Aj in pending[:-1]):
                        ok = recovered = True
                if ok:
                    pending = []
                w = 1.0
                if ok:
                    if args.blend:          # move toward the anchor by var / (var + anchor var)
                        w = var / (var + args.anchor_sigma ** 2)
                        var *= 1 - w
                        C = se3_log((invert_se3(T[i]) @ A)[None])[0]
                        T[i] = T[i] @ se3_exp((w * C)[None])[0]
                    else:
                        T[i] = A
                    anchors[i] = T[i].copy()
                    raw[i] = A
                rows_out.append({"run": run, "segment": sid, "index": i, "t": float(el[i]),
                                 "accepted": ok, "recovered": recovered, "weight": w if ok else 0.0, "jump_mm": jump,
                                 "err_mm": float(np.linalg.norm(A[:3, 3] - T_gt[i][:3, 3])),
                                 "err_deg": float(rot_angle_deg(T_gt[i][:3, :3], A[:3, :3])),
                                 "spread_mm": spread,
                                 "key_dist_mm": float(np.linalg.norm(T_key[cand][:, :3, 3] - A[:3, 3], axis=1).mean()) if len(cand) else 0.0,
                                 # per keyframe: predicted vs true keyframe -> frame pose (mm | rad)
                                 "keyframes": [f"{key[j][0]}:{key[j][1]}" for j in cand],
                                 "xi_pred": xp.round(5).tolist(),
                                 "xi_gt": se3_log(invert_se3(T_key[cand]) @ T_gt[i][None]).round(5).tolist() if len(cand) else []})
            trajs["causal"][(run, sid)] = T
            trajs["offline"][(run, sid)] = apply_anchors(xi, el, anchors, offline=True)
            trajs["none"][(run, sid)] = apply_anchors(xi, el, {0: T0}, offline=False)
            if args.pgo:
                trajs["pgo"][(run, sid)] = smooth_pgo(trajs["none"][(run, sid)], el, raw, args.pgo_sigma,
                                                      args.odo_q, args.pgo_sigma_deg, args.pgo_q_deg,
                                                      fix_start=args.start == "gt")

        for val_run in val_runs:
            res = {}
            for mode, tj in trajs.items():
                cam, us, step = [], [], []
                for k2, T in tj.items():
                    if k2[0] != val_run:
                        continue
                    T_g = chains[k2]["T_gt"]
                    cam.append(np.linalg.norm(T[:, :3, 3] - T_g[:, :3, 3], axis=1))
                    D = (T @ P_us - T_g @ P_us)[:, :3]                       # (N, 3, 5) error vectors
                    us.append(np.linalg.norm(D, axis=1).mean(1))
                    step.append(np.linalg.norm(np.diff(D, axis=0), axis=1).mean(1))   # change of error per step
                if not cam:
                    continue
                res[mode] = {"cam_median": float(np.median(np.concatenate(cam))),
                             "us_median": float(np.median(np.concatenate(us))),
                             "us_step_mean": float(np.mean(np.concatenate(step)))}
            if not res:
                continue
            an = [r for r in rows_out if r["run"] == val_run]
            res["anchors"] = {"n": len(an), "accepted_pct": 100 * float(np.mean([r["accepted"] for r in an])) if an else float("nan"),
                              "err_mm_median": float(np.median([r["err_mm"] for r in an])) if an else float("nan"),
                              "err_mm_p90": float(np.percentile([r["err_mm"] for r in an], 90)) if an else float("nan"),
                              "err_deg_median": float(np.median([r["err_deg"] for r in an])) if an else float("nan")}
            if classical or scr_mode:
                res["anchors"]["unsolved"] = failed.get(val_run, 0)
            st = [s for s in starts if s["run"] == val_run]
            if st:
                res["start"] = {"segments": len(st), "err_mm_max": max(s["err_mm"] for s in st),
                                "err_deg_max": max(s["err_deg"] for s in st)}
            per_sweep[val_run] = res
            print(f"  {val_run}: anchors {res['anchors']['n']}"
                  + (f" (+{failed.get(val_run, 0)} unsolved)" if classical or scr_mode else "")
                  + f" | accepted {res['anchors']['accepted_pct']:.0f}% | error median "
                  f"{res['anchors']['err_mm_median']:.1f} mm (p90 {res['anchors']['err_mm_p90']:.1f}), "
                  f"{res['anchors']['err_deg_median']:.2f} deg")
            print("    US image median error (step-to-step error): " + " | ".join(
                f"{m} {res[m]['us_median']:.1f} mm ({res[m]['us_step_mean']:.2f})" for m in trajs if m in res))
        for mode in [m for m in trajs if m != "none"]:
            save_preds(odo / "preds" / f"anchored-{mode}-{tag}_fold{fold}.npz", trajs[mode])

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    json.dump({"args": vars(args), "per_sweep": per_sweep, "starts": starts, "anchors": rows_out},
              open(out / f"anchor_eval_{tag}.json", "w"), indent=2)
    modes = [m for m in ("none", "causal", "offline", "pgo") if m in next(iter(per_sweep.values()))]
    label = {"none": "unanchored", "causal": "causal", "offline": "offline", "pgo": "offline pose graph"}
    md = [f"# {'Classical anchors (SIFT + PnP-RANSAC with depth)' if classical else f'Scene coordinate anchors: {name}' if scr_mode else f'Learned anchors: {name}'} ({args.retrieval} retrieval)", "",
          f"Odometry: {odo.name} ({args.odometry_source}). Anchor every {args.interval:g} s, {args.k} keyframes averaged, "
          f"gate {args.gate:g} mm"
          + (f", spread filter {args.accept_spread:g} mm" if args.accept_spread else "")
          + (f", keyframe distance filter {args.max_key_dist:g} mm" if args.max_key_dist else "")
          + (f", {args.refine} refinement pass(es)" if args.refine else "")
          + (f", blended (anchor sigma {args.anchor_sigma:g} mm, odometry growth "
             f"{args.odo_q:g} mm²/s)" if args.blend else ", reset to the anchor")
          + (f"; pose graph: anchor sigma {args.pgo_sigma:g} mm / {args.pgo_sigma_deg:g} deg, odometry growth "
             f"{args.odo_q:g} mm²/s / {args.pgo_q_deg:g} deg²/s" if args.pgo else "")
          + (". Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment)"
             if args.start == "anchor" else ". Segment starts at GT")
          + ". Median error at the US image (mm); in brackets the mean "
            "step-to-step error (mm), which matters for a smooth reconstruction.", "",
          "| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | "
          + ("start error mm / deg | " if starts else "") + " | ".join(label[m] for m in modes) + " |",
          "|---|---|---|---|---|" + ("---|" if starts else "") + "---|" * len(modes)]
    for sw, r in per_sweep.items():
        A = r["anchors"]
        md.append(f"| {sw} | {A['n']} | {A['accepted_pct']:.0f} % | {A['err_mm_median']:.1f} / {A['err_mm_p90']:.1f} | "
                  f"{A['err_deg_median']:.2f} | "
                  + (f"{r['start']['err_mm_max']:.1f} / {r['start']['err_deg_max']:.1f} | " if "start" in r else "")
                  + " | ".join(f"{r[m]['us_median']:.1f} ({r[m]['us_step_mean']:.2f})" for m in modes) + " |")
    if len(per_sweep) > 1:
        m = lambda f: np.nanmean([f(r) for r in per_sweep.values()])
        md.append(f"| **mean** | | {m(lambda r: r['anchors']['accepted_pct']):.0f} % | "
                  f"{m(lambda r: r['anchors']['err_mm_median']):.1f} / {m(lambda r: r['anchors']['err_mm_p90']):.1f} | "
                  f"{m(lambda r: r['anchors']['err_deg_median']):.2f} | "
                  + (f"{m(lambda r: r['start']['err_mm_max']):.1f} / {m(lambda r: r['start']['err_deg_max']):.1f} | "
                     if starts else "")
                  + " | ".join(f"{m(lambda r, mo=mo: r[mo]['us_median']):.1f} "
                               f"({m(lambda r, mo=mo: r[mo]['us_step_mean']):.2f})" for mo in modes) + " |")
    md += ["", "Compare the anchor error with simulate_<arm>.md: that table gives the trajectory "
           "error to expect for a given anchor error.", "",
           f"Poses for poses.py: `python poses.py --ckpts {odo}/fold*/best.pt --source anchored-offline-{tag}"
           + (f" --test-root {args.test_root} --out <folder for this test>" if args.test_root else "")
           + f"` (or anchored-pgo-{tag}, anchored-causal-{tag})."]
    (out / f"anchor_eval_{tag}.md").write_text("\n".join(md) + "\n")
    print(f"\nwrote {out / f'anchor_eval_{tag}.md'} and .json")


def main():
    common = argparse.ArgumentParser(add_help=False)          # data flags, given after the subcommand
    common.add_argument("--root", default="data/train", help="data folder")
    common.add_argument("--scan-runs", nargs="+", required=True,
                        help="room scans: the keyframe map and extra training data")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("coverage", parents=[common])
    c.add_argument("--out", default="runs/anchoring-gap4")
    c.add_argument("--keyframe-every", type=int, default=5)
    c.add_argument("--query-every", type=int, default=10)
    c.add_argument("--candidates", type=int, default=10)
    c.add_argument("--mm-per-deg", type=float, default=28.0,
                   help="pose-distance weight: 1 deg shifts the view ~28 mm at 1.6 m")
    c.add_argument("--stride", type=int, default=16, help="depth pixel stride for co-visibility")
    c.add_argument("--depth-tol", type=float, default=0.05, help="relative depth tolerance")
    s = sub.add_parser("simulate", parents=[common])
    s.add_argument("--runs", nargs="+", required=True)
    s.add_argument("--out", default="runs/anchoring-gap4")
    s.add_argument("--intervals", nargs="+", default=["0.5", "1", "2", "5", "inf"])
    s.add_argument("--sigmas", nargs="+", default=["0,0", "1,0.25", "2,0.5", "5,1"],
                   help="anchor error RMS as 'mm,deg'")
    s.add_argument("--repeats", type=int, default=3)

    p = sub.add_parser("pairs", parents=[common], help="wide-baseline training pairs for the anchor network (CPU)")
    p.add_argument("--out", default="runs/anchor-pairs/pairs_v2.json")
    p.add_argument("--keyframe-every", type=int, default=5)
    p.add_argument("--query-every", type=int, default=2)
    p.add_argument("--candidates", type=int, default=10)
    p.add_argument("--pairs-per-query", type=int, default=3, help="room-scan keyframes per query")
    p.add_argument("--sweep-pairs-per-query", type=int, default=3,
                   help="also pair each query with up to N keyframes of *other* sweeps (training data only)")
    p.add_argument("--min-covis", type=float, default=0.3)
    p.add_argument("--min-gap-s", type=float, default=3.0,
                   help="room-scan query vs keyframe of the same scan: at least this far apart in time")
    p.add_argument("--mm-per-deg", type=float, default=28.0)
    p.add_argument("--stride", type=int, default=16)
    p.add_argument("--depth-tol", type=float, default=0.05)

    e = sub.add_parser("evaluate", parents=[common], help="odometry + learned anchors on the held-out sweeps (GPU)")
    e.add_argument("--ckpts", nargs="+", default=None, help="anchor network fold*/best.pt (not with --anchor classical)")
    e.add_argument("--anchor", default="network", choices=["network", "classical", "scr"],
                   help="classical: SIFT + PnP-RANSAC with the keyframe depth instead of the anchor network (note §6.5); "
                        "scr: scene coordinate regression + PnP-RANSAC (scr.py, --scr-ckpt)")
    e.add_argument("--scr-ckpt", default=None, help="--anchor scr: scr.py checkpoint trained on this map's room scans")
    e.add_argument("--scr-px", type=float, default=10.0, help="--anchor scr: RANSAC reprojection error (px, full res)")
    e.add_argument("--scr-min-inliers", type=int, default=30, help="--anchor scr: fewer inliers = no anchor")
    e.add_argument("--cl-features", type=int, default=4000, help="--anchor classical: SIFT features per image")
    e.add_argument("--cl-ratio", type=float, default=0.8, help="--anchor classical: ratio test")
    e.add_argument("--cl-ransac-px", type=float, default=4.0, help="--anchor classical: RANSAC reprojection error (px, full res)")
    e.add_argument("--cl-min-inliers", type=int, default=20, help="--anchor classical: fewer inliers = keyframe not solved")
    e.add_argument("--odometry-source", default="model",
                   help="odometry steps: 'model' (the arm's prediction cache), 'zero' (no odometry: anchors only, "
                        "use with a small --interval), or another cache in <arm>/preds/<source>_fold<k>.npz, "
                        "e.g. classical-vo-test_4XXA from tools/classical_odometry.py")
    e.add_argument("--odometry", default="runs/rpr-rgb-gap4", help="odometry arm (needs preds/ cache)")
    e.add_argument("--pairs", default="runs/anchor-pairs/pairs_v2.json", help="for the keyframe map")
    e.add_argument("--out", default="runs/anchoring-gap4")
    e.add_argument("--interval", type=float, default=1.0)
    e.add_argument("--k", type=int, default=3, help="keyframes per anchor, poses averaged")
    e.add_argument("--retrieval", default="odometry", choices=["odometry", "oracle"])
    e.add_argument("--gate-recover", type=int, default=0,
                   help="accept an anchor despite --gate when this many consecutive rejected anchors agree "
                        "(carried forward with the odometry, within --gate-recover-mm); recovers from a wrong "
                        "accepted anchor. 0: off")
    e.add_argument("--gate-recover-mm", type=float, default=20.0)
    e.add_argument("--scr-frames", type=int, default=1,
                   help="--anchor scr: one anchor from this many chain frames (needs US_SCR tools/anchoring_kabsch.py)")
    e.add_argument("--gate", type=float, default=50.0,
                   help="reject an anchor that moves the estimate by more than this (mm)")
    e.add_argument("--mm-per-deg", type=float, default=28.0)
    e.add_argument("--blend", action="store_true",
                   help="weight each anchor against the odometry by their expected errors instead of resetting")
    e.add_argument("--anchor-sigma", type=float, default=22.0,
                   help="--blend: expected anchor error (mm), e.g. the validation median")
    e.add_argument("--odo-q", type=float, default=29.0,
                   help="--blend: odometry error growth (mm^2 per s; 29 = ~5.4 mm after 1 s)")
    e.add_argument("--refine", type=int, default=0,
                   help="re-pair with the keyframes nearest the anchor estimate and predict again, N times")
    e.add_argument("--accept-spread", type=float, default=0.0,
                   help="also reject an anchor whose keyframe estimates disagree by more than this (mm); 0 = off")
    e.add_argument("--max-key-dist", type=float, default=0.0,
                   help="also reject an anchor that lies more than this (mm) from its nearest keyframe: the network "
                        "had to bridge a distance where it is unreliable (note §6.3); 0 = off")
    e.add_argument("--pgo", action="store_true",
                   help="also report offline joint smoothing (pose graph) of odometry + accepted anchors")
    e.add_argument("--pgo-sigma", type=float, default=11.0, help="pose graph: anchor position sigma (mm)")
    e.add_argument("--pgo-sigma-deg", type=float, default=1.0, help="pose graph: anchor rotation sigma (deg)")
    e.add_argument("--pgo-q-deg", type=float, default=0.1,
                   help="pose graph: odometry rotation error growth (deg^2/s); position uses --odo-q")
    e.add_argument("--max-segments", type=int, default=0, help="smoke test: first N segments")
    e.add_argument("--test-root", default=None,
                   help="evaluate on the sweeps of this folder (needs odometry eval.py --test-root first)")
    e.add_argument("--test-runs", nargs="+", default=None, help="with --test-root: only these (default: every run-*)")
    e.add_argument("--map", default=None, help="scr_map.py folder: keyframe poses from this map without a tracker "
                   "(times its camera calibration) instead of Polaris")
    e.add_argument("--map-root", default=None, help="folder of the room scans used as the map (default: --root)")
    e.add_argument("--map-scans", nargs="+", default=None, help="room scans used as the map (default: --scan-runs)")
    e.add_argument("--keyframe-every", type=int, default=5, help="map keyframes when --map-* differs from the pairs")
    e.add_argument("--start", default="gt", choices=["gt", "anchor"],
                   help="segment start pose: the true pose, or from the anchor network with no prior (as in use)")
    args = ap.parse_args()
    global ROOT, SCANS
    ROOT, SCANS = args.root, args.scan_runs
    {"coverage": coverage, "simulate": simulate, "pairs": build_pairs,
     "evaluate": evaluate_anchors}[args.cmd](args)


if __name__ == "__main__":
    main()
