# Map without a tracker: room-401, room-402, room-403, room-404, room-405, room-406 (train_4XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 662 | 723/8671 (8 %) | 11.4 / 19.7 | 15.5 / 28.2 | 1.33 | 12.6 / 23.9 | 78.8 |
| round 2 (+ camera calibration) | 5735 | 6458/8671 (74 %) | 11.6 / 24.8 | 12.5 / 26.9 | 0.95 | 9.9 / 26.7 | 39.2 |
| round 3 (+ camera calibration) | 2213 | 8671/8671 (100 %) | 12.2 / 23.9 | 13.3 / 26.8 | 0.95 | 9.5 / 26.1 | 35.4 |
| final pass (+ camera calibration) | 8553 | 8671/8671 (100 %) | 9.5 / 17.0 | 11.2 / 19.8 | 0.75 | 7.5 / 20.9 | 35.4 |
| pose graph (+ camera calibration) | 0 | 8671/8671 (100 %) | 4.3 / 8.2 | 5.7 / 8.9 | 0.38 | 1.9 / 4.2 | 35.4 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-pool-4XXC`, or `track --cam-calib runs/map-pool-4XXC/map.json`).

Camera calibration fitted here on one scan alone, errors on the other scan(s) (held out, median): from room-401: 30.2 mm, 2.05 deg -> scene points 4.2 mm, camera 4.4 mm; from room-402: 29.1 mm, 1.90 deg -> scene points 4.8 mm, camera 4.7 mm; from room-403: 32.6 mm, 2.06 deg -> scene points 4.7 mm, camera 4.5 mm; from room-404: 31.3 mm, 2.00 deg -> scene points 4.7 mm, camera 4.1 mm; from room-405: 33.9 mm, 2.07 deg -> scene points 5.4 mm, camera 6.6 mm; from room-406: 31.4 mm, 2.00 deg -> scene points 4.7 mm, camera 6.7 mm. Similar values from each scan = a property of the probe; different values = the map's own error.

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 28.4 / 1.52, -167: 24.2 / 1.30, -133: 19.9 / 1.08, -100: 15.7 / 0.87, -67: 11.6 / 0.66, -33: 7.5 / 0.48, +0: 4.3 / 0.38, +33: 6.0 / 0.44, +67: 9.7 / 0.62, +100: 14.0 / 0.82, +133: 18.3 / 1.04, +167: 22.5 / 1.27, +200: 26.8 / 1.49. Best +5 ms (no timing offset).

Labels for training: `poses_room-401.json`, `poses_room-402.json`, `poses_room-403.json`, `poses_room-404.json`, `poses_room-405.json`, `poses_room-406.json` (`scr_anchor.py train --map runs/map-pool-4XXC`).
