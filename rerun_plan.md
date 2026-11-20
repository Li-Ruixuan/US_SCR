# Clean re-run plan for the paper numbers (v6)

**Status:** Tier 0 and Tier 1 are finished. **No further ORB-SLAM3 runs are planned.** What remains is writing: edit `main.tex` and `supp.tex` from section 5.
**Scope:** results and tables only. No change to the method code or to existing analysis scripts. New analysis code only under `tools/paper/`. No new experiments, no tuning on test sets.

## 0. Goal of the re-run

**Paper objective.** Show when a probe-mounted RGB-D camera alone is good enough for 3D compounding. The paper is not about better accuracy and never says the system beats ORB-SLAM3.

**Goal of the re-run.** Make every number in the paper come from one protocol, so that each claim can be checked and none depends on a mixed setting. It is not a search for better values.

**What it means in practice**
1. One protocol: 2 s smoothing window, the same error definition, the same sweeps for every system (D1, D2, D4).
2. Existing runs only. ORB-SLAM3 is re-scored, not re-run; the three incomplete occlusion runs are replaced by complete runs that already exist (section 3).
3. Report what comes out. A value that gets worse stays, and the claim is changed instead (rule 6).
4. Old values go to `content.tex`, so nothing is lost and `main.tex` stays free of defensive text.

**What is not part of it:** new ORB-SLAM3 runs, new experiments, tuning, changes to the method code.

**State.** The re-scoring and the anchor analysis are done. Writing is left (section 5), plus the table gaps in section 5.6.

## 1. What the numbers are for

The paper does not claim a more accurate tracker. It asks when a probe-mounted RGB-D camera alone is good enough for 3D compounding. The numbers support these claims, and the plan only repairs what a claim needs.

| Claim | Evidence | Status |
|---|---|---|
| Accuracy is bounded with a covering room scan | Table III upper block, Table IV | Done: all values at 2 s are in `main.tex` |
| Coverage, not mapping, sets the error | Table IV, anchor near / far | B1 done (Kabsch). Text still to be edited (5.3) |
| A scene change is detected by the inlier count | Table IV middle block | Done |
| Occlusion keeps the error bounded | Table IV lower block | Our side done. The "87--100 % posed" wording and the ORB-SLAM3 side still to be edited (5.2) |
| The per-frame approach fails differently from SLAM | Existing ORB-SLAM3 runs | **No new runs.** Existing runs are enough (section 3) |
| ORB-SLAM3 is more accurate on most sweeps | Paired test, 63 sweeps, 2 s | Done: 51 of 63, 1.95 mm [1.28, 2.61] |
| Ablations | Table III lower block | B2 done. B3: SD over sweeps available (5.4) |

## 2. Decisions (final)

| # | Decision |
|---|---|
| D1 | **2 s offline window everywhere**, for the proposed system and for ORB-SLAM3. |
| D2 | Keep "mean over the five sets" for F2 and the phantom. The over-sweeps values (F2 7.75 ± 3.15, n = 26; phantom 3.45 ± 1.46, n = 32) go to the supplement. |
| D3 | **No ORB-SLAM3 repeats beyond what exists.** The occluded ORB-SLAM3 values are reported as single runs, and the text says so. |
| D4 | Anchor analysis with Kabsch, the final system. The old PnP values are replaced. |

## 3. ORB-SLAM3: policy and what exists

No new ORB-SLAM3 runs. The claims use only complete runs that are already on disk.

- **Paired comparison (63 sweeps):** the 89 existing runs re-scored at 2 s (done, `runs/paper_final/slam-*`). All 89 end with their sequence except the three below.
- **Run-to-run spread:** `loc`, `loc-r2`, `loc-r3` on the 11 main splits (existing); the F2-arm sweep (81.5 and 28.2 mm in two runs); P-rearr1 30 % `loc-r2`, where the 132 mm failure repeats on the same sweep (127.7 mm).
- **Occlusion:** one run per setting. Where the original run is incomplete, a complete run already exists:

