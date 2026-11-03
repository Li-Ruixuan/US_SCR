# Map without a tracker: room-301, room-302 (train_3XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 3037 | 3098/3356 (92 %) | 9.5 / 27.8 | 11.3 / 30.5 | 1.01 | 9.3 / 31.4 | 73.9 |
| round 2 (+ camera calibration) | 258 | 3356/3356 (100 %) | 9.8 / 26.2 | 11.0 / 30.1 | 1.05 | 9.6 / 30.4 | 44.1 |
| final pass (+ camera calibration) | 3343 | 3356/3356 (100 %) | 6.7 / 12.7 | 9.5 / 18.2 | 0.89 | 5.8 / 16.9 | 44.1 |
| pose graph (+ camera calibration) | 0 | 3356/3356 (100 %) | 2.6 / 5.4 | 2.0 / 4.1 | 0.19 | 1.5 / 3.7 | 44.1 |
| pose graph (from map-3XX) (+ camera calibration) |  | 3356/3356 (100 %) | 4.5 / 7.7 | 5.2 / 9.5 | 0.55 | 1.5 / 3.8 |  |

Camera calibration from the room scan (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 32.3 mm, 1.49 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/repro/map-3XX-noloops`, or `track --cam-calib runs/repro/map-3XX-noloops/map.json`).

Camera calibration fitted here on one scan alone, errors on the other scan(s) (held out, median): from room-301: 31.1 mm, 1.55 deg -> scene points 6.0 mm, camera 7.6 mm; from room-302: 31.8 mm, 1.72 deg -> scene points 7.2 mm, camera 8.8 mm. Similar values from each scan = a property of the probe; different values = the map's own error.

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 22.3 / 1.50, -167: 19.0 / 1.28, -133: 15.6 / 1.07, -100: 12.2 / 0.89, -67: 9.0 / 0.72, -33: 6.2 / 0.59, +0: 4.4 / 0.54, +33: 5.2 / 0.57, +67: 7.8 / 0.64, +100: 11.1 / 0.80, +133: 14.4 / 0.98, +167: 17.8 / 1.17, +200: 21.1 / 1.36. Best +6 ms (no timing offset).

Labels for training: `poses_room-301.json`, `poses_room-302.json` (`scr_anchor.py train --map runs/repro/map-3XX-noloops`).
