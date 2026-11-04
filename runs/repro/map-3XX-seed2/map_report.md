# Map without a tracker: room-301, room-302 (train_3XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 2909 | 2970/3356 (88 %) | 8.8 / 30.5 | 10.7 / 31.5 | 0.90 | 9.4 / 25.8 | 73.1 |
| round 2 (+ camera calibration) | 386 | 3356/3356 (100 %) | 9.2 / 27.4 | 11.8 / 28.8 | 0.94 | 9.5 / 25.6 | 42.3 |
| final pass (+ camera calibration) | 3353 | 3356/3356 (100 %) | 5.8 / 12.2 | 7.4 / 15.3 | 0.63 | 5.4 / 14.2 | 42.3 |
| pose graph (+ camera calibration) | 0 | 3356/3356 (100 %) | 2.7 / 5.5 | 1.9 / 3.3 | 0.19 | 1.4 / 3.4 | 42.3 |

Camera calibration from the room scan (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.4 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/repro/map-3XX-seed2`, or `track --cam-calib runs/repro/map-3XX-seed2/map.json`).

Camera calibration fitted here on one scan alone, errors on the other scan(s) (held out, median): from room-301: 32.2 mm, 1.53 deg -> scene points 3.0 mm, camera 2.0 mm; from room-302: 31.0 mm, 1.57 deg -> scene points 2.9 mm, camera 2.1 mm. Similar values from each scan = a property of the probe; different values = the map's own error.

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 22.6 / 1.42, -167: 19.2 / 1.20, -133: 15.8 / 0.99, -100: 12.1 / 0.76, -67: 8.6 / 0.55, -33: 5.2 / 0.34, +0: 2.6 / 0.18, +33: 3.7 / 0.25, +67: 6.9 / 0.45, +100: 10.4 / 0.67, +133: 14.0 / 0.89, +167: 17.7 / 1.11, +200: 21.0 / 1.32. Best +7 ms (no timing offset).

Labels for training: `poses_room-301.json`, `poses_room-302.json` (`scr_anchor.py train --map runs/repro/map-3XX-seed2`).
