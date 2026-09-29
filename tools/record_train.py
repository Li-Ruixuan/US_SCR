"""
Synchronized RGB-D + ultrasound recorder for RealSense under ROS 2. 

cd ~/Polaris_Vega_VT
python3 vega_rtsp_overlay_ros.py

ros2 launch usb_cam demo_launch.py 

ros2 launch realsense2_camera rs_launch.py \
    align_depth.enable:=true \
    enable_gyro:=true enable_accel:=true unite_imu_method:=2 \
    rgb_camera.enable_auto_exposure:=false \
    rgb_camera.exposure:=<fixed> \
    rgb_camera.white_balance:=<fixed>

Usage:
  python3 record.py --run run_002 --root ./data --duration 40  
  python3 record.py --run run_003 --no-us      # RGB-D only, as before
"""

import argparse
import csv
import json
import os
import queue
import threading
import time
from collections import deque
from pathlib import Path

import numpy as np
import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image, Imu
from geometry_msgs.msg import PoseStamped

import message_filters


class SyncedImageSaver(Node):
    def __init__(self, args):
        super().__init__("synced_image_saver")
        self.bridge = CvBridge()
        self.args = args
        self.use_us = not args.no_us
        self.use_pose = not args.no_pose
        self.pose_max_gap = args.pose_max_gap

        self.run_dir = Path(args.root) / args.run
        self.color_dir = self.run_dir / "rgb"
        self.depth_dir = self.run_dir / "depth"
        self.us_dir = self.run_dir / "us"
        self.color_dir.mkdir(parents=True, exist_ok=True)
        self.depth_dir.mkdir(parents=True, exist_ok=True)
        if self.use_us:
            self.us_dir.mkdir(parents=True, exist_ok=True)

        if any(self.color_dir.iterdir()):
            raise RuntimeError(f"{self.color_dir} is not empty -- pick a new run name")

        self.idx = 0
        self.dropped = 0
        self.duration = args.duration
        self.t_start = None

        # Arrival counters, incremented per incoming message on each topic.
        # The gap between these and self.idx is how many messages the synchronizer threw away for want of a match.
        self.n_color = 0
        self.n_depth = 0
        self.n_us = 0

        # ---- frames.csv, written incrementally -------------------------------
        # Pose columns are filled at record time by interpolating the
        # optical marker stream onto each frame's stamp. Blank means no
        # pose within --pose-max-gap, i.e. the marker was occluded.
        # The us column is present but empty under --no-us, so the schema is
        # stable across runs and the dataloader needs no special case.
        self.csv_path = self.run_dir / "frames.csv"
        self.csv_file = open(self.csv_path, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(
            ["timestamp", "us_timestamp", "rgb", "depth", "us",
             "tx", "ty", "tz", "qx", "qy", "qz", "qw"]
        )
        self.csv_lock = threading.Lock()

        # ---- imu.csv --------------------------------------------------------
        # Written straight from the callback: IMU messages are tiny and arrive
        # at a few hundred Hz, so there is no reason to queue them.
        self.imu_file = open(self.run_dir / "imu.csv", "w")
        self.imu_file.write("timestamp,gx,gy,gz,ax,ay,az\n")
        self.n_imu = 0

        # ---- pose.csv (NDI Polaris Vicra optical marker) ---------------------
        # Units are whatever the tracker node publishes -- millimetres by
        # default. Recorded verbatim and noted in record_config.json.
        self.pose_file = None
        self.n_pose = 0
        self.pose_first_stamp = None
        self.pose_last_stamp = None
        if self.use_pose:
            self.pose_file = open(self.run_dir / "pose.csv", "w")
            self.pose_file.write("timestamp,tx,ty,tz,qx,qy,qz,qw\n")

        # Ring buffer of recent pose samples, used to fill the pose columns of
        # frames.csv at record time. ~10 s at 60 Hz. The synchronizer fires well
        # after the frame's acquisition stamp, so samples bracketing that stamp
        # have normally already arrived.
        self.pose_buf: deque = deque(maxlen=args.pose_buffer)
        self.pose_lock = threading.Lock()
        self.n_pose_filled = 0
        self.n_pose_unfilled = 0

        # ---- background encoders --------------------------------------------
        # maxsize bounds memory: if the writers cannot keep up we drop frames
        # loudly rather than growing the queue until the machine swaps.
        self.q: queue.Queue = queue.Queue(maxsize=args.queue_size)
        self.stop_evt = threading.Event()
        self.workers = [
            threading.Thread(target=self._writer_loop, daemon=True)
            for _ in range(args.workers)
        ]
        for w in self.workers:
            w.start()

        # ---- intrinsics: grab one message, then unsubscribe ------------------
        self.have_info = False
        self.info_sub = self.create_subscription(
            CameraInfo, "/camera/color/camera_info", self._on_camera_info, 1
        )

        # US camera_info carries pixel spacing if the publisher sets it, which
        # you need to convert image coordinates to millimetres. 
        self.have_us_info = False
        self.us_info_sub = None
        if self.use_us and args.us_info_topic:
            self.us_info_sub = self.create_subscription(
                CameraInfo, args.us_info_topic, self._on_us_camera_info, 1
            )

        # ---- synchronized image streams --------------------------------------
        self.color_sub = message_filters.Subscriber(
            self, Image, "/camera/color/image_raw"
        )
        self.depth_sub = message_filters.Subscriber(
            self, Image, "/camera/aligned_depth_to_color/image_raw"
        )
        self.color_sub.registerCallback(self._count_color)
        self.depth_sub.registerCallback(self._count_depth)

        subs = [self.color_sub, self.depth_sub]
        if self.use_us:
            self.us_sub = message_filters.Subscriber(self, Image, args.us_topic)
            self.us_sub.registerCallback(self._count_us)
            subs.append(self.us_sub)

        # queue_size is per topic. With three streams the synchronizer needs
        # room to hold messages while it waits for the slowest partner, so a
        # small buffer loses matches to ordinary arrival jitter.
        self.ts = message_filters.ApproximateTimeSynchronizer(
            subs, queue_size=args.sync_queue, slop=args.slop
        )
        self.ts.registerCallback(self.synced_callback)

        self.imu_sub = self.create_subscription(
            Imu, "/camera/imu", self._on_imu, 400)

        self.pose_sub = None
        if self.use_pose:
            self.pose_sub = self.create_subscription(
                PoseStamped, args.pose_topic, self._on_pose, 100)

        self.timer = self.create_timer(10.0, self._report)
        self.get_logger().info(
            f"recording to {self.run_dir} -- slop={args.slop * 1e3:.0f} ms -- "
            "Ctrl-C to stop")
        if self.use_pose:
            self.get_logger().info(f"optical marker topic: {args.pose_topic}")
        if self.use_us:
            self.get_logger().info(f"ultrasound topic: {args.us_topic}")
            self.get_logger().info(
                "TAP THE PROBE now for the start-of-session sync event")

    # -------------------------------------------------------------- counters
    def _count_color(self, _msg):
        self.n_color += 1

    def _count_depth(self, _msg):
        self.n_depth += 1

    def _count_us(self, _msg):
        self.n_us += 1

    # ------------------------------------------------------------------ info
    def _on_camera_info(self, msg: CameraInfo):
        if self.have_info:
            return
        info = {
            "width": msg.width,
            "height": msg.height,
            "fx": msg.k[0],
            "fy": msg.k[4],
            "cx": msg.k[2],
            "cy": msg.k[5],
            "K": list(msg.k),
            "D": list(msg.d),
            "distortion_model": msg.distortion_model, 
            "depth_scale": 0.001,
        }
        with open(self.run_dir / "camera_info.json", "w") as f:
            json.dump(info, f, indent=2)
        self.have_info = True
        self.destroy_subscription(self.info_sub)
        self.get_logger().info(
            f"intrinsics saved: fx={info['fx']:.1f} cx={info['cx']:.1f} "
            f"{info['width']}x{info['height']}"
        )

    def _on_us_camera_info(self, msg: CameraInfo):
        if self.have_us_info:
            return
        with open(self.run_dir / "us_camera_info.json", "w") as f:
            json.dump({
                "width": msg.width,
                "height": msg.height,
                "K": list(msg.k),
                "D": list(msg.d),
                "distortion_model": msg.distortion_model,
            }, f, indent=2)
        self.have_us_info = True
        self.destroy_subscription(self.us_info_sub)
        self.get_logger().info("us_camera_info.json saved")

    # ------------------------------------------------------------------- imu
    def _on_imu(self, msg: Imu):
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        g, a = msg.angular_velocity, msg.linear_acceleration
        self.imu_file.write(
            f"{t:.9f},{g.x:.6f},{g.y:.6f},{g.z:.6f},"
            f"{a.x:.6f},{a.y:.6f},{a.z:.6f}\n")
        self.n_imu += 1

    # ------------------------------------------------------------------ pose
    def _on_pose(self, msg: PoseStamped):
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        p, o = msg.pose.position, msg.pose.orientation
        self.pose_file.write(
            f"{t:.9f},{p.x:.6f},{p.y:.6f},{p.z:.6f},"
            f"{o.x:.9f},{o.y:.9f},{o.z:.9f},{o.w:.9f}\n")
        self.n_pose += 1
        if self.pose_first_stamp is None:
            self.pose_first_stamp = t
        self.pose_last_stamp = t

        with self.pose_lock:
            self.pose_buf.append(
                (t, p.x, p.y, p.z, o.x, o.y, o.z, o.w))

    @staticmethod
    def _slerp(q0, q1, u):
        """Spherical linear interpolation, (x,y,z,w) order.

        Component-wise linear interpolation of quaternions does not give a
        rotation; the error grows with the angle between samples.
        """
        q0 = np.asarray(q0, dtype=np.float64)
        q1 = np.asarray(q1, dtype=np.float64)
        dot = float(np.dot(q0, q1))
        if dot < 0.0:           # take the short way round
            q1 = -q1
            dot = -dot
        if dot > 0.9995:        # nearly parallel -> lerp is safe and stable
            q = q0 + u * (q1 - q0)
            return q / np.linalg.norm(q)
        theta = np.arccos(np.clip(dot, -1.0, 1.0))
        s = np.sin(theta)
        return (np.sin((1.0 - u) * theta) / s) * q0 + (np.sin(u * theta) / s) * q1

    def _lookup_pose(self, t):
        """Pose at time t, interpolated from the ring buffer.

        Returns (values, gap_s) where values is [tx,ty,tz,qx,qy,qz,qw], or
        (None, gap_s) if no sample is within --pose-max-gap. A miss means the
        marker was occluded around t; leaving the row blank is correct, since
        interpolating across an occlusion invents a plausible wrong pose.
        """
        with self.pose_lock:
            if not self.pose_buf:
                return None, float("inf")
            buf = list(self.pose_buf)

        ts = [b[0] for b in buf]

        # bracketing pair?
        if ts[0] <= t <= ts[-1]:
            hi = np.searchsorted(ts, t)
            hi = int(np.clip(hi, 1, len(ts) - 1))
            lo = hi - 1
            t0, t1 = ts[lo], ts[hi]
            gap = min(abs(t - t0), abs(t - t1))
            if gap > self.pose_max_gap:
                return None, gap
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            a, b = buf[lo], buf[hi]
            xyz = [a[1 + k] + u * (b[1 + k] - a[1 + k]) for k in range(3)]
            quat = self._slerp(a[4:8], b[4:8], u)
            return xyz + [float(v) for v in quat], gap

        # outside the buffered span: fall back to the nearest sample
        nearest = 0 if t < ts[0] else len(ts) - 1
        gap = abs(t - ts[nearest])
        if gap > self.pose_max_gap:
            return None, gap
        s = buf[nearest]
        return [s[1], s[2], s[3], s[4], s[5], s[6], s[7]], gap

    # --------------------------------------------------------------- capture
    def synced_callback(self, color_msg, depth_msg, us_msg=None):
        if self.t_start is None:
            self.t_start = time.time()

        stamp = color_msg.header.stamp.sec + color_msg.header.stamp.nanosec * 1e-9 
        color = self.bridge.imgmsg_to_cv2(color_msg, desired_encoding="bgr8")
        depth = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding="passthrough")

        us = None
        us_stamp = ""
        if us_msg is not None: 
            us = self.bridge.imgmsg_to_cv2(
                us_msg, desired_encoding="passthrough").copy()
            t_us = us_msg.header.stamp.sec + us_msg.header.stamp.nanosec * 1e-9 
            us_stamp = f"{t_us:.9f}"

        pose_vals = None
        if self.use_pose:
            pose_vals, _gap = self._lookup_pose(stamp)
            if pose_vals is None:
                self.n_pose_unfilled += 1
            else:
                self.n_pose_filled += 1

        try: 
            self.q.put_nowait(
                (self.idx, stamp, us_stamp, color.copy(), depth.copy(), us,
                 pose_vals))
            self.idx += 1
        except queue.Full:
            self.dropped += 1

        if self.duration and (time.time() - self.t_start) > self.duration:
            self.get_logger().info("duration reached")
            raise KeyboardInterrupt

    def _writer_loop(self):
        us_params = []
        if self.args.us_ext == "png": 
            us_params = [cv2.IMWRITE_PNG_COMPRESSION, 1]
        elif self.args.us_ext == "jpg":
            us_params = [cv2.IMWRITE_JPEG_QUALITY, self.args.us_jpeg_quality]

        while not self.stop_evt.is_set():
            try:
                idx, stamp, us_stamp, color, depth, us, pose_vals = self.q.get(timeout=0.2)
            except queue.Empty:
                continue
            rel_rgb = f"rgb/{idx:06d}.png"
            rel_depth = f"depth/{idx:06d}.png"
            cv2.imwrite(str(self.run_dir / rel_rgb), color)
            # PNG compression 1: 16-bit depth barely compresses anyway, and
            # level 1 is ~3x faster to encode than the default.
            cv2.imwrite(str(self.run_dir / rel_depth), depth,
                        [cv2.IMWRITE_PNG_COMPRESSION, 1])

            rel_us = ""
            if us is not None:
                rel_us = f"us/{idx:06d}.{self.args.us_ext}"
                cv2.imwrite(str(self.run_dir / rel_us), us, us_params)

            if pose_vals is None:
                pose_cells = ["", "", "", "", "", "", ""]
            else:
                pose_cells = [f"{v:.6f}" for v in pose_vals[:3]] + \
                             [f"{v:.9f}" for v in pose_vals[3:]]

            with self.csv_lock:
                self.csv_writer.writerow(
                    [f"{stamp:.9f}", us_stamp, rel_rgb, rel_depth, rel_us]
                    + pose_cells
                )
            self.q.task_done()

    def _report(self):
        elapsed = (time.time() - self.t_start) if self.t_start else 0.0
        fps = self.idx / elapsed if elapsed > 0 else 0.0
        msg = (f"{self.idx} matched  {fps:.1f} fps  q={self.q.qsize()}  "
               f"dropped={self.dropped}  imu={self.n_imu}"
               f"{f'  pose={self.n_pose}' if self.use_pose else ''}"
               f"{f' filled={self.n_pose_filled}/{self.n_pose_filled + self.n_pose_unfilled}' if self.use_pose else ''}"
               f" | arrivals rgb={self.n_color} depth={self.n_depth}")
        if self.use_us:
            msg += f" us={self.n_us}"

        warn = self.dropped > 0 
        arrivals = min(self.n_color, self.n_depth,
                       self.n_us if self.use_us else self.n_color)
        if arrivals > 30 and self.idx < 0.7 * arrivals:
            warn = True
            msg += "  <-- LOW MATCH RATE, raise --slop"
        if self.dropped:
            msg += "  <-- writers falling behind"
        (self.get_logger().warn if warn else self.get_logger().info)(msg)

    # ---------------------------------------------------------------- finish
    def finish(self):
        if self.use_us:
            self.get_logger().info("TAP THE PROBE now for the end-of-session sync event, then wait")
            time.sleep(2.0)

        self.get_logger().info(f"flushing {self.q.qsize()} queued frames...")
        self.q.join()
        self.stop_evt.set()
        for w in self.workers:
            w.join(timeout=2.0)
        with self.csv_lock:
            self.csv_file.close()
        self.imu_file.close()
        if self.pose_file is not None:
            self.pose_file.close()

        # Writers finish out of order, so sort the CSV by timestamp.
        import pandas as pd
        df = pd.read_csv(self.csv_path).sort_values("timestamp")
        df.to_csv(self.csv_path, index=False)

        # Residual matching error: how far apart the paired stamps actually
        # were. If this sits near slop, the window is doing real work and
        # tightening it would cost frames.
        match_stats = None
        if self.use_us and "us_timestamp" in df and df["us_timestamp"].notna().any():
            d = (df["timestamp"] - df["us_timestamp"]).dropna()
            if len(d):
                match_stats = {"mean_s": float(d.mean()),
                               "std_s": float(d.std()),
                               "max_abs_s": float(d.abs().max())}
                self.get_logger().info(
                    f"rgb-us stamp offset: mean {d.mean() * 1e3:.1f} ms  "
                    f"std {d.std() * 1e3:.1f} ms  max {d.abs().max() * 1e3:.1f} ms")

        arrivals = {"rgb": self.n_color, "depth": self.n_depth}
        if self.use_us:
            arrivals["us"] = self.n_us
        with open(self.run_dir / "record_config.json", "w") as f:
            json.dump({
                "run": self.args.run,
                "matched_frames": len(df),
                "write_dropped": self.dropped,
                "arrivals": arrivals,
                "sync": {"slop_s": self.args.slop,
                         "queue_size": self.args.sync_queue},
                "match_stats": match_stats,
                "us": {"enabled": self.use_us,
                       "topic": self.args.us_topic if self.use_us else None,
                       "ext": self.args.us_ext},
                "imu_samples": self.n_imu,
                "pose": {
                    "enabled": self.use_pose,
                    "topic": self.args.pose_topic if self.use_pose else None,
                    "samples": self.n_pose,
                    "frames_filled": self.n_pose_filled,
                    "frames_unfilled": self.n_pose_unfilled,
                    "max_gap_s": self.args.pose_max_gap,
                    "units": self.args.pose_units,
                    "note": (
                        "pose.csv is the raw 60 Hz stream. The pose columns "
                        "of frames.csv are interpolated onto frame stamps at "
                        "record time (linear translation, slerp rotation). "
                        "Blank rows mean no sample within max_gap_s."
                    ),
                },
                "timestamp_note": (
                    "Streams are matched on header stamps. This is only valid "
                    "if the US node stamps at acquisition rather than publish. "
                    "Verify with the probe-tap sync events at start and end."
                ),
            }, f, indent=2)

        if self.n_imu == 0:
            self.get_logger().error(
                "NO IMU samples. Relaunch the camera with enable_gyro:=true "
                "enable_accel:=true unite_imu_method:=2 -- without imu.csv "
                "there is no independent check on the pseudo-GT.")
        if self.use_pose:
            if self.n_pose == 0:
                self.get_logger().error(
                    f"NO messages on {self.args.pose_topic} -- check the topic "
                    "name and that the Vicra node is running. This run has no "
                    "optical tracking.")
            elif self.pose_first_stamp is not None:
                span = self.pose_last_stamp - self.pose_first_stamp
                rate = self.n_pose / span if span > 0 else 0.0
                self.get_logger().info(
                    f"pose: {self.n_pose} samples, {rate:.1f} Hz mean")
                # 60 Hz nominal; a low mean rate means the marker spent a lot
                # of the session occluded, since the node publishes nothing then.
                if rate < 30.0:
                    self.get_logger().warn(
                        f"mean pose rate {rate:.1f} Hz is well under the 60 Hz "
                        "nominal -- the marker was occluded for much of the "
                        "run. Check line of sight to the sensor.")

            total = self.n_pose_filled + self.n_pose_unfilled
            if total:
                pct = 100.0 * self.n_pose_filled / total
                log = self.get_logger().warn if pct < 95.0 else self.get_logger().info
                log(f"frames.csv pose columns filled: {self.n_pose_filled}/{total} "
                    f"({pct:.1f}%)")
                if pct < 95.0:
                    self.get_logger().warn(
                        "blank pose rows mean no sample within "
                        f"{self.args.pose_max_gap * 1e3:.0f} ms -- marker "
                        "occluded, or the tracker and camera clocks disagree")

        if not self.have_info:
            self.get_logger().error(
                "NO camera_info.json -- this run cannot be used for SCR. "
                "Check the /camera/color/camera_info topic name."
            )
        if self.use_us:
            if self.n_us == 0:
                self.get_logger().error(
                    f"NO messages on {self.args.us_topic} -- check the topic "
                    "name with 'ros2 topic list'. This run has no ultrasound.")
            elif len(df) < 0.8 * self.n_us:
                self.get_logger().warn(
                    f"only {len(df)} triples matched from {self.n_us} US "
                    "messages -- slop was too tight or the stamps disagree; "
                    "consider re-recording with a larger --slop")
            if self.args.us_info_topic and not self.have_us_info:
                self.get_logger().warn(
                    "no us_camera_info.json -- pixel spacing unknown, so US "
                    "image coordinates cannot be converted to mm")

        self.get_logger().info(
            f"done: {len(df)} frames, {self.dropped} write-dropped, "
            f"{self.n_imu} imu -> {self.run_dir}"
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="./data/train")
    ap.add_argument("--run", required=True, help="run name, e.g. run_001")
    ap.add_argument("--duration", type=float, default=60.0,    help="auto-stop after N seconds (0 = until Ctrl-C)")
    ap.add_argument("--workers", type=int, default=4,    help="encoder threads; 1080p US PNG is the slow one")
    ap.add_argument("--queue-size", type=int, default=5,    help="per-topic buffer inside the synchronizer")

    ap.add_argument("--no-us", action="store_true", help="RGB-D only, as before")
    ap.add_argument("--us-topic", default="/image_raw")
    ap.add_argument("--us-info-topic", default="/camera_info",    help="empty string to skip")
    ap.add_argument("--us-ext", default="png", choices=["png", "jpg"])
    ap.add_argument("--us-jpeg-quality", type=int, default=95)

    ap.add_argument("--no-pose", action="store_true", help="skip optical marker recording")
    ap.add_argument("--pose-topic", default="/marker_pose")
    ap.add_argument("--pose-max-gap", type=float, default=0.020,    help="max seconds from a frame stamp to a pose sample; beyond this the row stays blank")
    ap.add_argument("--pose-buffer", type=int, default=100,    help="pose ring buffer length (100 = 1.67 s at 60 Hz)")
    ap.add_argument("--pose-units", default="mm", choices=["mm", "m"],    help="units the tracker node publishes; recorded verbatim, noted in record_config.json")

    ap.add_argument("--slop", type=float, default=0.015,   help="sync window in seconds; raise if match rate is low")
    ap.add_argument("--sync-queue", type=int, default=5,    help="per-topic buffer inside the synchronizer")
    args = ap.parse_args()

    rclpy.init()
    node = SyncedImageSaver(args)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.finish()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()