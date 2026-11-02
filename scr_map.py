"""
Map a room without a tracker: the SCR network builds the room-scan poses itself (ACE0-style, Brachmann
et al. 2024, here with the measured depth). The poses it writes replace Polaris as the training labels,
so the whole system needs no tracker; Polaris is used only to evaluate the map.

  1. seed: one room-scan frame defines the map frame (identity pose);
  2. rounds: train the network on the frames mapped so far (labels: their depth placed with their
     poses), then localise unmapped frames with it (Kabsch RANSAC on the depth). Candidates: unmapped
     frames within --reach rows of a mapped frame of the same run (join with >= --gate inliers, if the
     pose is plausible given that frame: <= --max-speed mm/s and --max-turn deg/s plus a margin), and
     every --probe-every-th other unmapped frame (join with >= --gate-far inliers; other scans of the
     room join this way). Stops when a round adds fewer than --min-growth of the frames;
  3. final pass: every frame localised again with the last network (>= --gate-far inliers), replacing
     the rough early poses; then refine (--refine-steps): the network and a pose correction per mapped
     frame trained jointly (T_k <- T_k Exp(delta_k), seed frame fixed), so pose errors are corrected
     instead of learned;
  4. evaluate against Polaris after one rigid alignment of the whole map (positions, Kabsch): camera
     position / rotation error per frame and the error of 1 s relative motions (local consistency);
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


def align(P, Q):
    """Rigid A (4x4) with A P ~ Q for point sets (N, 3) (Kabsch, no scale)."""
    R, t = sa.kabsch(P, Q)
    A = np.eye(4)
    A[:3, :3], A[:3, 3] = R, t
    return A


def map_errors(est, gt, items, rows_per_s=30):
    """Map vs Polaris after one rigid alignment of all mapped camera positions: per-frame position /
    rotation error, and the error of relative motions over 1 s (local consistency)."""
    ok = [k for k, (n, r) in enumerate(items) if np.isfinite(est[n][r]).all()]
    if len(ok) < 3:
        return None, {}
    Te = np.stack([est[items[k][0]][items[k][1]] for k in ok])
    Tg = np.stack([gt[items[k][0]][items[k][1]] for k in ok])
    A = align(Te[:, :3, 3], Tg[:, :3, 3])
    Ta = A @ Te
    dt = np.linalg.norm(Ta[:, :3, 3] - Tg[:, :3, 3], axis=1)
    dR = np.einsum("nji,njk->nik", Ta[:, :3, :3], Tg[:, :3, :3])
    dr = np.degrees(np.arccos(np.clip((np.trace(dR, axis1=1, axis2=2) - 1) / 2, -1, 1)))
    rel = []
    for n in {n for n, _ in items}:                              # 1 s relative motions within a run
        rows = sorted(r for m, r in items if m == n and np.isfinite(est[n][r]).all())
        have = set(rows)
        for r in rows:
            if r + rows_per_s in have:
                Re = np.linalg.inv(est[n][r]) @ est[n][r + rows_per_s]
                Rg = np.linalg.inv(gt[n][r]) @ gt[n][r + rows_per_s]
                rel.append(np.linalg.norm(Re[:3, 3] - Rg[:3, 3]))
    q = lambda v, p: float(np.percentile(v, p)) if len(v) else None
    return A, {"mapped": len(ok), "frames": len(items), "mapped_pct": 100 * len(ok) / len(items),
               "pos_mm_median": q(dt, 50), "pos_mm_p90": q(dt, 90), "rot_deg_median": q(dr, 50),
               "rel1s_mm_median": q(rel, 50), "rel1s_mm_p90": q(rel, 90)}


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


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--scan-runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--every", type=int, default=1, help="use every n-th usable row of the scans")
    ap.add_argument("--seed-run", default=None, help="run of the seed frame (default: the first scan run)")
    ap.add_argument("--seed-row", type=int, default=None, help="row of the seed frame (default: its first usable row)")
    ap.add_argument("--seed-steps", type=int, default=2000, help="training steps on the seed frame alone")
    ap.add_argument("--round-steps", type=int, default=1500, help="training steps per round")
    ap.add_argument("--max-rounds", type=int, default=40)
    ap.add_argument("--reach", type=int, default=150,
                    help="candidates: unmapped frames within this many (used) rows of a mapped one in the same scan")
    ap.add_argument("--probe-every", type=int, default=30, help="candidates: also every n-th other unmapped frame")
    ap.add_argument("--min-growth", type=float, default=0.005, help="stop when a round adds less than this share")
    ap.add_argument("--gate", type=int, default=150, help="minimum inliers to join next to a mapped frame (with the check)")
    ap.add_argument("--gate-far", type=int, default=400, help="minimum inliers without a mapped neighbour, and in the final pass")
    ap.add_argument("--max-speed", type=float, default=500.0, help="plausibility check: camera speed (mm/s)")
    ap.add_argument("--max-turn", type=float, default=90.0, help="plausibility check: turn rate (deg/s)")
    ap.add_argument("--no-final-pass", dest="final_pass", action="store_false",
                    help="skip re-localising every frame before the refinement")
    ap.add_argument("--refine-steps", type=int, default=4000, help="joint training of the network and pose corrections")
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
    pos = {it: k for k, it in enumerate(items)}
    seed_run = args.seed_run or args.scan_runs[0]
    seed = pos[(seed_run, args.seed_row)] if args.seed_row is not None else next(k for k, (n, _) in enumerate(items) if n == seed_run)
    est[items[seed][0]][items[seed][1]] = np.eye(4)
    print(f"{len(items)} room-scan frames from {', '.join(args.scan_runs)}; seed {items[seed]} = map origin", flush=True)

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
        _, e = map_errors(est, gt, items)
        if not e:
            print(f"{stage}: +{added} frames, fewer than 3 mapped", flush=True)
            return
        h = {"stage": stage, "loss_mm": loss, "added": added, "s": round(time.time() - t0), **e}
        history.append(h)
        f = lambda v: "-" if v is None else f"{v:.1f}"
        print(f"{stage}: loss {loss:.1f} mm, +{added if added is not None else 0} frames, mapped {e['mapped']}/{e['frames']} "
              f"({e['mapped_pct']:.0f} %); vs Polaris after one rigid alignment: position {f(e['pos_mm_median'])} / "
              f"{f(e['pos_mm_p90'])} mm, rotation {e['rot_deg_median']:.2f} deg, 1 s motion {f(e['rel1s_mm_median'])} mm "
              f"[{h['s']} s]", flush=True)
        json.dump({"args": vars(args), "history": history}, open(out / "map.json", "w"), indent=1)

    # rounds: train on the map, localise candidates, grow
    t0 = time.time()
    loss = fit(net, opt, scaler, frames(mapped()), args.seed_steps, args, device)
    print(f"seed: {args.seed_steps} steps on the seed frame, loss {loss:.1f} mm", flush=True)
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
        print(f"round {rnd + 1}: {len(got)} of {len(cand)} candidates joined (inliers median {np.median(counts):.0f}, "
              f"p90 {np.percentile(counts, 90):.0f})", flush=True)
        log(f"round {rnd + 1}", loss, t0, len(got))
        if len(got) < args.min_growth * len(items) or len(mapped()) == len(items):
            break
        loss = fit(net, opt, scaler, frames(mapped()), args.round_steps, args, device)

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

    # aligned poses for scr_anchor.py train --label-poses; report
    A, e = map_errors(est, gt, items)
    if A is None:
        raise SystemExit("the map did not grow beyond the seed: train the seed longer (--seed-steps) or lower --gate")
    torch.save({"model": net.state_dict(), "centre": [0.0, 0.0, 0.0], "head": "big", "image_size": [360, 640],
                "args": {"hand_eye": args.hand_eye}, "map_to_polaris": A.tolist()}, out / "map.pt")
    for n in args.scan_runs:
        rows = [r for m, r in items if m == n and np.isfinite(est[n][r]).all()]
        json.dump({"run": n, "source": f"scr-map ({out.name})",
                   "note": "map poses after one rigid alignment to Polaris (map_to_polaris in map.json)",
                   "frames": [{"row": int(r), "T_world_cam_pred": (A @ est[n][r]).tolist()} for r in rows]},
                  open(out / f"poses_{n}.json", "w"))
    json.dump({"args": vars(args), "history": history, "final": e, "map_to_polaris": A.tolist()},
              open(out / "map.json", "w"), indent=1)
    f = lambda v: "-" if v is None else f"{v:.1f}"
    md = [f"# Map without a tracker: {', '.join(args.scan_runs)} ({Path(args.root).name})", "",
          "The SCR network built the room-scan poses from one seed frame (scr_map.py). Error against Polaris after one "
          "rigid alignment of the whole map; 1 s motion = error of the relative pose between frames 30 rows apart.", "",
          "| stage | frames added | mapped | position mm (median / p90) | rotation deg | 1 s motion mm (median / p90) | loss mm |",
          "|---|---|---|---|---|---|---|"]
    md += [f"| {h['stage']} | {h['added'] if h['added'] is not None else ''} | {h['mapped']}/{h['frames']} ({h['mapped_pct']:.0f} %) | "
           f"{f(h['pos_mm_median'])} / {f(h['pos_mm_p90'])} | {h['rot_deg_median']:.2f} | {f(h['rel1s_mm_median'])} / "
           f"{f(h['rel1s_mm_p90'])} | {h['loss_mm']:.1f} |" for h in history]
    md += ["", "Labels for training: " + ", ".join(f"`poses_{n}.json`" for n in args.scan_runs) +
           " (`scr_anchor.py train --label-poses`)."]
    (out / "map_report.md").write_text("\n".join(md) + "\n")
    print("\n".join(md[4:]) + f"\n-> {out}", flush=True)


if __name__ == "__main__":
    main()
