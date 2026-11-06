# Map without a tracker: room-502 (test_5XXA)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 2216 | 2277/2694 (85 %) | 7.2 / 13.4 | 16.4 / 26.9 | 1.05 | 7.7 / 18.5 | 74.8 |
| round 2 (+ camera calibration) | 417 | 2694/2694 (100 %) | 7.4 / 14.1 | 19.7 / 29.6 | 1.26 | 8.4 / 21.0 | 27.9 |
| final pass (+ camera calibration) | 2686 | 2694/2694 (100 %) | 5.3 / 11.2 | 13.1 / 20.8 | 0.84 | 5.8 / 14.8 | 27.9 |
| pose graph (+ camera calibration) | 0 | 2694/2694 (100 %) | 3.5 / 8.8 | 2.7 / 6.9 | 0.36 | 2.2 / 5.8 | 27.9 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-5XXA-exam`, or `track --cam-calib runs/map-5XXA-exam/map.json`).

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 16.5 / 0.95, -167: 14.2 / 0.84, -133: 11.9 / 0.70, -100: 9.5 / 0.57, -67: 7.1 / 0.47, -33: 4.8 / 0.40, +0: 3.5 / 0.36, +33: 4.1 / 0.40, +67: 5.8 / 0.49, +100: 7.8 / 0.58, +133: 10.0 / 0.69, +167: 12.1 / 0.80, +200: 14.5 / 0.93. Best +6 ms (no timing offset).

Labels for training: `poses_room-502.json` (`scr_anchor.py train --map runs/map-5XXA-exam`).