| Setting | Original run (do not use) | Complete run (use) |
|---|---|---|
| P-rearr2, 60 %, localisation only | stops at 268 of 579 s | `loc-r4`: 8 / 8 sweeps, mean 2.40, worst 2.7 |
| P-rearr2, 60 %, each frame relocalised | stops at 261 of 579 s ("3 of 8 sweeps") | `reloc-r2`: 8 / 8, mean 1.81, worst 2.2 |
| P-rearr1, 60 %, each frame relocalised | stops at 504 of 549 s (39.7 mm is its last sweep) | `reloc-r2`: 8 / 8, mean 1.83, worst 2.9 |

- **Stopped runs, not used:** P-rearr1 30 % `loc-r3` (242 of 549 s) and P-rearr1 60 % `loc-r2` (24 s). They are not repeated. If the folders get in the way, delete or rename them.
- **`runs/abl/`:** no usable result, and nothing in the paper depends on it.

## 4. Rules

1. Same rule for every row: a whole table or block, never only the rows that look odd.
2. Report the first complete result. If a number gets worse, it stays.
3. Settings are chosen on F1-val only.
4. Every replaced number goes to `paper/content.tex` with its old value.
5. Old results are not overwritten (re-scored copies are in `runs/paper_final/`).
6. If a claim no longer holds, change the claim, not the run.

## 5. Remaining work (writing only)

### 5.1 Already applied to `main.tex`
All 1 s to 2 s replacements: phantom rows in Tables III and IV, seeds, epochs, scene changes, occlusion means, ORB-SLAM3 paired values, abstract and Discussion numbers. The old values are in `content.tex`.

### 5.2 Occlusion text
- Replace the red placeholder: "87--100 % of the frames passed the inlier gate before smoothing; after smoothing, every frame had a pose." Source: raw share per sweep set, P-rearr1 30 % 99.6, 60 % 86.5; P-rearr2 30 % 100, 60 % 97.6 (`per_sweep["raw"]["coverage_pct"]`).
- ORB-SLAM3, P-rearr2 60 %: localisation only 2.40 (`loc-r4`), each frame relocalised 1.81 with 8 of 8 sweeps. **Remove "3 of 8 sweeps".**
- **Remove "39.7 mm"** from Results and Discussion. Other modes' worst sweep at 60 %: 38.7 (full SLAM), 13.0 (localisation only). Rewrite the sentence on "other modes failed on single sweeps" with these two values.
- State that the occluded ORB-SLAM3 values are single runs.
- "Lower mean in three of the four occluded settings" holds: ours 5.15, 5.25, 3.53, 3.86; ORB-SLAM3 17.88, 3.34, 2.46, 2.40 (`loc-r4`).

### 5.3 Coverage text (B1, Kabsch)
- Same-session anchor error, covered / not covered: **1.8--4.5 / 2.7--6.0 mm** (F1-val, F1-test, F2-new, F2-small); replaces 2.3--5.6 / 5.7--9.1.
- Pooled over all evaluations (median): **2.8 / 6.6 mm**; replaces 4.1 / 13.4 in the supplement.
- Discussion, "Coverage Sets the Accuracy": the sentence "anchor error was higher away from the room-scan poses (5.7--9.1 vs. 2.3--5.6 mm)" holds pooled (6.6 vs. 2.8) and across sessions, but **not within F1-val and F1-test** (only 6 and 19 frames not covered). State it pooled, not per session.
- State in the text that the anchors use Kabsch.

### 5.4 Open reads (read-only, no run)
- Table V jitter of ORB-SLAM3 on F1-test: **checked.** `runs/slam-3XX-loc` (1 s) gives 0.68, `runs/paper_final/slam-3XX-loc` (2 s) gives 0.75. Replace 0.68 by **0.75** (D1).
- Table V "Classical, self-made map 3.65 / 2.66; proposed 2.35 / 1.73 on the same frames": **checked.** The proposed poses (`runs/volume3d-classical-ourmap/3XX/poses/*scr-track.json`) are "SCR alone on every frame, smoothed 2 s"; the classical rows use their pose graph. Already on one protocol: no change.
- Table III, "without loop closures": **checked.** Track means (`runs/repro/track-v2map-3XX-noloops`): 5.84 at 1 s, **5.76 at 2 s**. The 5.77 in the table is not from another window (it comes from the shape script on the 2 s exports, `runs/repro/shape-3XX-ablations.md`). Use 5.76 ± 1.42. "Without correction": 11.49 at 2 s (`runs/repro/track-v2map-3XX-nocalib`), as in the table; add ± 0.79. B3 with three seeds is **not** needed.
- Experiment 6, ORB-SLAM3: "Its poses are smoothed over 1 s" becomes **2 s**.
- State the smoothing of the odometry, classical, hybrid and SCR rows of Table V (pose graph; oracle map at 2 s).
- Extend `missing_numbers.py` to read the three complete runs above, then update the numbers in 5.2.

