# Map without a tracker: room-405, room-406 (test_4XXC)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 2163 | 2224/2397 (93 %) | 14.4 / 34.0 | 14.4 / 39.3 | 1.12 | 7.8 / 29.6 | 72.3 |
| round 2 (+ camera calibration) | 173 | 2397/2397 (100 %) | 15.2 / 33.8 | 14.4 / 39.2 | 1.14 | 8.6 / 33.1 | 36.9 |
| final pass (+ camera calibration) | 2397 | 2397/2397 (100 %) | 9.7 / 21.2 | 7.8 / 24.1 | 0.70 | 6.5 / 19.0 | 36.9 |
| pose graph (+ camera calibration) | 0 | 2397/2397 (100 %) | 3.5 / 7.2 | 3.4 / 5.0 | 0.23 | 1.7 / 3.7 | 36.9 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-4XXC`, or `track --cam-calib runs/map-4XXC/map.json`).

Camera calibration fitted here on one scan alone, errors on the other scan(s) (held out, median): from room-405: 33.8 mm, 2.02 deg -> scene points 3.5 mm, camera 1.5 mm; from room-406: 31.1 mm, 1.97 deg -> scene points 3.6 mm, camera 1.9 mm. Similar values from each scan = a property of the probe; different values = the map's own error.

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 23.6 / 1.28, -167: 20.0 / 1.10, -133: 16.4 / 0.91, -100: 13.0 / 0.72, -67: 9.6 / 0.52, -33: 6.5 / 0.36, +0: 3.6 / 0.23, +33: 4.4 / 0.30, +67: 7.6 / 0.45, +100: 11.0 / 0.63, +133: 14.4 / 0.83, +167: 17.8 / 1.02, +200: 21.1 / 1.20. Best +9 ms (no timing offset).

Labels for training: `poses_room-405.json`, `poses_room-406.json` (`scr_anchor.py train --map runs/map-4XXC`).
