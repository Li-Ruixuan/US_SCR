"""
Why does a changed room break the anchors? Gradient attribution and a masking test for the
anchor network, on the (keyframe, frame) pairs of an `anchoring.py evaluate` result.

Per pair (room-scan keyframe k, sweep frame q, as used for an anchor):
  1. Changed pixels of q (true poses + depth, no labels): every pixel of q with depth is moved
     into the keyframe with T_k^-1 T_q and compared with the keyframe's depth there.
       same      depth agrees (within max(--tol-mm, --tol-rel * depth))
       changed   depth disagrees: something moved, appeared or disappeared (also parallax
                 occlusion, which is small for the short keyframe distances in use)
       not seen  outside the keyframe image or no keyframe depth there
  2. Attribution: the pair's error (|predicted - true| translation part of xi, mm) is
     backpropagated to the input images (weights fixed); |gradient x input| summed over the
     RGB channels and the depth channel gives a map over q. "Look ratio" = share of the
     attribution on changed pixels / share of changed pixels (> 1: the network looks at the
     changed parts more than their area).
  3. Masking test: the changed pixels of q are blanked (RGB to the ImageNet mean, depth
     invalid) and the pair predicted again; control: the same mask shifted to another place.
     If blanking the changed pixels lowers the error clearly more than the control, the
     changed objects are what misleads the network.

Writes <out>/saliency.json (per pair), <out>/saliency.md (summary) and overlay images of the
best and worst pairs (keyframe | frame with changed pixels in magenta | attribution).

Scene change (3XX sweeps, 2XX room scan) and its control (3XX sweeps, own room scan):
  python tools/anchor_saliency.py --eval runs/anchoring-final/anchor_eval_anchor-rgbd-e20-odometry-train_3XX.json \\
      --out runs/saliency/3XX_2XXmap
  python tools/anchor_saliency.py --eval runs/anchoring-final/anchor_eval_anchor-rgbd-e20-odometry-train_3XX-map-room-301+room-302.json \\
      --out runs/saliency/3XX_ownmap
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
from anchoring import anchor_net, load_depth                    # noqa: E402
from dataloader import IMAGENET_MEAN, IMAGENET_STD, RPRConfig, RPRDataset  # noqa: E402
from eval import load_val_set                                    # noqa: E402
from geometry import invert_se3                                  # noqa: E402
from trajectory import gt_chains                                 # noqa: E402

NO_DEPTH, SAME, CHANGED, NOT_SEEN = 0, 1, 2, 3


def change_labels(dq, T_q, dk, T_k, K, dmin, dmax, tol_mm, tol_rel):
    """(H, W) label per pixel of q: NO_DEPTH / SAME / CHANGED / NOT_SEEN (depth in mm)."""
    H, W = dq.shape
    v, u = np.mgrid[0:H, 0:W]
    z = dq.ravel()
    X = np.stack([(u.ravel() - K[0, 2]) / K[0, 0] * z, (v.ravel() - K[1, 2]) / K[1, 1] * z, z, np.ones_like(z)])
    Y = (invert_se3(T_k) @ T_q @ X)[:3]
    zf = np.maximum(Y[2], 1)
    uk = np.round(K[0, 0] * Y[0] / zf + K[0, 2]).astype(int)
    vk = np.round(K[1, 1] * Y[1] / zf + K[1, 2]).astype(int)
    inside = (Y[2] > dmin) & (uk >= 0) & (uk < W) & (vk >= 0) & (vk < H)
    zk = np.zeros_like(z)
    zk[inside] = dk[vk[inside], uk[inside]]
    seen = inside & (zk > dmin) & (zk < dmax)
    agree = np.abs(zk - Y[2]) <= np.maximum(tol_mm, tol_rel * Y[2])
    lab = np.full(z.shape, NOT_SEEN)
    lab[seen & agree] = SAME
    lab[seen & ~agree] = CHANGED
    lab[~((z > dmin) & (z < dmax))] = NO_DEPTH
    return lab.reshape(H, W)


def pair_error(net, fk, fq, xg, mean, std, device, grad=False):
    """Translation error (mm) of the pair prediction; with grad, also the attribution map over q."""
    rgb = torch.from_numpy(np.stack([fk[0], fq[0]])[None]).float().to(device).requires_grad_(grad)
    dep = torch.from_numpy(np.stack([fk[1], fq[1]])[None]).float().to(device).requires_grad_(grad)
    msk = torch.from_numpy(np.stack([fk[2], fq[2]])[None]).float().to(device)
    with torch.set_grad_enabled(grad):
        xp = net(rgb=rgb, depth=dep, depth_mask=msk)["xi"].view(6).double() * std + mean
        err = torch.linalg.norm(xp[:3] - xg[:3])
    if not grad:
        return err.item(), None
    err.backward()
    att = (rgb.grad * rgb).abs().sum(2)[0, 1] + (dep.grad * dep).abs().sum(2)[0, 1]
    return err.item(), att.detach().cpu().numpy()


def blank(f, m):
    """Frame f = (rgb, depth, mask) with the pixels of m blanked: RGB to the ImageNet mean
    (0 after normalisation), depth invalid."""
    rgb, dep, msk = f[0].copy(), f[1].copy(), f[2].copy()
    rgb[:, m] = 0
    dep[:, m] = 0
    msk[:, m] = False
    return rgb, dep, msk


def to_bgr(rgb):
    x = rgb.transpose(1, 2, 0) * IMAGENET_STD + IMAGENET_MEAN
    return cv2.cvtColor((np.clip(x, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)


def overlay(fk, fq, lab, att, title):
    k, q = to_bgr(fk[0]), to_bgr(fq[0])
    ch = q.copy()
    ch[lab == CHANGED] = (0.4 * ch[lab == CHANGED] + 0.6 * np.array([255, 0, 255])).astype(np.uint8)
    ch[lab == NOT_SEEN] = (0.5 * ch[lab == NOT_SEEN]).astype(np.uint8)
    a = cv2.GaussianBlur(att, (0, 0), 4)
    a = np.clip(a / (np.percentile(a, 99.5) + 1e-12), 0, 1)
    heat = cv2.addWeighted(q, 0.45, cv2.applyColorMap((a * 255).astype(np.uint8), cv2.COLORMAP_INFERNO), 0.55, 0)
    for img, t in ((k, "room-scan keyframe"), (ch, "frame: changed (magenta), not seen (dark)"), (heat, "attribution of the error")):
        cv2.putText(img, t, (8, 22), 0, 0.6, (255, 255, 255), 2)
    row = np.hstack([k, ch, heat])
    bar = np.zeros((30, row.shape[1], 3), np.uint8)
    cv2.putText(bar, title, (8, 21), 0, 0.6, (255, 255, 255), 1)
    return np.vstack([bar, row])


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1]) if len(a) > 2 else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", required=True, help="anchor_eval_*.json of anchoring.py evaluate")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-anchors", type=int, default=150, help="anchors used, spread over all (0: all)")
    ap.add_argument("--pairs-per-anchor", type=int, default=3, help="keyframes per anchor (up to k)")
    ap.add_argument("--tol-mm", type=float, default=30.0)
    ap.add_argument("--tol-rel", type=float, default=0.03)
    ap.add_argument("--shift-px", type=int, default=120, help="shift of the control mask")
    ap.add_argument("--images", type=int, default=6, help="overlays of the best and of the worst pairs")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    E = json.load(open(args.eval))
    ea = E["args"]
    map_root, map_scans = ea["map_root"] or ea["root"], ea["map_scans"] or ea["scan_runs"]
    ack = torch.load(ea["ckpts"][0], map_location=device, weights_only=False)
    a = ack["args"]
    mean = torch.as_tensor(ack["target_mean"], dtype=torch.float64, device=device)
    std = torch.as_tensor(ack["target_std"], dtype=torch.float64, device=device)
    ock = torch.load(Path(ea["odometry"]) / f"fold{a['fold']}" / "best.pt", map_location="cpu", weights_only=False)
    ds_val, T_mc, val_runs = load_val_set(ock, ea["test_root"], ea["test_runs"])
    chains = gt_chains(ds_val)
    cfg = RPRConfig(T_marker_cam=T_mc, use_depth=a["use_depth"], image_size=tuple(a["image_size"]))
    base_map = RPRDataset(map_root, map_scans, map_scans, cfg)
    test_root = ea["test_root"] or ea["root"]
    base = RPRDataset(test_root, val_runs, [], cfg)
    net = anchor_net(a, pretrained=False).to(device)
    net.load_state_dict(ack["model"])
    net.eval()
    H, W = cfg.image_size

    def net_depth(ds, root, name, row):
        """Aligned depth (mm) on the network grid, and K scaled to it."""
        d = load_depth(name, row, ds.runs, root)
        K = np.array(ds.runs[name]["K"], float).copy()
        K[0] *= W / d.shape[1]
        K[1] *= H / d.shape[0]
        return cv2.resize(d, (W, H), interpolation=cv2.INTER_NEAREST), K

    rows = E["anchors"]
    if args.max_anchors and len(rows) > args.max_anchors:
        rows = [rows[i] for i in np.linspace(0, len(rows) - 1, args.max_anchors).round().astype(int)]
    print(f"{len(rows)} anchors x up to {args.pairs_per_anchor} keyframes | map {map_root}: {'+'.join(map_scans)} | "
          f"sweeps {test_root} | anchor net {ea['ckpts'][0]}")

    res, pics = [], []
    for n_a, r in enumerate(rows):
        c = chains[(r["run"], r["segment"])]
        row_q, T_q = int(c["frames"][r["index"]]), c["T_gt"][r["index"]]
        fq = base.load_frame(r["run"], row_q)
        dq, K = net_depth(base, test_root, r["run"], row_q)
        for j, kf in enumerate(r["keyframes"][: args.pairs_per_anchor]):
            kn, kr = kf.rsplit(":", 1)
            kr = int(kr)
            fk = base_map.load_frame(kn, kr)
            dk, _ = net_depth(base_map, map_root, kn, kr)
            T_k = base_map.runs[kn]["T_world_cam"][kr]
            lab = change_labels(dq, T_q, dk, T_k, K, cfg.min_depth, cfg.max_depth, args.tol_mm, args.tol_rel)
            xg = torch.as_tensor(r["xi_gt"][j], dtype=torch.float64, device=device)
            err, att = pair_error(net, fk, fq, xg, mean, std, device, grad=True)
            ch = lab == CHANGED
            valid = (lab == SAME) | ch
            ch_share = float(ch.sum() / max(valid.sum(), 1))
            att_share = float(att[ch].sum() / max(att[valid].sum(), 1e-12))
            err_ch = pair_error(net, fk, blank(fq, ch), xg, mean, std, device)[0] if ch.any() else err
            dy, dx = rng.integers(args.shift_px // 2, args.shift_px, 2) * rng.choice([-1, 1], 2)
            ctrl = np.roll(ch, (dy, dx), (0, 1))
            err_ctrl = pair_error(net, fk, blank(fq, ctrl), xg, mean, std, device)[0] if ch.any() else err
            res.append({"run": r["run"], "segment": r["segment"], "index": r["index"], "frame": row_q, "keyframe": kf,
                        "key_dist_mm": float(np.linalg.norm(np.asarray(r["xi_gt"][j])[:3])),
                        "err_mm": err, "changed_share": ch_share, "not_seen_share": float((lab == NOT_SEEN).mean()),
                        "att_share_changed": att_share, "look_ratio": att_share / ch_share if ch_share > 0 else float("nan"),
                        "err_changed_blanked_mm": err_ch, "err_control_blanked_mm": err_ctrl})
            pics.append((err, fk, fq, lab, att, res[-1]))
            pics.sort(key=lambda p: p[0])
            if len(pics) > 2 * args.images:                       # keep only the best and worst ones
                pics = pics[: args.images] + pics[-args.images:]
        if (n_a + 1) % 25 == 0:
            print(f"  {n_a + 1}/{len(rows)} anchors", flush=True)

    for tag, sel in (("best", pics[: args.images]), ("worst", pics[-args.images:][::-1])):
        for i, (err, fk, fq, lab, att, rr) in enumerate(sel):
            t = (f"{rr['run']} frame {rr['frame']} vs {rr['keyframe']}: error {err:.1f} mm, changed {100 * rr['changed_share']:.0f} %, "
                 f"look ratio {rr['look_ratio']:.2f}, blanked changed {rr['err_changed_blanked_mm']:.1f} / control {rr['err_control_blanked_mm']:.1f} mm")
            cv2.imwrite(str(out / f"{tag}_{i}.jpg"), overlay(fk, fq, lab, att, t))

    g = lambda k: np.array([x[k] for x in res], float)
    err, chs, att, look = g("err_mm"), g("changed_share"), g("att_share_changed"), g("look_ratio")
    e_ch, e_ct = g("err_changed_blanked_mm"), g("err_control_blanked_mm")
    has = chs > 0.01
    summ = {"pairs": len(res), "err_mm_median": float(np.median(err)), "changed_share_median": float(np.median(chs)),
            "att_share_changed_median": float(np.median(att)), "look_ratio_median": float(np.nanmedian(look[has])) if has.any() else None,
            "err_changed_blanked_median": float(np.median(e_ch[has])) if has.any() else None,
            "err_control_blanked_median": float(np.median(e_ct[has])) if has.any() else None,
            "err_unblanked_median_same_pairs": float(np.median(err[has])) if has.any() else None,
            "pct_pairs_better_when_changed_blanked": float(100 * np.mean(e_ch[has] < err[has])) if has.any() else None,
            "spearman_err_vs_changed_share": spearman(err, chs), "spearman_err_vs_att_share_changed": spearman(err, att)}
    json.dump({"eval": args.eval, "settings": vars(args), "summary": summ, "pairs": res}, open(out / "saliency.json", "w"), indent=1)
    f = lambda v, d=1: "–" if v is None else f"{v:.{d}f}"
    md = [f"# Anchor attribution and masking test: {Path(args.eval).name}", "",
          f"{len(res)} (keyframe, frame) pairs from {len(rows)} anchors; map {map_root} ({'+'.join(map_scans)}), sweeps {test_root}; "
          f"changed = depth disagrees by more than max({args.tol_mm:g} mm, {100 * args.tol_rel:g} %) after moving the frame into the keyframe with the true poses.", "",
          "| measure | value |", "|---|---|",
          f"| pair error, median (translation, mm) | {f(summ['err_mm_median'])} |",
          f"| share of the frame that changed (of pixels seen in both), median | {f(100 * summ['changed_share_median'])} % |",
          f"| share of the attribution on changed pixels, median | {f(100 * summ['att_share_changed_median'])} % |",
          f"| look ratio (attribution share / area share; > 1: looks at changed parts more than their area), pairs with > 1 % changed | {f(summ['look_ratio_median'], 2)} |",
          f"| error with nothing blanked / changed pixels blanked / control (same mask, shifted), same pairs, median (mm) | "
          f"{f(summ['err_unblanked_median_same_pairs'])} / {f(summ['err_changed_blanked_median'])} / {f(summ['err_control_blanked_median'])} |",
          f"| pairs with lower error when the changed pixels are blanked | {f(summ['pct_pairs_better_when_changed_blanked'], 0)} % |",
          f"| rank correlation: error vs changed share / error vs attribution on changed | {f(summ['spearman_err_vs_changed_share'], 2)} / {f(summ['spearman_err_vs_att_share_changed'], 2)} |",
          "", f"Images: best_*.jpg and worst_*.jpg (keyframe | frame with changed pixels in magenta | attribution of the error)."]
    (out / "saliency.md").write_text("\n".join(md) + "\n")
    print("\n" + "\n".join(md[4:-2]) + f"\n-> {out / 'saliency.md'}")


if __name__ == "__main__":
    main()