### 5.5 Files
- Copy `content.tex` into `paper/` (it is not in the repository yet).
- `supp.tex`: still the old names and "we". Update with the new names, the M7 localisation-only interval written exactly (it crosses zero: 0.68 [-2.14, 2.38]), the ORB-SLAM3 code change in `Tracking.cc`, the per-sweep table `persweep_orbslam.tex` (M8), the pooled anchors 2.8 / 6.6, and the over-sweeps values from D2.

### 5.6 Empty cells (`--`) in Tables III to V

About 60 cells are `--`. They fall into three groups. No group needs an ORB-SLAM3 run.

**A. Not applicable: fix by layout, no run.**
- Table III ablation rows: Ref., Map err. and Seeds exist only for the headline rows. Move them to the upper block or drop them from the lower block.
- Table IV: the Oracle column in the scene-change and occlusion blocks, and Cov. / Map err. where they do not apply. Drop the column or split the block.
- Table V: columns where a system has no value by design.
- Aim: no `--` cell left, as in the example papers.

**B. Probably computable from existing files, no new run.**
| Cell | Source | Check |
|---|---|---|
| Table IV, Map err. of the F2 rows | self-mapping output vs tracker poses of the scans | was it logged? |
| Table IV, Cov. of scene-change and occlusion rows | existing poses | none |
| Table V, jitter on F2, strict column (proposed) | existing predictions | none |
| Table V, ORB-SLAM3 F1-val, strict, jitter on F2 | the 89 re-scored runs | is F1-val among the 11 main splits? |

Step: write `tools/paper/gap_check.py`. It lists every `--` cell and says whether its source file exists. Then fill the cells that exist.

**C. Real gaps (a run is needed, never ORB-SLAM3).**
| Gap | Run | Decision |
|---|---|---|
| Oracle on scene-change and occlusion rows | inference with existing oracle checkpoints | optional; the key coverage rows already have an oracle |
| Pose regression, hybrid, odometry, classical on sets that show `--` | own implementations, training PC | not needed for Experiment 6 (the claim is the failure behaviour, not a ranking); remove the cells or rows |
| Anchor ablations on F1-val only (n = 2) | none | leave; settings were chosen on F1-val on purpose |

### 5.7 New failure table (no run)

Sweeps by outcome for the proposed system and ORB-SLAM3 per mode, as `n (%)`: bounded, large error, no pose. Source: existing per-sweep errors, including the 89 re-scored runs. The threshold for "large error" is fixed before counting and is not tuned on the test sets. Script: `tools/paper/failure_table.py`, which writes the LaTeX rows. Keep the total at 5 tables, so it replaces rows of Table V rather than adding a sixth table.

## 6. Where to run

Nothing is required on the training PC. Tier 1 (B1, B2, B3) is closed. Analysis machine only: `gap_check.py`, `failure_table.py`, the optional M10 figure and, if wanted, the oracle inference from 5.6 C. Plain `python ...` commands in the conda env `usrgbd`.

## 7. Outputs to keep

```
runs/paper_final/
  README.md              decisions D1-D4, dates
  CODE_HASH  GIT_STATUS_AT_RUN.txt  ENV.txt  ORBSLAM3_BUILD.txt
  slam-<split>[-mode]/   ORB-SLAM3 re-scored at 2 s (89 runs)
  numbers/               missing_numbers.json, missing_numbers_report.md, persweep_orbslam.{csv,tex}
  coverage_error.md
  shape-occ-ours.md
```