"""
RGB-D + ultrasound + tracker recorder for RealSense under ROS 2 (layout 2, Oct 2026).

Every stream is saved on its own, with its header stamp and its receive time; nothing is
matched or thrown away at record time. tools/match_streams.py then builds frames.csv
offline (it runs automatically at the end; rerun it any time with other settings).
Changes from layout 1, and why:
  * raw depth (/camera/depth/image_rect_raw) + depth intrinsics + depth->colour extrinsics,
    aligned offline: the live aligned-depth topic sometimes delivered raw 848x480 frames
    that were saved unchecked (1-2 % of frames lost, and misaligned);
  * no online 3-stream synchronizer: it kept only ~85 % of RGB frames (15 ms slop,
    queue 5) and made the frame timing irregular;
  * receive time logged next to every header stamp, to diagnose clock problems;
  * IMU recorded: match_streams.py measures the tracker clock offset from the gyro.

Start the nodes (one terminal each):

cd ~/Polaris_Vega_VT
python3 vega_rtsp_overlay_ros.py

ros2 launch usb_cam demo_launch.py

ros2 launch realsense2_camera rs_launch.py \
    align_depth.enable:=true \
    enable_gyro:=true enable_accel:=true unite_imu_method:=2 \
    rgb_camera.enable_auto_exposure:=false \
    rgb_camera.exposure:=166 \
    rgb_camera.white_balance:=4600

For layout 2 (raw depth, aligned offline) the RealSense line changes to:
    align_depth.enable:=false global_time_enabled:=true
(and rgb_camera.enable_auto_white_balance:=false if your version has it). Put real numbers for
exposure / white balance and keep them for the whole dataset. Global time puts the RealSense
stamps on the host clock, like the US and tracker nodes. Parameter names differ between
realsense-ros versions: check with `ros2 param list`. With --aligned-depth keep
align_depth.enable:=true, as in your original line above.

Usage:
  python3 tools/record_train.py --run run-113 --root ./data/train --duration 60
  python3 tools/record_train.py --run room-103 --no-us            # room scan
  python3 tools/record_train.py --run run-114 --aligned-depth     # old aligned-depth topic
"""

import argparse
import collections
import csv
import json
import queue
import threading
import time
from pathlib import Path

import cv2
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import CameraInfo, Image, Imu

try:
    from realsense2_camera_msgs.msg import Extrinsics
except ImportError:                         # message package missing: use --extrinsics-file
    Extrinsics = None


def stamp_of(msg):
    return msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9


