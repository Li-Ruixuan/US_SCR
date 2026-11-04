# Map without a tracker: room-401, room-402, room-403, room-404 (train_4XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 662 | 723/6274 (12 %) | 11.8 / 17.7 | 18.8 / 32.0 | 1.36 | 13.3 / 28.9 | 78.6 |
| round 2 (+ camera calibration) | 5313 | 6036/6274 (96 %) | 10.8 / 21.2 | 14.9 / 26.9 | 1.21 | 10.9 / 29.1 | 39.0 |
| round 3 (+ camera calibration) | 238 | 6274/6274 (100 %) | 11.1 / 21.0 | 15.3 / 26.7 | 1.24 | 10.7 / 28.6 | 33.8 |
| final pass (+ camera calibration) | 6273 | 6274/6274 (100 %) | 9.0 / 15.0 | 15.8 / 21.6 | 1.18 | 6.8 / 20.9 | 33.8 |
| pose graph (+ camera calibration) | 0 | 6274/6274 (100 %) | 4.0 / 7.9 | 5.9 / 8.3 | 0.42 | 1.9 / 4.4 | 33.8 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-pool-4XXB`, or `track --cam-calib runs/map-pool-4XXB/map.json`).

Camera calibration fitted here on one scan alone, errors on the other scan(s) (held out, median): from room-401: 30.4 mm, 2.06 deg -> scene points 3.9 mm, camera 3.2 mm; from room-402: 29.4 mm, 1.90 deg -> scene points 4.2 mm, camera 3.7 mm; from room-403: 32.4 mm, 2.04 deg -> scene points 4.4 mm, camera 3.4 mm; from room-404: 31.1 mm, 1.99 deg -> scene points 4.3 mm, camera 2.9 mm. Similar values from each scan = a property of the probe; different values = the map's own error.

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 30.5 / 1.63, -167: 25.9 / 1.40, -133: 21.2 / 1.16, -100: 16.5 / 0.94, -67: 11.9 / 0.72, -33: 7.5 / 0.53, +0: 4.0 / 0.42, +33: 5.9 / 0.48, +67: 10.4 / 0.66, +100: 15.2 / 0.88, +133: 19.9 / 1.12, +167: 24.5 / 1.35, +200: 29.1 / 1.59. Best +5 ms (no timing offset).

Labels for training: `poses_room-401.json`, `poses_room-402.json`, `poses_room-403.json`, `poses_room-404.json` (`scr_anchor.py train --map runs/map-pool-4XXB`).
