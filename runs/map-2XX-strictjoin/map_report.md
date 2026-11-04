# Map without a tracker: room-201, room-202 (train_2XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 309 | 370/5366 (7 %) | 8.5 / 17.1 | 11.4 / 26.6 | 0.72 | 13.2 / 39.7 | 86.4 |
| round 2 (+ camera calibration) | 3333 | 3703/5366 (69 %) | 13.3 / 25.1 | 19.3 / 36.3 | 1.47 | 12.9 / 39.5 | 33.1 |
| round 3 (+ camera calibration) | 1571 | 5274/5366 (98 %) | 15.9 / 31.0 | 20.1 / 47.0 | 1.41 | 16.0 / 48.1 | 40.9 |
| round 4 (+ camera calibration) | 61 | 5335/5366 (99 %) | 16.0 / 31.1 | 20.2 / 47.0 | 1.42 | 16.2 / 48.6 | 37.7 |
| round 5 (+ camera calibration) | 6 | 5341/5366 (100 %) | 16.0 / 31.0 | 20.2 / 47.0 | 1.42 | 16.3 / 48.6 | 32.4 |
| final pass (+ camera calibration) | 4944 | 5344/5366 (100 %) | 13.1 / 26.6 | 13.5 / 35.0 | 1.26 | 11.8 / 34.8 | 32.4 |
| pose graph (+ camera calibration) | 0 | 5344/5366 (100 %) | 9.2 / 19.2 | 10.7 / 31.2 | 0.91 | 5.7 / 32.2 | 32.4 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-2XX-strictjoin`, or `track --cam-calib runs/map-2XX-strictjoin/map.json`).

Camera calibration fitted here on one scan alone, errors on the other scan(s) (held out, median): from room-201: 36.0 mm, 1.03 deg -> scene points 12.3 mm, camera 15.3 mm; from room-202: 34.8 mm, 1.65 deg -> scene points 15.1 mm, camera 12.7 mm. Similar values from each scan = a property of the probe; different values = the map's own error.

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 37.7 / 2.51, -167: 32.3 / 2.20, -133: 27.2 / 1.90, -100: 22.1 / 1.59, -67: 17.3 / 1.28, -33: 12.3 / 1.03, +0: 9.1 / 0.90, +33: 11.1 / 0.99, +67: 16.0 / 1.24, +100: 21.6 / 1.55, +133: 27.0 / 1.89, +167: 32.3 / 2.20, +200: 37.6 / 2.51. Best +4 ms (no timing offset).

Labels for training: `poses_room-201.json`, `poses_room-202.json` (`scr_anchor.py train --map runs/map-2XX-strictjoin`).
