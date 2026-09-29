"""
Full evaluation of a trained SCR checkpoint on its held-out validation runs.

Reports:
  * per-pixel coordinate error (median / p95 / mean), vs. the
    predict-the-scene-centroid baseline every checkpoint must beat to show
    it learned anything
  * solved pose error (translation mm, rotation deg) via PnP-RANSAC on the
    predicted coordinates, bootstrapped over runs
  * optionally (--kabsch), the same via Kabsch-RANSAC on the *measured*
    depth matched against predicted coordinates, for the 2D-3D vs 3D-3D
    comparison
  * a GT-vs-solved trajectory plot per validation run (eval_trajectories.png,
    disable with --no-plot) -- a path that visibly diverges from GT is
    obvious there in a way the pooled median/p95 numbers can hide

Both solve paths use depth_mask (real, measured-depth validity -- what a
deployed system actually has, unlike xyz_mask which also requires the GT
tracker label) to pick which cells to hand the solver. Cells the network was
never trained on because RealSense returned nothing there reach RANSAC as
real outliers, so solve_rate below is not artificially inflated.

Usage:
  python3 eval.py --ckpt runs/run_2_seq_3/best.pt
  python3 eval.py --ckpt runs/run_2_seq_3/best.pt --root data --kabsch
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import torch
from torch.utils.data import DataLoader

from dataset import SCRConfig, SCRDataset, build_splits
from geometry import backproject
from loss import coordinate_metrics
from model import SCRNet, pixel_grid
from solver import kabsch_ransac, pnp_ransac, pose_error
from train import bootstrap_group_ci, centroid_baseline, load_hand_eye, move, resample_labels


def summarise(name, vals, groups=None, seed=0):
    vals = np.asarray(vals, dtype=np.float64)
    print(f"\n  {name}  (n={len(vals)})")
    print(f"    median {np.median(vals):9.3f}   p95 {np.percentile(vals, 95):9.3f}   "
          f"mean {vals.mean():9.3f}")
    res = {"median": float(np.median(vals)), "p95": float(np.percentile(vals, 95)),
           "mean": float(vals.mean()), "n": len(vals)}
    if groups is not None and len(groups) == len(vals):
        lo, hi, n_groups = bootstrap_group_ci(groups, vals, seed=seed)
        if n_groups >= 2:
            print(f"    CI95   [{lo:.3f}, {hi:.3f}]  ({n_groups} groups)")
            res["ci95"] = (lo, hi)
            res["ci_groups"] = n_groups
    return res


def solve_pnp(xyz_world, uv, K, reproj_threshold):
    return pnp_ransac(xyz_world, uv, K, reproj_threshold)


def solve_kabsch(xyz_world, xyz_cam, threshold):
    return kabsch_ransac(xyz_world, xyz_cam, threshold)


def plot_trajectories(pnp_records, kab_records, out_path):
    """GT vs. solved camera-centre trajectories, one 3D subplot per run.

    Same idea as validate_run.py's trajectory plot, but overlaying the
    solved pose on top of the tracker GT instead of just showing the GT --
    a solved path that visibly diverges from GT (drift, jumps, offset) is
    obvious here in a way the pooled median/p95 numbers above can hide.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    runs = sorted({r for r, *_ in pnp_records} | {r for r, *_ in kab_records})
    if not runs:
        return
    fig = plt.figure(figsize=(5 * len(runs), 5))
    for k, run in enumerate(runs):
        ax = fig.add_subplot(1, len(runs), k + 1, projection="3d")

        pnp_r = sorted(((f, gt, est) for r, f, gt, est in pnp_records if r == run),
                       key=lambda t: t[0])
        if pnp_r:
            gt_xyz = np.array([gt[:3, 3] for _, gt, _ in pnp_r])
            est_xyz = np.array([est[:3, 3] for _, _, est in pnp_r])
            ax.plot(*gt_xyz.T, c="k", lw=1.5, label="GT")
            ax.plot(*est_xyz.T, c="tab:blue", lw=1, marker=".", ms=3, label="PnP")
            ax.scatter(*gt_xyz[0], c="g", s=40, label="start")
            ax.scatter(*gt_xyz[-1], c="r", s=40, label="end")

        kab_r = sorted(((f, gt, est) for r, f, gt, est in kab_records if r == run),
                       key=lambda t: t[0])
        if kab_r:
            est_xyz = np.array([est[:3, 3] for _, _, est in kab_r])
            ax.plot(*est_xyz.T, c="tab:orange", lw=1, marker=".", ms=3, label="Kabsch")

        ax.set_title(run, fontsize=9)
        ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)"); ax.set_zlabel("z (mm)")
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    print(f"  wrote {out_path}")


