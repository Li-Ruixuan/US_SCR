# Map without a tracker: room-501, room-502 (test_5XXA)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 2955 | 3016/5391 (56 %) | 10.2 / 18.1 | 20.4 / 34.1 | 1.08 | 11.7 / 28.0 | 72.0 |
| round 2 (+ camera calibration) | 2374 | 5390/5391 (100 %) | 10.7 / 18.8 | 20.4 / 35.7 | 1.22 | 12.0 / 31.0 | 36.8 |
| round 3 (+ camera calibration) | 1 | 5391/5391 (100 %) | 10.7 / 18.8 | 20.5 / 35.7 | 1.22 | 12.0 / 31.0 | 28.8 |
| final pass (+ camera calibration) | 5322 | 5391/5391 (100 %) | 7.2 / 13.5 | 19.6 / 30.9 | 1.10 | 8.2 / 21.5 | 28.8 |
| pose graph (+ camera calibration) | 0 | 5391/5391 (100 %) | 4.4 / 9.0 | 3.4 / 9.1 | 0.40 | 2.9 / 8.0 | 28.8 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-5XXA-both`, or `track --cam-calib runs/map-5XXA-both/map.json`).

Camera calibration fitted here on one scan alone, errors on the other scan(s) (held out, median): from room-501: 31.9 mm, 2.00 deg -> scene points 4.3 mm, camera 4.1 mm; from room-502: 32.9 mm, 2.48 deg -> scene points 5.9 mm, camera 5.2 mm. Similar values from each scan = a property of the probe; different values = the map's own error.

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 19.3 / 1.18, -167: 16.5 / 1.02, -133: 13.8 / 0.87, -100: 10.9 / 0.72, -67: 8.2 / 0.59, -33: 5.8 / 0.48, +0: 4.4 / 0.40, +33: 5.1 / 0.41, +67: 7.4 / 0.49, +100: 10.0 / 0.63, +133: 12.7 / 0.77, +167: 15.4 / 0.91, +200: 18.5 / 1.07. Best +5 ms (no timing offset).

Labels for training: `poses_room-501.json`, `poses_room-502.json` (`scr_anchor.py train --map runs/map-5XXA-both`).
