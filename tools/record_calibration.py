"""
Standalone RGB + tracker-pose recorder for hand-eye calibration sessions.

Deliberately independent of record.py: no import, no shared code. A
calibration session only needs colour frames and interpolated marker pose
(calibrate_hand_eye.py detects a ChArUco board in RGB and solves PnP against
it), so this recorder captures nothing else -- no depth, no IMU, no
ultrasound. That also means no cross-stream synchronizer is needed: there is
only one image stream, matched against pose by interpolation, not against a
second image stream by timestamp.


cd ~/Polaris_Vega_VT
python3 vega_rtsp_overlay_ros.py

ros2 launch usb_cam demo_launch.py

ros2 launch realsense2_camera rs_launch.py \
    align_depth.enable:=true \
    enable_gyro:=true enable_accel:=true unite_imu_method:=2 \
    rgb_camera.enable_auto_exposure:=false \
    rgb_camera.exposure:=166 \
    rgb_camera.white_balance:=4600

Usage:
  python3 tools/record_calibration.py --run calib_201 --root ./data \
      --duration 90 --pose-topic /marker_pose

Fix the ChArUco board rigidly somewhere in the room, keep it in view, and
sweep the probe through wide, varied rotations -- calibrate_hand_eye.py's
own self-test and rotational-diversity check both depend on that.

Recording protocol (Oct 2026, from validate_hand_eye.py: the residual grows with speed,
i.e. a camera-tracker time offset and/or motion blur):
  * move SLOWLY, and pause ~1 s still at each of many different orientations
    (validate_hand_eye.py --stationary-deg-s can then solve on still frames only);
  * fixed, short RGB exposure (less blur), the same values as for the dataset;
  * calibrate on the same day as the recordings, without remounting the marker or camera;
  * afterwards check the time offset: tools/validate_hand_eye.py --time-offset-sweep.
frames.csv also has an `rx` column (host receive time), to diagnose clock offsets.
"""

import argparse
import csv
import json
import queue
import threading
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image


