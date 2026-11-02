# Map without a tracker: room-301, room-302 (train_3XX)

The SCR network built the room-scan poses from one seed frame (scr_map.py). Error against Polaris after one rigid alignment of the whole map; 1 s motion = error of the relative pose between frames 30 rows apart.

| stage | frames added | mapped | position mm (median / p90) | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|
| round 1 | 2887 | 2948/3356 (88 %) | 12.7 / 33.7 | 23.31 | 9.2 / 31.5 | 74.1 |
| round 2 | 408 | 3356/3356 (100 %) | 12.9 / 32.7 | 23.47 | 9.5 / 32.8 | 42.3 |
| final pass | 3349 | 3356/3356 (100 %) | 8.4 / 16.6 | 17.25 | 6.1 / 17.3 | 42.3 |
| refined | 0 | 3356/3356 (100 %) | 8.9 / 16.9 | 17.45 | 7.2 / 18.5 | 22.1 |

Labels for training: `poses_room-301.json`, `poses_room-302.json` (`scr_anchor.py train --label-poses`).