class StreamRecorder(Node):
    def __init__(self, args):
        super().__init__("stream_recorder")
        self.args = args
        self.bridge = CvBridge()
        self.use_us, self.use_pose = not args.no_us, not args.no_pose
        self.raw_depth = not args.aligned_depth
        self.run_dir = Path(args.root) / args.run
        if self.run_dir.exists() and any(self.run_dir.iterdir()):
            raise RuntimeError(f"{self.run_dir} is not empty -- pick a new run name")

        self.streams = ["rgb", "depth"] + (["us"] if self.use_us else [])
        self.dirs = {"rgb": "rgb", "depth": "depth_raw" if self.raw_depth else "depth", "us": "us"}
        for s in self.streams:
            (self.run_dir / self.dirs[s]).mkdir(parents=True, exist_ok=True)
        self.files, self.writers, self.locks = {}, {}, {}
        header = {"rgb": ["idx", "timestamp", "rx", "file"],
                  "depth": ["idx", "timestamp", "rx", "file", "width", "height"],
                  "us": ["idx", "timestamp", "rx", "file"]}
        for s in self.streams:
            self.files[s] = open(self.run_dir / f"{s}.csv", "w", newline="")
            self.writers[s] = csv.writer(self.files[s])
            self.writers[s].writerow(header[s])
            self.locks[s] = threading.Lock()
        self.count = collections.Counter()          # arrivals per stream
        self.saved = collections.Counter()
        self.dropped = collections.Counter()
        self.depth_sizes = collections.Counter()

        self.imu_file = open(self.run_dir / "imu.csv", "w")
        self.imu_file.write("timestamp,rx,gx,gy,gz,ax,ay,az\n")
        self.pose_file = None
        if self.use_pose:
            self.pose_file = open(self.run_dir / "pose.csv", "w")
            self.pose_file.write("timestamp,rx,tx,ty,tz,qx,qy,qz,qw\n")

        self.q = queue.Queue(maxsize=args.queue_size)
        self.stop_evt = threading.Event()
        self.threads = [threading.Thread(target=self._writer_loop, daemon=True) for _ in range(args.workers)]
        for t in self.threads:
            t.start()

        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                             reliability=ReliabilityPolicy.RELIABLE)
        self.have = {"color_info": False, "depth_info": False, "extrinsics": False}
        self.create_subscription(CameraInfo, "/camera/color/camera_info", self._on_color_info, 1)
        if self.raw_depth:
            self.create_subscription(CameraInfo, "/camera/depth/camera_info", self._on_depth_info, 1)
            if Extrinsics is not None:
                self.create_subscription(Extrinsics, args.extrinsics_topic, self._on_extrinsics, latched)

        self.create_subscription(Image, "/camera/color/image_raw", lambda m: self._on_image("rgb", m), 30)
        depth_topic = "/camera/depth/image_rect_raw" if self.raw_depth else "/camera/aligned_depth_to_color/image_raw"
        self.create_subscription(Image, depth_topic, lambda m: self._on_image("depth", m), 30)
        if self.use_us:
            self.create_subscription(Image, args.us_topic, lambda m: self._on_image("us", m), 30)
        self.create_subscription(Imu, "/camera/imu", self._on_imu, 400)
        if self.use_pose:
            self.create_subscription(PoseStamped, args.pose_topic, self._on_pose, 100)

        self.t_start = None
        self.create_timer(10.0, self._report)
        self.get_logger().info(f"recording every stream separately to {self.run_dir} "
                               f"(depth: {'raw, aligned offline' if self.raw_depth else 'aligned topic'})")

    # ---------------------------------------------------------------- info topics
    def _save_json(self, name, d):
        with open(self.run_dir / name, "w") as f:
            json.dump(d, f, indent=2)

    def _on_color_info(self, msg):
        if self.have["color_info"]:
            return
        self._save_json("camera_info.json", {
            "width": msg.width, "height": msg.height, "fx": msg.k[0], "fy": msg.k[4], "cx": msg.k[2],
            "cy": msg.k[5], "K": list(msg.k), "D": list(msg.d), "distortion_model": msg.distortion_model,
            "depth_scale": self.args.depth_scale})
        self.have["color_info"] = True

    def _on_depth_info(self, msg):
        if self.have["depth_info"]:
            return
        self._save_json("depth_camera_info.json", {
            "width": msg.width, "height": msg.height, "K": list(msg.k), "D": list(msg.d),
            "distortion_model": msg.distortion_model, "depth_scale": self.args.depth_scale})
        self.have["depth_info"] = True

    def _on_extrinsics(self, msg):
        if self.have["extrinsics"]:
            return
        self._save_json("depth_to_color.json", {
            "rotation": list(msg.rotation), "translation": list(msg.translation),
            "translation_units": "m", "rotation_order": "column-major (librealsense rs2_extrinsics)",
            "source": self.args.extrinsics_topic})
        self.have["extrinsics"] = True

    # ---------------------------------------------------------------- streams
    def _on_image(self, stream, msg):
        rx = time.time()
        if stream == "rgb":
            if self.t_start is None:
                self.t_start = rx
            self._check_duration(rx)
        idx = self.count[stream]
        self.count[stream] += 1
        enc = "bgr8" if stream == "rgb" else "passthrough"
        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding=enc).copy()
        try:
            self.q.put_nowait((stream, idx, stamp_of(msg), rx, img))
        except queue.Full:
            self.dropped[stream] += 1

    def _on_imu(self, msg):
        g, a = msg.angular_velocity, msg.linear_acceleration
        self.imu_file.write(f"{stamp_of(msg):.9f},{time.time():.9f},{g.x:.6f},{g.y:.6f},{g.z:.6f},"
                            f"{a.x:.6f},{a.y:.6f},{a.z:.6f}\n")
        self.count["imu"] += 1

    def _on_pose(self, msg):
        p, o = msg.pose.position, msg.pose.orientation
        self.pose_file.write(f"{stamp_of(msg):.9f},{time.time():.9f},{p.x:.6f},{p.y:.6f},{p.z:.6f},"
                             f"{o.x:.9f},{o.y:.9f},{o.z:.9f},{o.w:.9f}\n")
        self.count["pose"] += 1

    def _check_duration(self, now):
        if not self.args.duration or self.t_start is None:
            return
        if now - self.t_start > self.args.duration:
            raise KeyboardInterrupt

    def _writer_loop(self):
        us_params = ([cv2.IMWRITE_PNG_COMPRESSION, 1] if self.args.us_ext == "png"
                     else [cv2.IMWRITE_JPEG_QUALITY, self.args.us_jpeg_quality])
        while not self.stop_evt.is_set():
            try:
                stream, idx, stamp, rx, img = self.q.get(timeout=0.2)
            except queue.Empty:
                continue
            ext = self.args.us_ext if stream == "us" else "png"
            rel = f"{self.dirs[stream]}/{idx:06d}.{ext}"
            params = us_params if stream == "us" else [cv2.IMWRITE_PNG_COMPRESSION, 1]
            cv2.imwrite(str(self.run_dir / rel), img, params)
            row = [idx, f"{stamp:.9f}", f"{rx:.9f}", rel]
            if stream == "depth":
                row += [img.shape[1], img.shape[0]]
                self.depth_sizes[f"{img.shape[1]}x{img.shape[0]}"] += 1
            with self.locks[stream]:
                self.writers[stream].writerow(row)
            self.saved[stream] += 1
            self.q.task_done()

    def _report(self):
        el = time.time() - self.t_start if self.t_start else 0.0
        rates = " ".join(f"{s}={self.count[s] / el:.1f}Hz" for s in self.streams + ["imu", "pose"] if el > 0)
        drop = sum(self.dropped.values())
        msg = f"t={el:.0f}s {rates} queue={self.q.qsize()} dropped={dict(self.dropped)}"
        (self.get_logger().warn if drop else self.get_logger().info)(
            msg + ("  <-- writers falling behind: more --workers or a faster disk" if drop else ""))

    # ---------------------------------------------------------------- finish
    def finish(self):
        self.get_logger().info(f"flushing {self.q.qsize()} queued images...")
        self.q.join()
        self.stop_evt.set()
        for t in self.threads:
            t.join(timeout=2.0)
        for f in self.files.values():
            f.close()
        self.imu_file.close()
        if self.pose_file:
            self.pose_file.close()
        if self.raw_depth and not self.have["extrinsics"] and self.args.extrinsics_file:
            ext = json.load(open(self.args.extrinsics_file))
            self._save_json("depth_to_color.json", ext)
            self.have["extrinsics"] = True

        el = (time.time() - self.t_start) if self.t_start else 0.0
        summary = {
            "run": self.args.run, "layout_version": 2, "duration_s": el,
            "arrivals": dict(self.count), "saved": dict(self.saved), "write_dropped": dict(self.dropped),
            "rate_hz": {s: (self.count[s] / el if el else 0.0) for s in self.streams + ["imu", "pose"]},
            "depth": {"mode": "raw" if self.raw_depth else "aligned topic", "sizes": dict(self.depth_sizes)},
            "info_received": self.have,
            "us": {"enabled": self.use_us, "topic": self.args.us_topic if self.use_us else None,
                   "ext": self.args.us_ext},
            "pose": {"enabled": self.use_pose, "topic": self.args.pose_topic if self.use_pose else None,
                     "units": self.args.pose_units, "samples": self.count["pose"]},
            "note": "Every stream saved separately (header stamp + receive time 'rx'). frames.csv is built "
                    "offline by tools/match_streams.py; see match_report.json.",
        }
        self._save_json("record_config.json", summary)

        warn = self.get_logger().warn
        if not self.have["color_info"]:
            warn("NO camera_info.json: check /camera/color/camera_info")
        if self.raw_depth and not (self.have["depth_info"] and self.have["extrinsics"]):
            warn("raw depth recorded, but depth_camera_info.json or depth_to_color.json is missing: "
                 "depth cannot be aligned. Get the extrinsics with "
                 f"`ros2 topic echo --once {self.args.extrinsics_topic}` and pass --extrinsics-file, "
                 "or record with --aligned-depth")
        if len(self.depth_sizes) > 1:
            warn(f"depth images of several sizes: {dict(self.depth_sizes)}")
        if self.count["imu"] == 0:
            warn("NO IMU samples: launch with enable_gyro:=true enable_accel:=true unite_imu_method:=2")
        if self.use_pose and self.count["pose"] == 0:
            warn(f"NO messages on {self.args.pose_topic}: no tracking in this run")
        if self.use_us and self.count["us"] == 0:
            warn(f"NO messages on {self.args.us_topic}: no ultrasound in this run")
        self.get_logger().info("done: " + ", ".join(f"{s} {self.saved[s]}" for s in self.streams)
                               + f", imu {self.count['imu']}, pose {self.count['pose']} -> {self.run_dir}")

        if not self.args.no_match:
            try:
                from match_streams import match
                match(self.run_dir, apply_sync=False)
            except Exception as e:                   # never lose a recording to a matching error
                warn(f"matching failed ({e}); run `python3 tools/match_streams.py {self.run_dir}` later")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="./data/train")
    ap.add_argument("--run", required=True, help="run name, e.g. run-113 or room-103")
    ap.add_argument("--duration", type=float, default=60.0, help="seconds of sweep; 0 = until Ctrl-C")
    ap.add_argument("--workers", type=int, default=6, help="image writer threads")
    ap.add_argument("--queue-size", type=int, default=300, help="images waiting to be written (all streams)")
    ap.add_argument("--aligned-depth", action="store_true",
                    help="record the live aligned-depth topic instead of raw depth (layout 1 behaviour)")
    ap.add_argument("--depth-scale", type=float, default=0.001, help="metres per depth unit (RealSense D4xx: 0.001)")
    ap.add_argument("--extrinsics-topic", default="/camera/extrinsics/depth_to_color")
    ap.add_argument("--extrinsics-file", default="",
                    help="depth_to_color.json to use if the extrinsics topic is not received")
    ap.add_argument("--no-us", action="store_true", help="room scans: no ultrasound stream")
    ap.add_argument("--us-topic", default="/image_raw")
    ap.add_argument("--us-ext", default="png", choices=["png", "jpg"])
    ap.add_argument("--us-jpeg-quality", type=int, default=95)
    ap.add_argument("--no-pose", action="store_true")
    ap.add_argument("--pose-topic", default="/marker_pose")
    ap.add_argument("--pose-units", default="mm", choices=["mm", "m"])
    ap.add_argument("--no-match", action="store_true", help="do not build frames.csv at the end")
    args = ap.parse_args()

    rclpy.init()
    node = StreamRecorder(args)
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
