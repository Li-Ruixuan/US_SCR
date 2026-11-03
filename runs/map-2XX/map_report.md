# Map without a tracker: room-201, room-202 (train_2XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 2502 | 2563/5366 (48 %) | 12.9 / 23.1 | 18.6 / 41.3 | 1.27 | 12.7 / 35.6 | 86.5 |
| round 2 (+ camera calibration) | 2725 | 5288/5366 (99 %) | 13.7 / 26.9 | 22.1 / 41.9 | 1.43 | 15.9 / 46.7 | 51.2 |
| round 3 (+ camera calibration) | 74 | 5362/5366 (100 %) | 13.9 / 26.9 | 22.5 / 42.6 | 1.45 | 16.2 / 47.6 | 39.5 |
| round 4 (+ camera calibration) | 2 | 5364/5366 (100 %) | 13.9 / 27.0 | 22.5 / 42.6 | 1.45 | 16.2 / 47.6 | 33.1 |
| final pass (+ camera calibration) | 5327 | 5365/5366 (100 %) | 11.3 / 24.1 | 20.2 / 35.4 | 1.46 | 13.1 / 41.3 | 33.1 |
| pose graph (+ camera calibration) | 0 | 5365/5366 (100 %) | 6.7 / 12.9 | 8.3 / 14.3 | 0.64 | 3.6 / 31.2 | 33.1 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-2XX`, or `track --cam-calib runs/map-2XX/map.json`).

Camera calibration fitted here on one scan alone, errors on the other scan(s) (held out, median): from room-201: 31.7 mm, 0.93 deg -> scene points 6.9 mm, camera 8.1 mm; from room-202: 31.8 mm, 1.89 deg -> scene points 8.8 mm, camera 8.4 mm. Similar values from each scan = a property of the probe; different values = the map's own error.

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 37.8 / 2.31, -167: 32.2 / 1.98, -133: 26.6 / 1.66, -100: 21.1 / 1.35, -67: 15.7 / 1.03, -33: 10.3 / 0.78, +0: 6.7 / 0.64, +33: 8.6 / 0.74, +67: 14.0 / 1.05, +100: 19.5 / 1.39, +133: 25.2 / 1.72, +167: 30.8 / 2.05, +200: 36.0 / 2.38. Best +5 ms (no timing offset).

Labels for training: `poses_room-201.json`, `poses_room-202.json` (`scr_anchor.py train --map runs/map-2XX`).