def save_pose_estimates(records, out_dir, tag):
    """Write each val run's solved poses to <out_dir>/poses_<tag>_<run>.csv.

    One row per solved frame: frame,x,y,z,qx,qy,qz,qw (translation in mm,
    quaternion in x,y,z,w order). `records` is (run, frame, T_gt, T_est) --
    the same list plot_trajectories already builds, so no extra solving.
    """
    from scipy.spatial.transform import Rotation

    runs = sorted({r for r, *_ in records})
    for run in runs:
        rows = sorted((f, T) for r, f, _gt, T in records if r == run)
        path = Path(out_dir) / f"poses_{tag}_{run}.csv"
        with open(path, "w") as fh:
            fh.write("frame,x,y,z,qx,qy,qz,qw\n")
            for frame, T in rows:
                x, y, z = T[:3, 3]
                qx, qy, qz, qw = Rotation.from_matrix(T[:3, :3]).as_quat()
                fh.write(f"{frame},{x:.4f},{y:.4f},{z:.4f},"
                        f"{qx:.6f},{qy:.6f},{qz:.6f},{qw:.6f}\n")
        print(f"  wrote {path}")


class _OrbitViewer:
    """Minimal interactive 3D viewer for one run's trajectories.

    OpenCV has no built-in 3D renderer in this install (cv2.viz needs a
    VTK-linked build, which the pip wheel doesn't ship), so this does the
    rotation itself: left-drag orbits (orthographic projection, rotate
    around Z then X), the scroll wheel zooms. `series` is a list of
    (points (N,3), BGR color, "line"|"points").
    """

    def __init__(self, name, series, size=640):
        self.name, self.series, self.size = name, series, size
        self.az, self.el, self.zoom = -60.0, 20.0, 1.0
        self.dragging, self.last = False, (0, 0)
        pts = np.concatenate([p for p, _, _ in series], axis=0)
        self.center = pts.mean(axis=0)
        self.radius = max(float(np.abs(pts - self.center).max()), 1e-6)
        cv2.namedWindow(self.name)
        cv2.setMouseCallback(self.name, self._on_mouse)

    def _on_mouse(self, event, x, y, flags, _param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.dragging, self.last = True, (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            dx, dy = x - self.last[0], y - self.last[1]
            self.az += dx * 0.4
            self.el = float(np.clip(self.el - dy * 0.4, -89.0, 89.0))
            self.last = (x, y)
        elif event == cv2.EVENT_MOUSEWHEEL:
            self.zoom *= 1.1 if flags > 0 else (1 / 1.1)

    def _project(self, pts):
        p = (pts - self.center) / self.radius
        a, e = np.radians(self.az), np.radians(self.el)
        cz, sz = np.cos(a), np.sin(a)
        Rz = np.array([[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]])
        ce, se = np.cos(e), np.sin(e)
        Rx = np.array([[1.0, 0.0, 0.0], [0.0, ce, -se], [0.0, se, ce]])
        p = p @ Rz.T @ Rx.T
        s = self.size * 0.35 * self.zoom
        u = (p[:, 0] * s + self.size / 2).astype(np.int32)
        v = (-p[:, 1] * s + self.size / 2).astype(np.int32)
        return np.stack([u, v], axis=1)

    def render(self):
        img = np.full((self.size, self.size, 3), 30, np.uint8)
        for pts, color, mode in self.series:
            uv = self._project(pts)
            if mode == "line":
                cv2.polylines(img, [uv], False, color, 1, cv2.LINE_AA)
            else:
                for u, v in uv:
                    cv2.circle(img, (int(u), int(v)), 4, color, -1, cv2.LINE_AA)
        cv2.putText(img, f"{self.name}  (drag=orbit, wheel=zoom)", (8, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow(self.name, img)


def show_pose_3d_cv2(pnp_records, kab_records):
    """GT-vs-solved trajectories, one interactive OpenCV window per val run.

    Unlike a static plot, this actually renders and re-projects in 3D: drag
    to orbit, scroll to zoom. See _OrbitViewer for the projection.
    """
    runs = sorted({r for r, *_ in pnp_records} | {r for r, *_ in kab_records})
    if not runs:
        return

    viewers = []
    for run in runs:
        series = []
        pnp_r = sorted(((f, gt, est) for r, f, gt, est in pnp_records if r == run),
                       key=lambda t: t[0])
        if pnp_r:
            gt_xyz = np.array([gt[:3, 3] for _, gt, _ in pnp_r])
            est_xyz = np.array([est[:3, 3] for _, _, est in pnp_r])
            series.append((gt_xyz, (255, 255, 255), "line"))     # GT, white
            series.append((est_xyz, (255, 0, 0), "line"))        # PnP, blue
            series.append((gt_xyz[:1], (0, 255, 0), "points"))   # start, green
            series.append((gt_xyz[-1:], (0, 0, 255), "points"))  # end, red

        kab_r = sorted(((f, gt, est) for r, f, gt, est in kab_records if r == run),
                       key=lambda t: t[0])
        if kab_r:
            est_xyz = np.array([est[:3, 3] for _, _, est in kab_r])
            series.append((est_xyz, (0, 165, 255), "line"))      # Kabsch, orange

        if series:
            viewers.append(_OrbitViewer(run, series))

    print("  drag with the left mouse button to orbit each window, scroll to "
          "zoom, press q or ESC (window focused) to close")
    while viewers:
        for v in viewers:
            v.render()
        if cv2.waitKey(15) & 0xFF in (27, ord("q")):
            break
    cv2.destroyAllWindows()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--root", default=None, help="defaults to the root the checkpoint was trained on")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--reproj-threshold", type=float, default=None, help="PnP inlier threshold, pixels; defaults to the training value")
    ap.add_argument("--kabsch", action="store_true",
                    help="also solve pose via 3D-3D Kabsch (measured depth vs "
                         "predicted coordinates) for the PnP vs Kabsch comparison")
    ap.add_argument("--kabsch-threshold", type=float, default=50.0, help="Kabsch inlier threshold, millimetres")
    ap.add_argument("--out", default=None, help="write metrics json here") 
    ap.add_argument("--plot-out", default=None, help="write the trajectory plot here (default: next to --ckpt)")
    ap.add_argument("--save-poses", action="store_true",
                    help="write each val run's solved poses (x,y,z,qx,qy,qz,qw) to "
                         "poses_<solver>_<run>.csv next to --ckpt")
    ap.add_argument("--show-3d", action="store_true",
                    help="show each val run's GT-vs-solved trajectory in a live OpenCV "
                         "window (blocks until a key is pressed)")
    args = ap.parse_args()

    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ck = torch.load(args.ckpt, map_location=dev, weights_only=False)
    a = ck["args"]
    print(f"checkpoint: {args.ckpt}  (epoch {ck['epoch'] + 1})")

    # calibration_pending only makes dataset.py fall back to identity when
    # T_marker_cam is None (dataset.py SCRConfig.__post_init__) -- if
    # --hand-eye was also given, the real matrix wins and the flag is stale,
    # not a description of what labels the run actually used. Distinguish
    # the two rather than trusting the flag (and config.json's REPORTABLE,
    # which is derived from the same flag) at face value.
    identity_hand_eye = a["calibration_pending"] and not a["hand_eye"]
    if identity_hand_eye:
        print("\n  CALIBRATION PENDING at training time -- labels used identity "
              "hand-eye. Nothing below is reportable, only useful for pipeline "
              "debugging.")
    elif a["calibration_pending"] and a["hand_eye"]:
        print(f"\n  NOTE: calibration_pending=True but --hand-eye {a['hand_eye']!r} "
              "was also set. dataset.py uses the real matrix whenever one is "
              "given -- labels below were built from the real calibration, not "
              "identity -- but config.json's REPORTABLE and each batch's "
              "'calibrated' flag were derived from calibration_pending alone, "
              "so they are mislabeled for this run. Treat REPORTABLE as unknown, "
              "not false, until this is confirmed with whoever launched training.")

    root = args.root or a["root"]
    _, val_runs = build_splits(root, a["val_runs"], a["val_fraction"], a["seed"])
    print(f"val runs: {val_runs}")

    T_marker_cam = load_hand_eye(a["hand_eye"], a["hand_eye_units"]) if a["hand_eye"] else None
    cfg = SCRConfig(
        pose_units=a["pose_units"], T_marker_cam=T_marker_cam,
        calibration_pending=a["calibration_pending"],
        image_size=tuple(a["image_size"]), max_depth=a["max_depth"],
        avg_frames=a["avg_frames"], seq_len=a["seq_len"], seq_stride=a["seq_stride"],
        augment=False,
        scene_center=np.asarray(ck["scene_center"]), scene_scale=ck["scene_scale"])
    ds = SCRDataset(root, val_runs, cfg)
    dl = DataLoader(ds, batch_size=args.batch_size, num_workers=args.workers)
    print(f"val frames: {len(ds)}")

    net = SCRNet(
        backbone=a["backbone"], pretrained=False, use_depth=not a["no_depth"],
        head_width=a["head_width"], predict_uncertainty=a["uncertainty"],
        seq_len=a["seq_len"],
        scene_center=torch.from_numpy(np.asarray(ck["scene_center"])).float(),
        scene_scale=ck["scene_scale"]).to(dev)
    net.load_state_dict(ck["model"])
    net.eval()

    base_mm = centroid_baseline(ds, ck["scene_scale"])
    print(f"\n  centroid baseline: {base_mm:.1f} mm  "
          "(anything at or near this means the network learned nothing)")

    reproj_threshold = args.reproj_threshold or a["reproj_threshold"]
    min_depth = cfg.min_depth
    stride, off = net.stride, net.stride // 2

    coord_errs = []
    t_pnp, r_pnp, t_kab, r_kab = [], [], [], []
    pose_runs, pose_idx, kab_runs, kab_idx = [], [], [], []
    pnp_records, kab_records = [], []          # (run, frame, T_gt, T_est), for the plot
    attempted = solved_pnp = solved_kab = 0

    with torch.no_grad():
        for batch in dl:
            b = move(batch, dev)
            out = net(b["rgb"], b["inv_depth"], b["depth_mask"])
            coord_errs.append(coordinate_metrics(out, b, ck["scene_scale"]).float().cpu())

            xyz = out["xyz"].float().cpu().numpy()          # (B, 3, h, w)
            B, _, h, w = xyz.shape
            uv = pixel_grid(h, w, stride).numpy()
            K = batch["K"].numpy()
            T_gt = batch["T_world_cam"].numpy().astype(np.float64)
            # D4 fix: gate on depth_mask (real depth availability), not
            # xyz_mask (requires the GT tracker label) -- see module docstring.
            dmask_anchor = batch["depth_mask"][:, -1, 0].numpy()   # (B, H, W)
            mask = dmask_anchor[:, off::stride, off::stride].reshape(B, -1) > 0
            if args.kabsch:
                inv_anchor = batch["inv_depth"][:, -1, 0].numpy()

            for i in range(B):
                pts_world = xyz[i].reshape(3, -1).T[mask[i]].astype(np.float64)
                pix = uv[mask[i]]
                attempted += 1

                T, _ = solve_pnp(pts_world, pix, K[i].astype(np.float64), reproj_threshold)
                if T is not None:
                    solved_pnp += 1
                    dt, dr = pose_error(T, T_gt[i])
                    t_pnp.append(dt); r_pnp.append(dr)
                    run_i, frame_i = batch["run"][i], int(batch["frame"][i])
                    pose_runs.append(run_i); pose_idx.append(frame_i)
                    pnp_records.append((run_i, frame_i, T_gt[i], T))

                if not args.kabsch:
                    continue
                depth_mm = np.zeros_like(inv_anchor[i])
                m = dmask_anchor[i] > 0
                depth_mm[m] = min_depth / inv_anchor[i][m]
                xyz_cam_full = backproject(depth_mm, K[i].astype(np.float64))
                xyz_cam = xyz_cam_full[off::stride, off::stride].reshape(-1, 3)[mask[i]]

                Tk, _ = solve_kabsch(pts_world, xyz_cam, args.kabsch_threshold)
                if Tk is not None:
                    solved_kab += 1
                    dt, dr = pose_error(Tk, T_gt[i])
                    t_kab.append(dt); r_kab.append(dr)
                    run_i, frame_i = batch["run"][i], int(batch["frame"][i])
                    kab_runs.append(run_i); kab_idx.append(frame_i)
                    kab_records.append((run_i, frame_i, T_gt[i], Tk))

    print("\n" + "=" * 62)
    coord = torch.cat(coord_errs).numpy()
    res = {"coord_mm": summarise("COORDINATE ERROR", coord),
           "centroid_baseline_mm": base_mm}

    if t_pnp:
        groups = resample_labels(pose_runs, pose_idx)
        res["pose_pnp"] = summarise("POSE (PnP, 2D-3D)  translation mm", t_pnp, groups)
        res["pose_pnp"]["rotation_deg"] = summarise(
            "POSE (PnP, 2D-3D)  rotation deg", r_pnp, groups)
        res["pose_pnp"]["solve_rate"] = solved_pnp / max(attempted, 1)
    print(f"\n  PnP solve rate: {solved_pnp}/{attempted}")

    if args.kabsch:
        if t_kab:
            groups = resample_labels(kab_runs, kab_idx)
            res["pose_kabsch"] = summarise(
                "POSE (Kabsch, 3D-3D)  translation mm", t_kab, groups)
            res["pose_kabsch"]["rotation_deg"] = summarise(
                "POSE (Kabsch, 3D-3D)  rotation deg", r_kab, groups)
            res["pose_kabsch"]["solve_rate"] = solved_kab / max(attempted, 1)
        print(f"  Kabsch solve rate: {solved_kab}/{attempted}")

        if t_pnp and t_kab:
            print("\n  VERDICT (PnP vs Kabsch)")
            dt = 100 * (1 - np.median(t_pnp) / np.median(t_kab))
            print(f"    PnP translation is {dt:+.1f}% vs Kabsch "
                  "(positive = PnP better)")
            print("    RealSense depth error grows with range, so a positive "
                  "number here (PnP winning despite Kabsch's better-conditioned "
                  "3D-3D fit) is the expected outcome -- see solver.py's "
                  "docstring.")

    if identity_hand_eye:
        print("\n  CALIBRATION PENDING: none of the numbers above are reportable.")

    if pnp_records or kab_records:
        plot_path = Path(args.plot_out) if args.plot_out \
            else Path(args.ckpt).parent / "eval_trajectories.png"
        plot_trajectories(pnp_records, kab_records, plot_path)

    if args.save_poses:
        pose_dir = Path(args.ckpt).parent
        if pnp_records:
            save_pose_estimates(pnp_records, pose_dir, "pnp")
        if kab_records:
            save_pose_estimates(kab_records, pose_dir, "kabsch")

    if args.show_3d:
        show_pose_3d_cv2(pnp_records, kab_records)

    out = Path(args.out) if args.out else Path(args.ckpt).parent / "eval.json"
    json.dump(res, open(out, "w"), indent=2)
    print(f"\n  wrote {out}")


if __name__ == "__main__":
    main()
