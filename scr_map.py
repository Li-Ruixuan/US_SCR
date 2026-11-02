"""
Map a room without a tracker: the SCR network builds the room-scan poses itself (ACE0-style, Brachmann
et al. 2024, here with the measured depth). The poses it writes replace Polaris as the training labels,
so the whole system needs no tracker; Polaris is used only to evaluate the map.

  1. seed: one room-scan frame defines the map frame (identity pose); the frames of the next and
     previous --seed-seconds join by frame-to-frame depth ICP (point-to-plane, geometry only: no
     features, no learning). A network trained on one image does not recognise even the next views
     (3XX: 43 inliers median), so the seed needs several views;
  2. rounds: train the network on the frames mapped so far (labels: their depth placed with their
     poses), then localise unmapped frames with it (Kabsch RANSAC on the depth). Candidates: unmapped
     frames within --reach rows of a mapped frame of the same run (join with >= --gate inliers, if the
     pose is plausible given that frame: <= --max-speed mm/s and --max-turn deg/s plus a margin), and
     every --probe-every-th other unmapped frame (join with >= --gate-far inliers; other scans of the
     room join this way). Then depth ICP extends every edge of the map by up to --icp-extend frames, so
     the map grows even where the network does not yet recognise the views. Stops when a round adds
     fewer than --min-growth of the frames;
  3. final pass: every frame localised again with the last network (>= --gate-far inliers), replacing
     the rough early poses; then refine (--refine-steps): the network and a pose correction per mapped
     frame trained jointly (T_k <- T_k Exp(delta_k), seed frame fixed), so pose errors are corrected
     instead of learned (off by default: on 3XX it made the map worse);
     then the pose graph (on by default; --no-graph): depth ICP between frames --graph-offsets apart (1 to 30,
     started from the map's relative pose) gives exact local motion, each frame's map pose stays as a loose
     prior on its view points; robust least squares. Without it, every frame is localised on its own and the
     map bends over seconds (3XX: 7 mm error of the 1 s motion, shape 8.5 mm at the US image).
     --from <map folder> runs only this step on an existing map (edges cached in its graph_edges.npz);
  4. evaluate against Polaris after one rigid alignment of the whole map (Kabsch on the points 1 m in front
     of each camera) and one fixed camera-frame transform (camera calibration, a property of the probe: Polaris
     gives the camera through the hand-eye, the map from the camera itself; --no-cam-calib leaves it out):
     scene-point / camera position / rotation error per frame and the error of 1 s relative motions. The
     calibration is saved in map.json; `scr_anchor.py track --cam-calib map.json` applies it;
  5. write the aligned poses per scan in the poses.py JSON format, for
     `scr_anchor.py train --label-poses` (frames that never joined the map get no label).

Only rows with a Polaris pose are used (the dataloader's segments), so that every map pose can be
evaluated; in deployment all rows would be.

  python scr_map.py --root $DATA/train_3XX --scan-runs room-301 room-302 --out runs/map-3XX
  python scr_anchor.py train --root $DATA/train_3XX --scan-runs room-301 room-302 \\
      --label-poses runs/map-3XX/poses_room-301.json runs/map-3XX/poses_room-302.json --out runs/v2map-3XX
  python scr_anchor.py track --ckpt runs/v2map-3XX/best.pt --test-root $DATA/train_3XX --every 2 --out runs/track-v2map-3XX
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from torch.utils.data import DataLoader, Dataset, RandomSampler

import scr_anchor as sa
from dataloader import RPRConfig, RPRDataset, load_hand_eye
from scr import load_depth_mm


# ---------------------------------------------------------------- helpers

def so3_exp(w):
    """Rotation matrices (B, 3, 3) from rotation vectors (B, 3) (Rodrigues)."""
    th = w.norm(dim=1, keepdim=True).clamp_min(1e-9)
    k = w / th
    K = torch.zeros(len(w), 3, 3, device=w.device, dtype=w.dtype)
    K[:, 0, 1], K[:, 0, 2], K[:, 1, 2] = -k[:, 2], k[:, 1], -k[:, 0]
    K = K - K.transpose(1, 2)
    s, c = th.sin()[..., None], th.cos()[..., None]
    return torch.eye(3, device=w.device, dtype=w.dtype) + s * K + (1 - c) * K @ K


VIEW = np.array([[0, 0, 1000.0], [300, 0, 1000], [0, 300, 1000], [-300, -300, 1000]])   # camera frame, mm


def view_points(T):
    """Points 1 m in front of each camera (N, 4, 3), placed with the poses T (N, 4, 4): what the camera sees,
    so they fix the orientation (a room scan barely moves the camera: its positions span a few cm only)."""
    return np.einsum("nij,kj->nki", T[:, :3, :3], VIEW) + T[:, None, :3, 3]


def align(Te, Tg):
    """Rigid A (4x4) with A Te ~ Tg for poses (N, 4, 4): Kabsch on their view points (no scale)."""
    R, t = sa.kabsch(view_points(Te).reshape(-1, 3), view_points(Tg).reshape(-1, 3))
    A = np.eye(4)
    A[:3, :3], A[:3, 3] = R, t
    return A


def align_calib(Te, Tg, iters=10):
    """Rigid A (world frame) and X (camera frame) with A Te X ~ Tg: the map's alignment plus one fixed transform
    in the camera frame, the same for every frame. Polaris gives the camera pose through the hand-eye
    calibration, the map gives it from the camera itself, so a hand-eye error appears as X (3XX: ~10 mm).
    X is a property of the probe (camera -> US image), estimated once on the room scan; it never enters the
    labels. Alternating: A by Kabsch on the view points, X = mean of (A Te)^-1 Tg."""
    X = np.eye(4)
    for _ in range(iters):
        A = align(Te @ X, Tg)
        D = np.linalg.inv(A @ Te) @ Tg
        X = np.eye(4)
        X[:3, :3] = Rotation.from_matrix(D[:, :3, :3]).mean().as_matrix()
        X[:3, 3] = np.median(D[:, :3, 3], axis=0)
    return align(Te @ X, Tg), X


def map_errors(est, gt, items, rows_per_s=30, calib=False):
    """Map vs Polaris after one rigid alignment of the whole map (on the view points) and, with calib, one fixed
    camera-frame transform X (align_calib): per frame the error of the scene points 1 m in front of the camera
    (what the training labels are made of), camera position and rotation; and the error of relative motions
    over 1 s (local consistency, needs no alignment). -> (A, errors, X)."""
    ok = [k for k, (n, r) in enumerate(items) if np.isfinite(est[n][r]).all()]
    if len(ok) < 3:
        return None, {}, None
    Te = np.stack([est[items[k][0]][items[k][1]] for k in ok])
    Tg = np.stack([gt[items[k][0]][items[k][1]] for k in ok])
    A, X = align_calib(Te, Tg) if calib else (align(Te, Tg), np.eye(4))
    Ta = A @ Te @ X
    dv = np.linalg.norm(view_points(Ta) - view_points(Tg), axis=2).mean(1)
    dt = np.linalg.norm(Ta[:, :3, 3] - Tg[:, :3, 3], axis=1)
    dR = np.einsum("nji,njk->nik", Ta[:, :3, :3], Tg[:, :3, :3])
    dr = np.degrees(np.arccos(np.clip((np.trace(dR, axis1=1, axis2=2) - 1) / 2, -1, 1)))
    rel = []
    for n in {n for n, _ in items}:                              # 1 s relative motions within a run
        rows = sorted(r for m, r in items if m == n and np.isfinite(est[n][r]).all())
        have = set(rows)
        for r in rows:
            if r + rows_per_s in have:
                Re = np.linalg.inv(est[n][r] @ X) @ est[n][r + rows_per_s] @ X
                Rg = np.linalg.inv(gt[n][r]) @ gt[n][r + rows_per_s]
                rel.append(np.linalg.norm(Re[:3, 3] - Rg[:3, 3]))
    q = lambda v, p: float(np.percentile(v, p)) if len(v) else None
    cal = {"calib_mm": float(np.linalg.norm(X[:3, 3])),
           "calib_deg": float(np.degrees(np.linalg.norm(Rotation.from_matrix(X[:3, :3]).as_rotvec())))} if calib else {}
    return A, {"mapped": len(ok), "frames": len(items), "mapped_pct": 100 * len(ok) / len(items),
               "view_mm_median": q(dv, 50), "view_mm_p90": q(dv, 90), "pos_mm_median": q(dt, 50), "pos_mm_p90": q(dt, 90), "rot_deg_median": q(dr, 50),
               "rel1s_mm_median": q(rel, 50), "rel1s_mm_p90": q(rel, 90), **cal}, X


def depth_cloud(ds, root, n, r, stride, max_depth):
    """Camera-frame points (N, 3, mm) and unit normals (N, 3, towards the camera) of one frame's depth on a
    `stride`-pixel grid; no points on depth edges (neighbours more than 6 % apart) or beyond max_depth."""
    run = ds.runs[n]
    K = np.asarray(run["K"], float)
    d = load_depth_mm(ds, root, n, r).astype(np.float64)
    v, u = np.mgrid[0:d.shape[0]:stride, 0:d.shape[1]:stride]
    z = d[v, u]
    P = np.stack([(u - K[0, 2]) / K[0, 0] * z, (v - K[1, 2]) / K[1, 1] * z, z], -1)
    ok = (z > 100) & (z < max_depth)
    N = np.cross(P[1:-1, 2:] - P[1:-1, :-2], P[2:, 1:-1] - P[:-2, 1:-1])
    norm = np.linalg.norm(N, axis=-1)
    zc = z[1:-1, 1:-1]
    good = (ok[1:-1, 1:-1] & ok[1:-1, 2:] & ok[1:-1, :-2] & ok[2:, 1:-1] & ok[:-2, 1:-1] & (norm > 0)
            & (np.abs(z[1:-1, 2:] - z[1:-1, :-2]) < 0.06 * zc) & (np.abs(z[2:, 1:-1] - z[:-2, 1:-1]) < 0.06 * zc))
    Pc = P[1:-1, 1:-1][good]
    Nc = (N / np.maximum(norm, 1e-9)[..., None])[good]
    Nc = Nc * -np.sign((Nc * Pc).sum(1, keepdims=True))
    return Pc, Nc


def icp(src, tgt, args, init=None):
    """Point-to-plane ICP from frame src to frame tgt (each (points, normals), camera frame, mm), starting at
    `init` (default identity: consecutive frames). -> (T_tgt_src or None, fitness, rmse): accepted if at least
    --icp-fitness of the source points end within --icp-dist mm of the target with an rmse of at most --icp-rmse mm."""
    Ps = src[0][:: max(1, len(src[0]) // 8000)]
    Pt, Nt = tgt
    if len(Ps) < 500 or len(Pt) < 500:
        return None, 0.0, float("inf")
    tree = cKDTree(Pt)
    T = np.eye(4) if init is None else init.copy()
    for dmax in (40, 40, 25, 25, 15, 15, 10, 10, 10, 10):
        X = Ps @ T[:3, :3].T + T[:3, 3]
        dist, j = tree.query(X, distance_upper_bound=dmax)
        m = np.isfinite(dist)
        if m.sum() < 300:
            return None, 0.0, float("inf")
        p, q, nq = X[m], Pt[j[m]], Nt[j[m]]
        A = np.hstack([np.cross(p, nq), nq])                    # n.(p + w x p + t - q) = 0, linearised
        x = np.linalg.lstsq(A, -((p - q) * nq).sum(1), rcond=None)[0]
        dT = np.eye(4)
        dT[:3, :3], dT[:3, 3] = Rotation.from_rotvec(x[:3]).as_matrix(), x[3:]
        T = dT @ T
    dist, _ = tree.query(Ps @ T[:3, :3].T + T[:3, 3], distance_upper_bound=args.icp_dist)
    m = np.isfinite(dist)
    fit = float(m.mean())
    rmse = float(np.sqrt((dist[m] ** 2).mean())) if m.any() else float("inf")
    return (T if fit >= args.icp_fitness and rmse <= args.icp_rmse else None), fit, rmse


def icp_extend(est, items, k0, step, n_max, cloud, args):
    """Chain depth ICP from mapped item k0 to its unmapped neighbours in one direction (step +-1) of the
    same scan, up to n_max frames or the first failure, gap or mapped frame. Returns the items added."""
    added, k = [], k0
    while len(added) < n_max:
        j = k + step
        if not 0 <= j < len(items) or items[j][0] != items[k][0] or abs(items[j][1] - items[k][1]) > 3 * args.every:
            break
        n, r = items[j]
        if np.isfinite(est[n][r]).all():
            break
        T, _, _ = icp(cloud(j), cloud(k), args)
        if T is None:
            break
        est[n][r] = est[items[k][0]][items[k][1]] @ T
        added.append(j)
        k = j
    return added


GRAPH_POINTS = np.vstack([np.zeros((1, 3)), VIEW])          # camera centre + view points (camera frame, mm)


def rinv(T):
    """Inverse of rigid poses (..., 4, 4)."""
    Ti = np.zeros_like(T)
    Rt = np.swapaxes(T[..., :3, :3], -1, -2)
    Ti[..., :3, :3], Ti[..., :3, 3], Ti[..., 3, 3] = Rt, -(Rt @ T[..., :3, 3, None])[..., 0], 1.0
    return Ti


def graph_edges(est, items, cloud, args):
    """Depth ICP between mapped frames --graph-offsets apart in the same scan, started from the map's relative
    pose. -> (i, j, Z (M, 4, 4) = measured T_i^-1 T_j). Pairs whose ICP result differs from the map's relative
    pose by more than --graph-check mm at the view points are dropped (wrong convergence)."""
    ok = lambda k: np.isfinite(est[items[k][0]][items[k][1]]).all()
    I, J, Z = [], [], []
    tried = {o: 0 for o in args.graph_offsets}
    kept = {o: 0 for o in args.graph_offsets}
    for k in sa.bar(range(len(items)), desc="graph edges", total=len(items)):
        if not ok(k):
            continue
        Tk = est[items[k][0]][items[k][1]]
        for o in args.graph_offsets:
            j = k + o
            if j >= len(items) or items[j][0] != items[k][0] or not ok(j) or items[j][1] - items[k][1] > 3 * o * args.every:
                continue
            tried[o] += 1
            rel = rinv(Tk) @ est[items[j][0]][items[j][1]]
            T, _, _ = icp(cloud(j), cloud(k), args, init=rel)
            if T is None or np.linalg.norm((T - rel)[:3, :3] @ VIEW.T + (T - rel)[:3, 3:], axis=0).mean() > args.graph_check:
                continue
            I.append(k), J.append(j), Z.append(T)
            kept[o] += 1
    print("graph edges (depth ICP, kept / tried): " + ", ".join(f"{o} frames apart {kept[o]}/{tried[o]}"
                                                                for o in args.graph_offsets), flush=True)
    return np.array(I, int), np.array(J, int), np.array(Z).reshape(-1, 4, 4)


def pose_graph(est, items, edges, args):
    """Pose graph over the room scan: the depth-ICP edges (exact local motion, --graph-edge-mm at the camera
    centre and view points) and each frame's map pose as a prior on its view points (--graph-prior-mm: the
    network fixes where the scene is, not the camera; it keeps the graph from drifting). Robust (soft L1)
    least squares; poses T_k = T0_k Exp(delta_k). Updates est in place."""
    from scipy.optimize import least_squares
    from scipy.sparse import coo_matrix
    idx = [k for k, (n, r) in enumerate(items) if np.isfinite(est[n][r]).all()]
    col = {k: c for c, k in enumerate(idx)}
    I, J, Z = edges
    keep = np.array([i in col and j in col for i, j in zip(I, J)], bool)
    ei = np.array([col[i] for i in I[keep]], int)
    ej = np.array([col[j] for j in J[keep]], int)
    Zinv = rinv(Z[keep])
    T0 = np.stack([est[items[k][0]][items[k][1]] for k in idx])
    V0 = view_points(T0)
    P = GRAPH_POINTS
    m, K = len(ei), len(idx)

    def poses(x):
        d = x.reshape(-1, 6)
        T = T0.copy()
        T[:, :3, :3] = T0[:, :3, :3] @ Rotation.from_rotvec(d[:, :3]).as_matrix()
        T[:, :3, 3] = T0[:, :3, 3] + (T0[:, :3, :3] @ d[:, 3:, None])[..., 0]
        return T

    def res(x):
        T = poses(x)
        E = Zinv @ rinv(T[ei]) @ T[ej]
        re = (np.einsum("nij,kj->nki", E[:, :3, :3], P) + E[:, None, :3, 3] - P) / args.graph_edge_mm
        rp = (view_points(T) - V0) / args.graph_prior_mm
        return np.concatenate([re.ravel(), rp.ravel()])

    ne, npr = 3 * len(P), 3 * len(VIEW)                       # residuals per edge, per prior
    r_e = np.broadcast_to(np.arange(ne * m).reshape(m, ne, 1), (m, ne, 12))
    c_e = np.broadcast_to(np.concatenate([6 * ei[:, None] + np.arange(6), 6 * ej[:, None] + np.arange(6)], 1)[:, None], (m, ne, 12))
    r_p = np.broadcast_to(ne * m + np.arange(npr * K).reshape(K, npr, 1), (K, npr, 6))
    c_p = np.broadcast_to((6 * np.arange(K))[:, None, None] + np.arange(6), (K, npr, 6))
    rows = np.concatenate([r_e.ravel(), r_p.ravel()])
    cols = np.concatenate([c_e.ravel(), c_p.ravel()])
    S = coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(ne * m + npr * K, 6 * K))
    edge_mm = lambda r: np.linalg.norm(r[: ne * m].reshape(m, len(P), 3), axis=2).mean(1) * args.graph_edge_mm
    prior_mm = lambda r: np.linalg.norm(r[ne * m:].reshape(K, len(VIEW), 3), axis=2).mean(1) * args.graph_prior_mm
    r0 = res(np.zeros(6 * K))
    print(f"pose graph: {K} poses, {m} edges; before: edges {np.median(edge_mm(r0)):.2f} mm median (ICP vs map)", flush=True)
    sol = least_squares(res, np.zeros(6 * K), jac_sparsity=S, method="trf", tr_solver="lsmr", loss="soft_l1",
                        f_scale=1.0, x_scale="jac", max_nfev=args.graph_iters, verbose=1)
    r1 = sol.fun
    print(f"pose graph: after: edges {np.median(edge_mm(r1)):.2f} / {np.percentile(edge_mm(r1), 90):.2f} mm, moved from "
          f"the network's view points {np.median(prior_mm(r1)):.1f} / {np.percentile(prior_mm(r1), 90):.1f} mm "
          f"(median / p90; {sol.nfev} evaluations)", flush=True)
    for c, T in enumerate(poses(sol.x)):
        n, r = items[idx[c]]
        est[n][r] = T


def run_graph(est, items, cloud, args, cache):
    """Edges + pose graph. With `cache` (a map's folder file: the edges depend on its poses), edges for the same
    offsets and ICP settings are read from it instead of computed again."""
    key = np.array([args.every, args.icp_stride, args.icp_dist, args.icp_fitness, args.icp_rmse, args.graph_check, *args.graph_offsets], float)
    if cache is not None and cache.exists() and np.array_equal(np.load(cache)["key"], key):
        z = np.load(cache)
        edges = (z["i"], z["j"], z["Z"])
        print(f"graph edges: {len(edges[0])} from {cache}", flush=True)
    else:
        edges = graph_edges(est, items, cloud, args)
        if cache is not None:
            np.savez(cache, key=key, i=edges[0], j=edges[1], Z=edges[2])
    pose_graph(est, items, edges, args)


class LocFrames(Dataset):
    """(item index, normalised RGB, depth mm) of room-scan frames, for localisation with workers."""

    def __init__(self, ds, root, items, idx):
        self.ds, self.root, self.items, self.idx = ds, root, items, idx

    def __len__(self):
        return len(self.idx)

    def __getitem__(self, j):
        k = self.idx[j]
        n, r = self.items[k]
        return k, torch.from_numpy(self.ds.load_frame(n, r)[0]).float(), \
            torch.from_numpy(load_depth_mm(self.ds, self.root, n, r).astype(np.float32))


# ---------------------------------------------------------------- the mapper

def fit(net, opt, scaler, data, steps, args, device, deltas=None, poses=None, fixed=None):
    """`steps` training steps on `data` (sampled with replacement). With `deltas` (an nn.Embedding of
    pose corrections), data returns camera-frame targets + item index and the labels are placed with
    poses[k] Exp(delta_k) (seed frame `fixed` kept at zero correction)."""
    dl = DataLoader(data, args.batch_size, sampler=RandomSampler(data, replacement=True, num_samples=steps * args.batch_size),
                    num_workers=args.workers, drop_last=True, pin_memory=device.type == "cuda")
    amp = device.type == "cuda"
    net.train()
    losses = []
    for batch in sa.bar(dl, desc="train", total=steps):
        rgb, tgt, ok = (x.to(device, non_blocking=True) for x in batch[:3])
        with torch.autocast(device.type, enabled=amp):
            pred = net(rgb)
        if deltas is not None:                # tgt: camera frame (m) -> map frame with the corrected pose
            k = batch[3].to(device)
            d = deltas(k)
            d = torch.where((k == fixed)[:, None], torch.zeros_like(d), d)
            T = poses[k]                                              # (B, 4, 4), m
            R = T[:, :3, :3] @ so3_exp(d[:, :3])
            t = T[:, :3, 3] + (T[:, :3, :3] @ d[:, 3:, None])[..., 0]
            tgt = torch.einsum("bij,bjhw->bihw", R, tgt) + t[:, :, None, None]
        err = torch.linalg.norm(pred.float() - tgt, dim=1)[ok]
        if err.numel() == 0:
            continue
        loss = err.mean()
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        losses.append(loss.item())
    return float(np.mean(losses)) * 1000 if losses else float("nan")


def plausible(T, T_ref, rows_apart, args, fps=30.0):
    """Is pose T reachable from T_ref in rows_apart frames (max speed and turn rate, plus a margin)?"""
    dt = abs(rows_apart) / fps
    d = np.linalg.norm(T[:3, 3] - T_ref[:3, 3])
    a = np.degrees(np.arccos(np.clip((np.trace(T_ref[:3, :3].T @ T[:3, :3]) - 1) / 2, -1, 1)))
    return d <= args.max_speed * dt + 20.0 and a <= args.max_turn * dt + 5.0


@torch.no_grad()
def localise(net, ds, root, items, idx, args, device, gates=None, refs=None, est=None):
    """({item index: (T map_cam, inliers)} for the frames in idx that pass their gate (gates[k], default
    --gate-far) and, with refs[k] = a mapped neighbour, the plausibility check; inliers of all)."""
    net.eval()
    ck = {"centre": np.zeros(3)}
    dl = DataLoader(LocFrames(ds, root, items, idx), batch_size=None, num_workers=args.workers)
    out, counts = {}, []
    for k, rgb, depth in sa.bar(dl, desc="localise", total=len(idx)):
        n, r = items[int(k)]
        run = ds.runs[n]
        T, inl = sa.localize_kabsch(net, ck, rgb.numpy(), depth.numpy(), np.asarray(run["K"], float), run["hw"][1],
                                    device, rng=np.random.default_rng(int(k)))
        counts.append(inl)
        k = int(k)
        if T is None or inl < (gates or {}).get(k, args.gate_far):
            continue
        if refs and k in refs and not plausible(T, est[items[refs[k]][0]][items[refs[k]][1]],
                                                items[k][1] - items[refs[k]][1], args):
            continue
        out[k] = (T, inl)
    return out, counts


def write_outputs(args, out, items, est, gt, history, stage, net, mapping_args=None):
    """Align the map to Polaris (view points), write poses_<scan>.json (labels for scr_anchor.py train
    --label-poses), map.json, map_report.md and, after mapping, map.pt (the mapping network). With `stage`,
    the final errors are added to the history under that name (--realign)."""
    A, e, X = map_errors(est, gt, items, calib=args.cam_calib)
    if A is None:
        raise SystemExit("the map did not grow beyond the seed: train the seed longer (--seed-steps) or lower --gate")
    if stage:
        history = history + [{"stage": stage, "added": None, "loss_mm": None, **e}]
    if net is not None:
        torch.save({"model": net.state_dict(), "centre": [0.0, 0.0, 0.0], "head": "big", "image_size": [360, 640],
                    "args": {"hand_eye": args.hand_eye}, "map_to_polaris": A.tolist()}, out / "map.pt")
    for n in args.scan_runs:
        rows = [r for m, r in items if m == n and np.isfinite(est[n][r]).all()]
        json.dump({"run": n, "source": f"scr-map ({out.name})",
                   "note": "map poses after one rigid alignment to Polaris (map_to_polaris in map.json)",
                   "frames": [{"row": int(r), "T_world_cam_pred": (A @ est[n][r]).tolist()} for r in rows]},
                  open(out / f"poses_{n}.json", "w"))
    json.dump({"args": mapping_args or vars(args), "history": history, "final": e, "map_to_polaris": A.tolist(),
               "cam_calib": X.tolist(),
               **({"rerun_args": vars(args)} if mapping_args else {})}, open(out / "map.json", "w"), indent=1)
    f = lambda v: "-" if v is None else f"{v:.1f}"
    md = [f"# Map without a tracker: {', '.join(args.scan_runs)} ({Path(args.root).name})", "",
          "Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of "
          "the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training "
          "labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).", "",
          "| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg "
          "| 1 s motion mm (median / p90) | loss mm |",
          "|---|---|---|---|---|---|---|---|"]
    md += [f"| {h['stage']}{' (+ camera calibration)' if 'calib_mm' in h else ''} | {h['added'] if h['added'] is not None else ''} | {h['mapped']}/{h['frames']} ({h['mapped_pct']:.0f} %) | "
           f"{f(h.get('view_mm_median'))} / {f(h.get('view_mm_p90'))} | {f(h['pos_mm_median'])} / {f(h['pos_mm_p90'])} | "
           f"{h['rot_deg_median']:.2f} | {f(h['rel1s_mm_median'])} / {f(h['rel1s_mm_p90'])} | "
           f"{'' if h.get('loss_mm') is None else format(h['loss_mm'], '.1f')} |" for h in history]
    if any("view_mm_median" not in h for h in history):
        md += ["", "Stages without scene-point errors were aligned on camera positions only (before 3 Nov): their "
               "rotation and position errors include an alignment error."]
    if "calib_mm" in e:
        md += ["", f"Camera calibration from the room scan (one fixed camera-frame transform, a property of the probe; "
               f"Polaris sees the marker, the map the camera): {e['calib_mm']:.1f} mm, {e['calib_deg']:.2f} deg. Rows marked "
               "(+ camera calibration) include it. It is not in the labels; `scr_anchor.py track --cam-calib "
               f"{out / 'map.json'}` applies it when placing the US images."]
    md += ["", "Labels for training: " + ", ".join(f"`poses_{n}.json`" for n in args.scan_runs) +
           " (`scr_anchor.py train --label-poses`)."]
    (out / "map_report.md").write_text("\n".join(md) + "\n")
    print("\n".join(md[4:]) + f"\n-> {out}", flush=True)



def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--scan-runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--every", type=int, default=1, help="use every n-th usable row of the scans")
    ap.add_argument("--seed-run", default=None, help="run of the seed frame (default: the first scan run)")
    ap.add_argument("--seed-row", type=int, default=None, help="row of the seed frame (default: its first usable row)")
    ap.add_argument("--seed-seconds", type=float, default=2.0, help="seed: frames this far before / after the seed frame, by depth ICP")
    ap.add_argument("--seed-steps", type=int, default=2000, help="training steps on the seed frames")
    ap.add_argument("--icp-extend", type=int, default=90, help="per round, depth ICP extends each map edge by up to this many frames (0 = off)")
    ap.add_argument("--icp-stride", type=int, default=4, help="depth ICP: pixel grid of the point clouds")
    ap.add_argument("--icp-dist", type=float, default=10.0, help="depth ICP: inlier distance (mm)")
    ap.add_argument("--icp-fitness", type=float, default=0.5, help="depth ICP: minimum share of inliers")
    ap.add_argument("--icp-rmse", type=float, default=6.0, help="depth ICP: maximum inlier rmse (mm)")
    ap.add_argument("--round-steps", type=int, default=1500, help="training steps per round")
    ap.add_argument("--max-rounds", type=int, default=40)
    ap.add_argument("--reach", type=int, default=150,
                    help="candidates: unmapped frames within this many (used) rows of a mapped one in the same scan")
    ap.add_argument("--probe-every", type=int, default=30, help="candidates: also every n-th other unmapped frame")
    ap.add_argument("--min-growth", type=float, default=0.005, help="stop when a round adds less than this share")
    ap.add_argument("--gate", type=int, default=60, help="minimum inliers to join next to a mapped frame (with the check)")
    ap.add_argument("--gate-far", type=int, default=400, help="minimum inliers without a mapped neighbour, and in the final pass")
    ap.add_argument("--max-speed", type=float, default=500.0, help="plausibility check: camera speed (mm/s)")
    ap.add_argument("--max-turn", type=float, default=90.0, help="plausibility check: turn rate (deg/s)")
    ap.add_argument("--no-final-pass", dest="final_pass", action="store_false",
                    help="skip re-localising every frame before the refinement")
    ap.add_argument("--refine-steps", type=int, default=0,
                    help="joint training of the network and pose corrections (off: on 3XX it made the map worse)")
    ap.add_argument("--realign", action="store_true",
                    help="no mapping: re-align the map in --out (or --from, written to --out): its poses_*.json and map.json")
    ap.add_argument("--no-cam-calib", dest="cam_calib", action="store_false",
                    help="evaluate without the camera calibration (one fixed camera-frame transform fitted with the alignment)")
    ap.add_argument("--no-graph", dest="graph", action="store_false",
                    help="skip the pose graph (depth-ICP edges between nearby frames + the network's poses) after the final pass")
    ap.add_argument("--from", dest="from_map", default=None,
                    help="no mapping: run the pose graph on the map in this folder (e.g. runs/map-3XX) and write the result to --out")
    ap.add_argument("--graph-offsets", type=int, nargs="+", default=[1, 5, 15, 30], help="pose graph: ICP edges between frames this many apart")
    ap.add_argument("--graph-edge-mm", type=float, default=1.0, help="pose graph: ICP edge uncertainty at the camera centre and view points (mm)")
    ap.add_argument("--graph-prior-mm", type=float, default=10.0, help="pose graph: uncertainty of the network's view points (mm)")
    ap.add_argument("--graph-check", type=float, default=50.0, help="pose graph: drop ICP edges this far from the map's relative pose (mm)")
    ap.add_argument("--graph-iters", type=int, default=300, help="pose graph: maximum least-squares evaluations")
    ap.add_argument("--refine-lr", type=float, default=1e-4, help="pose corrections (rad, m)")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-3, help="head")
    ap.add_argument("--lr-encoder", type=float, default=1e-4)
    ap.add_argument("--label-max-depth", type=float, default=2000.0)
    ap.add_argument("--hand-eye", default=str(sa.REPO / "T_marker_cam.npy"), help="for the Polaris evaluation only")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-frames", type=int, default=0, help="smoke tests only")
    args = ap.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(args.seed)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cfg = RPRConfig(T_marker_cam=load_hand_eye(sa.resolve_hand_eye(args.hand_eye), "mm"))
    ds = RPRDataset(args.root, args.scan_runs, args.scan_runs, cfg)
    items = [(n, int(r)) for n in args.scan_runs for r in np.concatenate(ds.runs[n]["segments"])[:: args.every]]
    if args.max_frames:
        items = items[: args.max_frames]
    gt = {n: ds.runs[n]["T_world_cam"].copy() for n in args.scan_runs}            # evaluation only
    est = {n: np.full_like(gt[n], np.nan) for n in args.scan_runs}
    for n in args.scan_runs:
        ds.runs[n]["T_world_cam"] = est[n]                                         # labels come from the map
    clouds = {}

    def cloud(k):                             # depth clouds, cached (ICP touches each frame a few times)
        if k not in clouds:
            if len(clouds) > 400:
                clouds.clear()
            clouds[k] = depth_cloud(ds, args.root, *items[k], args.icp_stride, args.label_max_depth)
        return clouds[k]

    if args.realign or args.from_map:         # the map of an earlier run: est = inverse of its old alignment x its poses
        src = Path(args.from_map) if args.from_map else out
        old = json.load(open(src / "map.json"))
        A_old = np.asarray(old["map_to_polaris"])
        for n in args.scan_runs:
            for f in json.load(open(src / f"poses_{n}.json"))["frames"]:
                est[n][f["row"]] = np.linalg.inv(A_old) @ np.asarray(f["T_world_cam_pred"])
        if args.realign:                      # with --from: the map of --from, written to --out
            write_outputs(args, out, items, est, gt, old["history"], "re-aligned", None, mapping_args=old["args"])
            return
        run_graph(est, items, cloud, args, src / "graph_edges.npz")
        write_outputs(args, out, items, est, gt, old["history"], f"pose graph (from {src.name})", None, mapping_args=old["args"])
        return
    pos = {it: k for k, it in enumerate(items)}
    seed_run = args.seed_run or args.scan_runs[0]
    seed = pos[(seed_run, args.seed_row)] if args.seed_row is not None else next(k for k, (n, _) in enumerate(items) if n == seed_run)
    est[items[seed][0]][items[seed][1]] = np.eye(4)
    print(f"{len(items)} room-scan frames from {', '.join(args.scan_runs)}; seed {items[seed]} = map origin", flush=True)

    n_seed = int(round(args.seed_seconds * 30 / args.every))
    seed_icp = icp_extend(est, items, seed, 1, n_seed, cloud, args) + icp_extend(est, items, seed, -1, n_seed, cloud, args)
    print(f"seed: {1 + len(seed_icp)} frames by depth ICP around the seed (up to {args.seed_seconds:g} s each way)", flush=True)

    net = sa.build_net("big").to(device)
    encoder = list(net.low.parameters()) + list(net.high.parameters())
    opt = torch.optim.AdamW([{"params": encoder, "lr": args.lr_encoder}, {"params": net.head.parameters(), "lr": args.lr}],
                            weight_decay=1e-4)
    scaler = torch.amp.GradScaler(enabled=device.type == "cuda")
    mapped = lambda: [k for k, (n, r) in enumerate(items) if np.isfinite(est[n][r]).all()]
    frames = lambda idx: sa.Frames(ds, args.root, [items[k] for k in idx], np.zeros(3), max_depth=args.label_max_depth,
                                   drop_edges=True, seed=args.seed)
    history = []

    def log(stage, loss, t0, added=None):
        _, e, _ = map_errors(est, gt, items, calib=args.cam_calib)
        if not e:
            print(f"{stage}: +{added} frames, fewer than 3 mapped", flush=True)
            return
        h = {"stage": stage, "loss_mm": loss, "added": added, "s": round(time.time() - t0), **e}
        history.append(h)
        f = lambda v: "-" if v is None else f"{v:.1f}"
        print(f"{stage}: loss {loss:.1f} mm, +{added if added is not None else 0} frames, mapped {e['mapped']}/{e['frames']} "
              f"({e['mapped_pct']:.0f} %); vs Polaris after one rigid alignment: scene points at 1 m "
              f"{f(e['view_mm_median'])} / {f(e['view_mm_p90'])} mm, camera position {f(e['pos_mm_median'])} / "
              f"{f(e['pos_mm_p90'])} mm, rotation {e['rot_deg_median']:.2f} deg, 1 s motion {f(e['rel1s_mm_median'])} mm "
              f"[{h['s']} s]", flush=True)
        json.dump({"args": vars(args), "history": history}, open(out / "map.json", "w"), indent=1)

    # rounds: train on the map, localise candidates, grow
    t0 = time.time()
    loss = fit(net, opt, scaler, frames(mapped()), args.seed_steps, args, device)
    print(f"seed: {args.seed_steps} steps on the seed frames, loss {loss:.1f} mm", flush=True)
    for rnd in range(args.max_rounds):
        have = set(mapped())
        refs = {}                                                  # unmapped frame -> nearest mapped one, same run
        for k in sorted(have):
            n, _ = items[k]
            for j in range(max(0, k - args.reach), min(len(items), k + args.reach + 1)):
                if items[j][0] == n and j not in have and (j not in refs or abs(j - k) < abs(j - refs[j])):
                    refs[j] = k
        far = [j for j in range(len(items)) if j not in have and j not in refs][:: args.probe_every]
        cand = sorted(set(refs) | set(far))
        if not cand:
            break
        got, counts = localise(net, ds, args.root, items, cand, args, device,
                               gates={j: args.gate for j in refs}, refs=refs, est=est)
        for k, (T, _) in got.items():
            est[items[k][0]][items[k][1]] = T
        by_icp = []
        if args.icp_extend:                   # depth ICP from every edge of the map
            for k in mapped():
                for step in (1, -1):
                    j = k + step
                    if 0 <= j < len(items) and items[j][0] == items[k][0] and not np.isfinite(est[items[j][0]][items[j][1]]).all():
                        by_icp += icp_extend(est, items, k, step, args.icp_extend, cloud, args)
        print(f"round {rnd + 1}: network {len(got)} of {len(cand)} candidates (inliers median {np.median(counts):.0f}, "
              f"p90 {np.percentile(counts, 90):.0f}); depth ICP {len(by_icp)} more", flush=True)
        added = len(got) + len(by_icp)
        log(f"round {rnd + 1}", loss, t0, added)
        if added < args.min_growth * len(items) or len(mapped()) == len(items):
            break
        loss = fit(net, opt, scaler, frames(mapped()), args.round_steps, args, device)

    if len(mapped()) < 3:
        raise SystemExit("the map did not grow beyond the seed: check the 'seed:' and 'round' lines above")

    # final pass: every frame again with the last network, strict gate
    if args.final_pass:
        got, counts = localise(net, ds, args.root, items, list(range(len(items))), args, device)
        for k, (T, _) in got.items():
            if k != seed:
                est[items[k][0]][items[k][1]] = T
        print(f"final pass: {len(got)} of {len(items)} frames passed (inliers median {np.median(counts):.0f})", flush=True)
        log("final pass", loss, t0, len(got))

    # refine: network + per-frame pose corrections, seed fixed
    idx = mapped()
    if args.refine_steps and len(idx) > 1:
        data = sa.Frames(ds, args.root, [items[k] for k in idx], np.zeros(3), max_depth=args.label_max_depth,
                         drop_edges=True, seed=args.seed, camera_frame=True)
        P = np.stack([est[items[k][0]][items[k][1]] for k in idx])
        P[:, :3, 3] /= 1000.0                                                      # mm -> m
        poses = torch.from_numpy(P).float().to(device)
        deltas = torch.nn.Embedding(len(idx), 6).to(device)
        torch.nn.init.zeros_(deltas.weight)
        opt.add_param_group({"params": deltas.parameters(), "lr": args.refine_lr, "weight_decay": 0.0})
        loss = fit(net, opt, scaler, data, args.refine_steps, args, device, deltas=deltas, poses=poses,
                   fixed=idx.index(seed))
        with torch.no_grad():
            d = deltas.weight.clone()
            d[idx.index(seed)] = 0
            R = so3_exp(d[:, :3]).cpu().numpy()
            dt = d[:, 3:].cpu().numpy() * 1000.0
        for j, k in enumerate(idx):
            T = est[items[k][0]][items[k][1]]
            C = np.eye(4)
            C[:3, :3], C[:3, 3] = R[j], dt[j]
            est[items[k][0]][items[k][1]] = T @ C
        log("refined", loss, t0, 0)

    if args.graph:
        run_graph(est, items, cloud, args, None)
        log("pose graph", loss, t0, 0)

    write_outputs(args, out, items, est, gt, history, None, net)


if __name__ == "__main__":
    main()
