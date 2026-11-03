# Map without a tracker: room-401, room-402 (test_4XXA)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 662 | 723/3893 (19 %) | 12.5 / 21.9 | 18.3 / 29.0 | 1.51 | 13.6 / 28.8 | 78.7 |
| round 2 (+ camera calibration) | 3170 | 3893/3893 (100 %) | 10.3 / 19.6 | 13.3 / 25.9 | 1.19 | 12.3 / 28.8 | 39.5 |
| final pass (+ camera calibration) | 3556 | 3893/3893 (100 %) | 9.0 / 18.3 | 10.8 / 21.1 | 0.95 | 9.4 / 21.9 | 39.5 |
| pose graph (+ camera calibration) | 0 | 3893/3893 (100 %) | 3.9 / 8.7 | 4.8 / 7.0 | 0.35 | 2.4 / 5.2 | 39.5 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-4XXA`, or `track --cam-calib runs/map-4XXA/map.json`).

Camera calibration fitted here on one scan alone, errors on the other scan(s) (held out, median): from room-401: 30.2 mm, 2.05 deg -> scene points 4.0 mm, camera 2.7 mm; from room-402: 29.6 mm, 1.89 deg -> scene points 4.1 mm, camera 3.2 mm. Similar values from each scan = a property of the probe; different values = the map's own error.

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 35.2 / 1.83, -167: 30.0 / 1.56, -133: 24.6 / 1.29, -100: 19.1 / 1.04, -67: 13.7 / 0.77, -33: 8.2 / 0.53, +0: 3.9 / 0.35, +33: 6.2 / 0.44, +67: 11.8 / 0.69, +100: 17.6 / 0.97, +133: 23.2 / 1.24, +167: 28.7 / 1.52, +200: 34.0 / 1.79. Best +5 ms (no timing offset).

Labels for training: `poses_room-401.json`, `poses_room-402.json` (`scr_anchor.py train --map runs/map-4XXA`).
