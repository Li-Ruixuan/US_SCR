# Map without a tracker: room-301, room-302 (train_3XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 2880 | 2941/3356 (88 %) | 9.4 / 23.8 | 10.9 / 38.3 | 1.01 | 8.8 / 25.2 | 73.4 |
| round 2 (+ camera calibration) | 415 | 3356/3356 (100 %) | 9.3 / 22.5 | 11.5 / 35.7 | 1.03 | 8.6 / 26.4 | 42.5 |
| final pass (+ camera calibration) | 3348 | 3356/3356 (100 %) | 6.5 / 13.4 | 10.8 / 19.3 | 0.81 | 6.6 / 20.4 | 42.5 |
| pose graph (+ camera calibration) | 0 | 3356/3356 (100 %) | 2.7 / 5.4 | 2.0 / 3.7 | 0.19 | 1.5 / 3.7 | 42.5 |

Camera calibration from the room scan (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.2 mm, 1.52 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/repro/map-3XX-seed1`, or `track --cam-calib runs/repro/map-3XX-seed1/map.json`).

Camera calibration fitted here on one scan alone, errors on the other scan(s) (held out, median): from room-301: 32.2 mm, 1.54 deg -> scene points 3.0 mm, camera 2.0 mm; from room-302: 30.6 mm, 1.57 deg -> scene points 2.9 mm, camera 2.4 mm. Similar values from each scan = a property of the probe; different values = the map's own error.

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 22.6 / 1.42, -167: 19.2 / 1.20, -133: 15.8 / 0.98, -100: 12.1 / 0.76, -67: 8.5 / 0.55, -33: 5.2 / 0.34, +0: 2.7 / 0.19, +33: 3.7 / 0.26, +67: 7.0 / 0.45, +100: 10.4 / 0.67, +133: 14.0 / 0.89, +167: 17.7 / 1.11, +200: 21.1 / 1.33. Best +7 ms (no timing offset).

Labels for training: `poses_room-301.json`, `poses_room-302.json` (`scr_anchor.py train --map runs/repro/map-3XX-seed1`).