class CalibrationRecorder(Node):
    def __init__(self, args):
        super().__init__("calibration_recorder")
        self.args = args
        self.bridge = CvBridge()

        self.run_dir = Path(args.root) / args.run
        self.rgb_dir = self.run_dir / "rgb"
        self.rgb_dir.mkdir(parents=True, exist_ok=True)
        if any(self.rgb_dir.iterdir()):
            raise RuntimeError(f"{self.rgb_dir} is not empty -- pick a new run name")

        self.idx = 0
        self.dropped = 0
        self.n_color = 0
        self.duration = args.duration
        self.t_start = None

        # frames.csv: RGB + pose only, no depth/us columns -- this run exists
        # for hand-eye calibration, not SCR training.
        self.csv_path = self.run_dir / "frames.csv"
        self.csv_file = open(self.csv_path, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(
            ["timestamp", "rgb", "tx", "ty", "tz", "qx", "qy", "qz", "qw", "rx"])
        self.csv_lock = threading.Lock()

        # Ring buffer of recent pose samples, used to interpolate the pose
        # onto each frame's stamp at record time.
        self.pose_buf: deque = deque(maxlen=args.pose_buffer)
        self.pose_lock = threading.Lock()
        self.n_pose = 0
        self.n_pose_filled = 0
        self.n_pose_unfilled = 0
        self.pose_first_stamp = None
        self.pose_last_stamp = None

        self.q: queue.Queue = queue.Queue(maxsize=args.queue_size)
        self.stop_evt = threading.Event()
        self.writer = threading.Thread(target=self._writer_loop, daemon=True)
        self.writer.start()

        self.have_info = False
        self.info_sub = self.create_subscription(
            CameraInfo, "/camera/color/camera_info", self._on_camera_info, 1)

        self.color_sub = self.create_subscription(
            Image, "/camera/color/image_raw", self._on_color, 5)

        self.pose_sub = self.create_subscription(
            PoseStamped, args.pose_topic, self._on_pose, 10)

        self.timer = self.create_timer(5.0, self._report)
        self.get_logger().info(
            f"recording calibration session to {self.run_dir} -- "
            f"pose topic: {args.pose_topic} -- Ctrl-C to stop")
        self.get_logger().info(
            "keep the ChArUco board rigidly fixed in the room and in view; "
            "sweep the probe through wide, varied rotations")

    # ------------------------------------------------------------------ info
    def _on_camera_info(self, msg: CameraInfo):
        if self.have_info:
            return
        info = {
            "width": msg.width, "height": msg.height,
            "fx": msg.k[0], "fy": msg.k[4], "cx": msg.k[2], "cy": msg.k[5],
            "K": list(msg.k), "D": list(msg.d),
            "distortion_model": msg.distortion_model,
        }
        with open(self.run_dir / "camera_info.json", "w") as f:
            json.dump(info, f, indent=2)
        self.have_info = True
        self.destroy_subscription(self.info_sub)
        self.get_logger().info(
            f"intrinsics saved: fx={info['fx']:.1f} cx={info['cx']:.1f} "
            f"{info['width']}x{info['height']}")

    # ------------------------------------------------------------------ pose
    def _on_pose(self, msg: PoseStamped):
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        p, o = msg.pose.position, msg.pose.orientation
        self.n_pose += 1
        if self.pose_first_stamp is None:
            self.pose_first_stamp = t
        self.pose_last_stamp = t
        with self.pose_lock:
            self.pose_buf.append((t, p.x, p.y, p.z, o.x, o.y, o.z, o.w))

    @staticmethod
    def _slerp(q0, q1, u):
        """Spherical linear interpolation, (x, y, z, w) order.

        Component-wise linear interpolation of quaternions does not give a
        rotation; the error grows with the angle between samples.
        """
        q0 = np.asarray(q0, dtype=np.float64)
        q1 = np.asarray(q1, dtype=np.float64)
        dot = float(np.dot(q0, q1))
        if dot < 0.0:
            q1 = -q1
            dot = -dot
        if dot > 0.9995:
            q = q0 + u * (q1 - q0)
            return q / np.linalg.norm(q)
        theta = np.arccos(np.clip(dot, -1.0, 1.0))
        s = np.sin(theta)
        return (np.sin((1.0 - u) * theta) / s) * q0 + (np.sin(u * theta) / s) * q1

    def _lookup_pose(self, t):
        """Pose at time t, interpolated from the ring buffer.

        Returns (values, gap_s), values is [tx,ty,tz,qx,qy,qz,qw] or None if
        no sample is within --pose-max-gap -- a miss means the marker was
        occluded around t, and leaving the row blank is correct: interpolating
        across an occlusion invents a plausible wrong pose.
        """
        with self.pose_lock:
            if not self.pose_buf:
                return None, float("inf")
            buf = list(self.pose_buf)

        ts = [b[0] for b in buf]
        if ts[0] <= t <= ts[-1]:
            hi = int(np.clip(np.searchsorted(ts, t), 1, len(ts) - 1))
            lo = hi - 1
            t0, t1 = ts[lo], ts[hi]
            gap = min(abs(t - t0), abs(t - t1))
            if gap > self.args.pose_max_gap:
                return None, gap
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            a, b = buf[lo], buf[hi]
            xyz = [a[1 + k] + u * (b[1 + k] - a[1 + k]) for k in range(3)]
            quat = self._slerp(a[4:8], b[4:8], u)
            return xyz + [float(v) for v in quat], gap

        nearest = 0 if t < ts[0] else len(ts) - 1
        gap = abs(t - ts[nearest])
        if gap > self.args.pose_max_gap:
            return None, gap
        s = buf[nearest]
        return [s[1], s[2], s[3], s[4], s[5], s[6], s[7]], gap

    # --------------------------------------------------------------- capture
    def _on_color(self, msg: Image):
        if self.t_start is None:
            self.t_start = time.time()
        self.n_color += 1

        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        color = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        pose_vals, _gap = self._lookup_pose(stamp)
        if pose_vals is None:
            self.n_pose_unfilled += 1
        else:
            self.n_pose_filled += 1

        try:
            self.q.put_nowait((self.idx, stamp, color.copy(), pose_vals, time.time()))
            self.idx += 1
        except queue.Full:
            self.dropped += 1

        if self.duration and (time.time() - self.t_start) > self.duration:
            self.get_logger().info("duration reached")
            raise KeyboardInterrupt

    def _writer_loop(self):
        while not self.stop_evt.is_set():
            try:
                idx, stamp, color, pose_vals, rx = self.q.get(timeout=0.2)
            except queue.Empty:
                continue
            rel_rgb = f"rgb/{idx:06d}.png"
            cv2.imwrite(str(self.run_dir / rel_rgb), color)

            if pose_vals is None:
                pose_cells = ["", "", "", "", "", "", ""]
            else:
                pose_cells = [f"{v:.6f}" for v in pose_vals[:3]] + \
                             [f"{v:.9f}" for v in pose_vals[3:]]

            with self.csv_lock:
                self.csv_writer.writerow([f"{stamp:.9f}", rel_rgb] + pose_cells + [f"{rx:.9f}"])
            self.q.task_done()

    def _report(self):
        elapsed = (time.time() - self.t_start) if self.t_start else 0.0
        fps = self.idx / elapsed if elapsed > 0 else 0.0
        total = self.n_pose_filled + self.n_pose_unfilled
        pct = 100.0 * self.n_pose_filled / total if total else 0.0
        msg = (f"{self.idx} frames  {fps:.1f} fps  q={self.q.qsize()}  "
               f"dropped={self.dropped}  pose_filled={pct:.0f}%")
        warn = self.dropped > 0 or (total > 30 and pct < 90.0)
        (self.get_logger().warn if warn else self.get_logger().info)(msg)

    # ---------------------------------------------------------------- finish
    def finish(self):
        self.get_logger().info(f"flushing {self.q.qsize()} queued frames...")
        self.q.join()
        self.stop_evt.set()
        self.writer.join(timeout=2.0)
        with self.csv_lock:
            self.csv_file.close()

        # Writer finishes out of order (single thread here, but keep the same
        # safety net record.py uses).
        import pandas as pd
        df = pd.read_csv(self.csv_path).sort_values("timestamp")
        df.to_csv(self.csv_path, index=False)

        with open(self.run_dir / "record_config.json", "w") as f:
            json.dump({
                "run": self.args.run,
                "purpose": "hand-eye calibration (ChArUco board): RGB + pose "
                           "only, not a training run",
                "frames": len(df),
                "write_dropped": self.dropped,
                "pose": {
                    "topic": self.args.pose_topic,
                    "samples": self.n_pose,
                    "frames_filled": self.n_pose_filled,
                    "frames_unfilled": self.n_pose_unfilled,
                    "max_gap_s": self.args.pose_max_gap,
                    "units": self.args.pose_units,
                    "note": ("Pose columns interpolated onto frame stamps at "
                             "record time (linear translation, slerp "
                             "rotation). Blank rows mean no sample within "
                             "max_gap_s."),
                },
            }, f, indent=2)

        if not self.have_info:
            self.get_logger().error(
                "NO camera_info.json -- check the /camera/color/camera_info "
                "topic name")
        if self.n_pose == 0:
            self.get_logger().error(
                f"NO messages on {self.args.pose_topic} -- check the topic "
                "name and that the tracker node is running")

        total = self.n_pose_filled + self.n_pose_unfilled
        if total and self.n_pose_filled / total < 0.9:
            self.get_logger().warn(
                f"only {self.n_pose_filled}/{total} frames got a pose match "
                "-- check line of sight to the marker")

        self.get_logger().info(f"done: {len(df)} frames -> {self.run_dir}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="./data")
    ap.add_argument("--run", required=True, help="run name, e.g. calib_001")
    ap.add_argument("--duration", type=float, default=90.0,
                    help="auto-stop after N seconds (0 = until Ctrl-C)")
    ap.add_argument("--queue-size", type=int, default=10,
                    help="RGB write queue depth; images accumulate here if the disk can't keep up")
    ap.add_argument("--pose-topic", default="/marker_pose")
    ap.add_argument("--pose-max-gap", type=float, default=0.020,
                    help="max seconds from a frame stamp to a pose sample; beyond this the row stays blank")
    ap.add_argument("--pose-buffer", type=int, default=100,
                    help="pose ring buffer length (100 = 1.67s at 60Hz)")
    ap.add_argument("--pose-units", default="mm", choices=["mm", "m"],
                    help="units the tracker node publishes; recorded verbatim, noted in record_config.json")
    args = ap.parse_args()

    rclpy.init()
    node = CalibrationRecorder(args)
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
