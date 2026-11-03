# Map without a tracker: room-301, room-302 (train_3XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 3037 | 3098/3356 (92 %) | 9.5 / 27.8 | 11.3 / 30.5 | 1.01 | 9.3 / 31.4 | 73.9 |
| round 2 (+ camera calibration) | 258 | 3356/3356 (100 %) | 9.8 / 26.2 | 11.0 / 30.1 | 1.05 | 9.6 / 30.4 | 44.1 |
| final pass (+ camera calibration) | 3343 | 3356/3356 (100 %) | 6.7 / 12.7 | 9.5 / 18.2 | 0.89 | 5.8 / 16.9 | 44.1 |
| pose graph (+ camera calibration) | 0 | 3356/3356 (100 %) | 2.6 / 5.4 | 2.0 / 4.1 | 0.19 | 1.5 / 3.7 | 44.1 |

Camera calibration from the room scan (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/repro/map-3XX`, or `track --cam-calib runs/repro/map-3XX/map.json`).

Camera calibration fitted here on one scan alone, errors on the other scan(s) (held out, median): from room-301: 32.8 mm, 1.52 deg -> scene points 2.9 mm, camera 1.9 mm; from room-302: 31.0 mm, 1.57 deg -> scene points 2.9 mm, camera 2.4 mm. Similar values from each scan = a property of the probe; different values = the map's own error.

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 22.6 / 1.42, -167: 19.2 / 1.21, -133: 15.7 / 0.99, -100: 12.1 / 0.77, -67: 8.5 / 0.55, -33: 5.2 / 0.34, +0: 2.6 / 0.18, +33: 3.7 / 0.26, +67: 6.9 / 0.45, +100: 10.4 / 0.67, +133: 14.0 / 0.89, +167: 17.7 / 1.10, +200: 21.1 / 1.32. Best +7 ms (no timing offset).

Labels for training: `poses_room-301.json`, `poses_room-302.json` (`scr_anchor.py train --map runs/repro/map-3XX`).
