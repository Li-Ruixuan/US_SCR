# Clean re-run plan for the paper numbers (v3)

**Status (2026-11-20):** Tier 0 done on the analysis machine (re-scoring and reading only). Tier 1 not started. See section 0.

## 0. Progress log (where to pick up)

### 0.1 Finished

| Task | Result | Files |
|---|---|---|
| Freeze (section 3) | Code clean (`GIT_STATUS_AT_RUN.txt` lists only `runs/paper_final/`); ORB-SLAM3 commit and `Tracking.cc` diff recorded | `runs/paper_final/CODE_HASH`, `GIT_STATUS_AT_RUN.txt`, `ENV.txt`, `ORBSLAM3_BUILD.txt` |
| 0b: ORB-SLAM3 re-scored at 2 s | 89 / 89 evaluations, all `smooth = 2.0`; 1 s originals untouched | `runs/paper_final/slam-*/slam_eval.{md,json}`, `runs/paper_final/rescore_2s.{sh,log}` |
| ORB-SLAM3 shape at 2 s | 89 / 89, 0 failures | `runs/paper_final/slam-*/shape.md`, `runs/paper_final/shape_2s.log` |
| 0a + 0c + 0d: `tools/paper/missing_numbers.py` | Exit 0, every check passed; the 1 s self-check reproduces `runs/stats-orbslam.md` exactly | `runs/paper_final/numbers/missing_numbers_report.md`, `missing_numbers.json` |
| M8 per-sweep table (63 sweeps, 2 s) | Ready for the supplement | `runs/paper_final/numbers/persweep_orbslam.{csv,tex}` |
| Our shape under occlusion at 2 s | 2.81 / 3.38 / 3.88 (P-rearr1), 1.76 / 2.27 / 2.80 (P-rearr2): unchanged | `runs/paper_final/shape-occ-ours.md` |
| Window audit of every table value | Old (1 s) and new (2 s) values listed | **section 7.1 below** (edit `main.tex` from there) |
| Lookups (M4, M5, M9) and hand checks | Hand–eye solver, ORB-SLAM3 diff, 6.3 mm run, near/far sources | `missing_numbers.md`, section 5 |
| B2 | No re-run needed (recipes do not mix) | section 5 |
| B3 (half) | SD over sweeps: 5.76 ± 1.42 (no loop closures), 11.49 ± 0.79 (no camera correction) | section 5 |
| Tier 2 decision | Not needed: largest headline change 0.05 mm (< 0.1 mm trigger) | – |

**Headline numbers at 2 s (details and all other rows in section 7.1):**

- F1-test 2.34 ± 0.47 (unchanged); F2 7.92 ± 2.56 over 5 sets (7.75 ± 3.15 over 26 sweeps); phantom 2.26, 4.41, 3.09, 2.19, 5.86, mean over 5 sets 3.56 ± 1.57 (3.45 ± 1.46 over 32 sweeps); P-ref generic 13.57.
- P-ref exam-view vs. generic: lower on 8 / 8, exact p = 0.0078.
- Seed gap to the oracle map: 0.29 mm (0.13–0.48 per seed).
- ORB-SLAM3, each frame relocalised: lower on 51 / 63, 1.95 mm [1.28, 2.61], p < 0.001; full SLAM 50 / 63; localisation only 49 / 63, three runs 3.09–4.46 mm.
- Occlusion (ours): increase 0.4–0.8 mm, worst sweep 8.4 mm.

### 0.2 Do not use yet

| Value | Why |
|---|---|
| ORB-SLAM3 on P-rearr2, 60 % occluded (`slam-5XXC-exam-occ60-loc`, 2 s mean 3.46) | Trajectory on disk is incomplete: 5 of 8 sweeps unposed at 2 s but posed at 1 s (overwritten or crashed run). `-reloc` on the same setting has 3 of 8 sweeps at both windows. Replaced in B4. |
| "ORB-SLAM3 lower in three of the four occluded settings" | Depends on the row above |
| ORB-SLAM3 jitter F1-test 0.68 → 0.75 | Rises with the longer window; check before replacing |
| Near / far anchors 4.1 / 13.4 (and 2.3–5.6 / 5.7–9.1) | Old PnP networks; needs B1 (D4: Kabsch) |
| "87–100 % of the frames were posed" (occlusion) | Tracks report 100 % at both windows; source of 87 % unknown |

### 0.3 Waiting (in this order)

| # | Task | Where | State |
|---|---|---|---|
| 1 | **Check 2**: compare every sweep of the 89 ORB-SLAM3 runs at 1 s and 2 s (posed share, > 0.5 mm change) to find other incomplete trajectories | analysis machine, read only, seconds | command given in the session, not run |
| 2 | **B4**: 32 ORB-SLAM3 runs (reloc r2/r3 on 11 splits; loc r2/r3 on 4 occluded settings; P-rearr2 60 % loc-r4 and reloc-r2), plus any from check 2 via `--extra NEW=TEMPLATE` | analysis machine (ORB-SLAM3 build is here), 3–5 h, one run after the other | generator `tools/paper/make_b4.py` written; `python tools/paper/make_b4.py > runs/paper_final/b4_orbslam.sh`, check (32 targets, no SKIP), then `nohup bash runs/paper_final/b4_orbslam.sh > runs/paper_final/b4_orbslam.log 2>&1 &` |
| 3 | After B4: extend `missing_numbers.py` to read the repeats (run-to-run spread) and update section 7.1 | analysis machine | not started |
| 4 | **B1**: Kabsch evaluation of the final networks on F2-new → F2-small, F2-new → F2-large, F1-val → F1-test, then `coverage_error.py` | training PC (checkpoints) | commands not written |
| 5 | Find the source of "87–100 % posed" (occlusion) | user | open |
| 6 | Copy `content.tex` into `paper/` (section 9) | user | open |
| 7 | Edit `main.tex` / `supp.tex` from section 7.1; old values to `content.tex` | after 5 and 6 | not started |
| 8 | Optional: B3 with three seeds (training PC); M10 figure (analysis machine) | – | not started |
**Scope:** results and tables only. No change to the method code and to existing analysis scripts (`compare_stats.py`, `coverage_error.py`, `slam_baseline.py`), no new experiments, no tuning on test sets. **New analysis code is allowed only under `tools/paper/`** (this is `missing_numbers.py`).
**Revision:** v3 after the second review: the paired comparison moves into `missing_numbers.py` (`compare_stats.py` hard-codes `runs/`), Tier 0 needs the raw data, D3 and B4 agree, B2 is done and B3 is half done.

## 1. Rules

1. **Freeze first.** One code version, one configuration, three seeds (0, 1, 2), recorded before the first run (section 3).
2. **Same rule for every row.** Re-evaluate or re-run a whole table or a whole block of it. Never only the rows that look odd.
3. **Report the first complete result** on the frozen pipeline. If a number gets worse, it stays. Do not repeat a run to get a better number.
4. **Settings are chosen on F1-val only.** The test sets are not used to choose anything.
5. **Keep the old values.** Every number that is replaced goes to `paper/content.tex` with its old value and the reason. (`content.tex` is not in the repository yet; see section 9.)
6. **Do not overwrite old results.** New runs get new folder names in `runs/`, following the existing pattern `runs/slam-{split}{tag}[-{mode}]`, so they cannot overwrite anything. A **re-scored copy of an existing run** goes to `runs/paper_final/`, because a `slam_eval.json` holds one smoothing window and re-scoring in place would destroy the 1 s result.

## 2. Decisions to make before the first run

| # | Decision | Recommendation |
|---|---|---|
| D1 | Smoothing window | **2 s offline everywhere**, for the proposed system and for ORB-SLAM3. F1-test, F2 and the seed values already use 2 s. The phantom values and the ORB-SLAM3 comparison use 1 s. |
| D2 | Mean of set means or mean over sweeps | Keep "mean over the five sets" for F2 and the phantom, as the paper says. Put the over-sweeps values in the supplement. |
| D3 | ORB-SLAM3 repeats | Three runs for **every mode that is reported with a spread**: `loc` (11 main splits, already done), `reloc` and the occluded sets `occ30` / `occ60` with `loc`. Reported as run-to-run spread. |
| D4 | Anchor analysis: PnP or Kabsch | **Kabsch**, because it is the final system. The old near/far values (4.1 / 13.4, and the same-session 2.3--5.6 / 5.7--9.1) used PnP. State in the text which localiser was used. |

Write the choices at the top of `runs/paper_final/README.md`.

## 3. Freeze checklist (do once)

```bash
conda activate usrgbd      # or /data2/u0137815/conda/envs/usrgbd/bin/python; no bare python on the PATH
mkdir -p runs/paper_final
git rev-parse HEAD > runs/paper_final/CODE_HASH
git status --short > runs/paper_final/GIT_STATUS_AT_RUN.txt     # no modified code files expected
python -c "import numpy, scipy, torch; print(numpy.__version__, scipy.__version__, torch.__version__)" > runs/paper_final/ENV.txt
```

Also record in `runs/paper_final/README.md`: the ORB-SLAM3 build with the one-line change in `Tracking.cc` (`if(mState==LOST || mState==RECENTLY_LOST)`), the sweeps per set (F1-val 2, F1-test 5, P-ref 8, P-rearr1 8, P-rearr2 8, P-people 4, P-empty 4, F2-new 8, F2-small 4, F2-large 4, F2-subj2 6, F2-arm 4) and the training configuration (Table I of the paper).

## 4. Tier 0: re-scoring only, no SLAM run, no training

These steps only re-score saved poses. Step 0b needs the raw data, so run Tier 0 on the machine where `runs/` **and the raw data** are.

| Step | Action | Command |
|---|---|---|
| 0a | **Write `tools/paper/missing_numbers.py`** from `missing_numbers.md`, with the M7 addendum below. It does not exist yet, and 0c and 0d depend on it. | (code task, new file only) |
| 0b | **Re-score the saved ORB-SLAM3 trajectories at 2 s.** `slam_baseline.py evaluate` reads the raw sessions through `--root` (for example `/data2/u0137815/rgbd-us/data/train_3XX`), the `seq/` folders and `T_marker_cam.npy`. Use the arguments of the existing evaluations and change only `--smooth 2` and the output folder. No SLAM re-run. | `python tools/slam_baseline.py evaluate --smooth 2 --root <session root> <existing arguments> --out runs/paper_final/slam-<split>{tag}[-<mode>]` |
| 0c + 0d | **Numbers at 2 s, including the paired comparison.** Means, SD with `ddof=1`, per-sweep table, and M7 (ours at 2 s against ORB-SLAM3 at 2 s, from the re-scored folders). One script, one window. `compare_stats.py` is not used, because it hard-codes `runs/` and adds `--tag` to both folders. | `python tools/paper/missing_numbers.py --window 2 --slam-dir runs/paper_final --out runs/paper_final/numbers` |

**M7 addendum (for the script).**
- Inputs: ours, `per_sweep["2.0"][<sweep>]["us_median"]` in `runs/<track>/scr_track.json`; ORB-SLAM3, the re-scored `runs/paper_final/slam-*/slam_eval.json`.
- Sweeps: 63 = F1-test 5 + F2 26 + phantom exam-view 32.
- Modes: full SLAM, localisation only, each frame relocalised, and the run repeats.
- Statistics: difference proposed minus ORB-SLAM3 (sign as in `missing_numbers.md`), bootstrap over sweeps (same number of resamples and seed as `compare_stats.py`; read it), two-sided Wilcoxon.

**Checks (ours only):** F1-test 2.34 ± 0.47; F2 7.92 ± 2.56 over five sets. **The old ORB-SLAM3 check values no longer apply:** 52 of 63, 1.96 [1.30, 2.61], and the means 1.84, 8.37 and 2.36 mm are 1 s values and will change.

## 5. Tier 1: needs the checkpoints (training PC)

| Block | What | Needs | Replaces in `main.tex` |
|---|---|---|---|
| **B1. Near / far anchors** | Re-evaluate **only the cross-session cases** (A to B, A to C, F1-val to F1-test) with the existing final networks. Own-session evaluations already exist (`v2-3XX`, `v2-4XXA/B/C` with C evaluated on D and E, `bigclean-2XX`), but only with Kabsch. No mapping and no training. Then run `coverage_error.py`. | existing checkpoints, D4 | Coverage results (near / far); Discussion "Coverage Sets the Accuracy" |
| **B2. F1-val ablations** | **Done, no re-run.** The recovered configs were compared: the 30-, 60- and 120-epoch runs and the full-resolution run differ only in epochs or input size (plus logging). Only the first recipe (`s1-base`, 15 epochs) had the half-precision head switched off, and it is already removed from the table. | none | none |
| **B3. F1-test ablations** | **Half done.** Per-sweep values exist for both ablations (one seed each), so the SD over sweeps can be reported now (table below). Re-mapping with three seeds is needed only if an SD over seeds is wanted. | existing tracks | Table III lower block; Results, Self-Mapping |
| **B4. ORB-SLAM3 repeats** | `loc`, `loc-r2` and `loc-r3` exist for the 11 main splits. **Missing:** `reloc-r2`, `reloc-r3`, and `occ30-loc-r2`, `occ30-loc-r3`, `occ60-loc-r2`, `occ60-loc-r3` (the occluded sets have one `loc` run each). | ORB-SLAM3 build, D3 | Occlusion results; Discussion (13--132 mm; 81.5 and 28.2 mm) |

**B3 values at 2 s (F1-test, n = 5, mean ± SD over sweeps):** without loop closures 5.76 ± 1.42; without camera correction 11.49 ± 0.79. Table III currently has 5.77 for the first row, so that value was read at another window. Resolve this under rule 7.1 before editing the table.

```bash
# B1: cross-session re-evaluation (copy the arguments from the config.json of the existing evaluation)
python <evaluation script> --config runs/<run>/config.json --out runs/paper_final/<run>
python tools/coverage_error.py runs/paper_final/*/eval_*/scr_eval.json

# B4: missing repeats only; names follow runs/slam-{split}{tag}[-{mode}]
python tools/slam_baseline.py <arguments of the existing run> --out runs/slam-<split>-reloc-r2
python tools/slam_baseline.py <arguments of the existing run> --out runs/slam-<split>-reloc-r3
python tools/slam_baseline.py <arguments of the existing run> --out runs/slam-<split>-occ30-loc-r2
python tools/slam_baseline.py <arguments of the existing run> --out runs/slam-<split>-occ30-loc-r3
python tools/slam_baseline.py <arguments of the existing run> --out runs/slam-<split>-occ60-loc-r2
python tools/slam_baseline.py <arguments of the existing run> --out runs/slam-<split>-occ60-loc-r3
```

## 6. Tier 2: full re-run (optional)

Only if Tier 0 and Tier 1 show disagreement above 0.1 mm on the headline rows. Then re-run mapping, training and tracking for all sets, three seeds each, and regenerate Tables III to V. Do not mix old and new runs in one table.

## 7. Replacement rule

1. **Any value whose window changed is replaced**, even by 0.01 mm. Under D1 the phantom values move to 2 s: 2.28 to 2.26, 4.43 to 4.41, 3.11 to 3.09, 2.24 to 2.19, 5.85 to 5.86 (from `missing_numbers.md`), and the phantom mean 3.58 to 3.56. The SDs, the shape errors and every ORB-SLAM3 value at 1 s move too. Tables III to V must be on one window.
2. The 0.05 mm tolerance applies only to a **repeat at the same window** (for example a B4 repeat or a Tier 2 run). If the repeat is within 0.05 mm, keep the old text.
3. Each replaced value goes to `content.tex` with its old value.
4. After the replacements, re-read the claims that quote numbers, and change the claim if it no longer holds:
   - abstract: "2.2--3.1 mm", "shape 1.7--1.9 mm", "0.3--0.5 mm above the oracle map", **"in an emptied room it was 5.85 mm"**, **"from 2.28 to 13.57 mm"**, "at most 0.9 mm", "no sweep above 8.5 mm", "13--132 mm";
   - Results: the closing "Thus" sentences, the seed paragraph, the coverage paragraphs;
   - Discussion and Conclusion: the numbers quoted in the paragraphs on coverage, bounded failures and the comparison;
   - ORB-SLAM3: "lower on 52 of 63 sweeps", "1.96 mm [1.30, 2.61]", Table V row, F2 without F2-arm (4.45), the generic scan (2.88).
5. If a claim no longer holds, change the claim, not the run.

### 7.1 Replacement list from Tier 0 (window audit, 2026-11-20)

Source of the 2 s values: `runs/paper_final/numbers/` (script, all checks passed), `runs/shape-5XX.md`, `runs/shape-5XX-extra.md`, `runs/shape-v2map-4XX.md` (their "absolute" column is 2 s), and a read-only print of the occluded and seed tracks. **Finding:** in the phantom rows of `tab:ctrl` the absolute error is 1 s and the shape error is already 2 s, so only the absolute values change.

**`tab:ctrl` and text, proposed system (absolute only; shape already 2 s)**

| Row / sentence | Old (1 s) | New (2 s) |
|---|---|---|
| P-ref / P-rearr1 / P-rearr2 / P-people / P-empty, exam-view | 2.28, 4.43, 3.11, 2.24, 5.85 | **2.26, 4.41, 3.09, 2.19, 5.86** |
| … with SD (Results, first paragraph) | ±0.38, 0.92, 0.96, 0.25, 1.06 | **±0.38, 0.92, 0.93, 0.25, 1.06** |
| Same, generic scans | 13.57, 3.36, 6.35, 5.07, 13.03 | **13.57, 3.35, 6.32, 5.09, 13.08** |
| P-ref, both scans in one map | 3.15 | **3.11** |
| P-ref, oracle map: exam-view / generic | 1.85 / 10.95 | **1.81 / 10.93** (shape 1.67 / 3.93 unchanged) |
| Scene changes: scan after the sweeps / P-ref's map on P-rearr1 / P-rearr1's map on P-rearr2 / P-rearr2's map on P-empty | 2.50, 4.28, 40.9, 13.9 | **2.48, 4.23, 40.7, 13.6** (posed shares and p90 to be re-read at 2 s) |
| P-ref's map on P-rearr2 (59.4, 21 % posed) | 59.4 (21 %) | **58.7** (21 %) |
| Posed shares and p90 of the other scene-change rows | 40.9 (96 %); 13.9 (p90 46.6) | **40.7 (96 %); 13.6 (p90 46.4)** |
| P-rearr1 exam-view vs. generic (text) | 4.43 vs. 3.36 | **4.41 vs. 3.35** |
| People in the background (text) / scan after the sweeps (text) / rescanning P-rearr2 (text) | 2.24 / 2.50 / 3.11 | **2.19 / 2.48 / 3.09** |
| P-ref epochs 20 / 40 / 80 / 120 | 2.53, 2.34, 2.37, 2.28 | **2.53, 2.31, 2.34, 2.26** |
| Phantom seeds (mean ± SD over 3 seeds) | 2.26±0.03, 4.20±0.23, 3.17±0.12, 2.22±0.03, 6.00±0.27 | **2.23±0.03, 4.19±0.22, 3.14±0.12, 2.19±0.03, 6.00±0.25** |
| "seed spread at most 0.27 mm on the phantom" | 0.27 | **0.25** |
| Phantom mean (5 sets), e.g. SLAM paragraph | 3.58 | **3.56** |

**Occlusion rows (mean (worst sweep); shape already 2 s and unchanged: 2.81, 3.38, 3.88 / 1.76, 2.27, 2.80, `runs/paper_final/shape-occ-ours.md`)**

| Set, occluder | Old (1 s) | New (2 s) |
|---|---|---|
| P-rearr1 none / 30 % / 60 % | 4.43 (6.3), 5.16 (7.5), 5.28 (8.5) | **4.41 (6.3), 5.15 (7.5), 5.25 (8.4)** |
| P-rearr2 none / 30 % / 60 % | 3.11 (5.1), 3.54 (6.1), 3.89 (6.6) | **3.09 (5.0), 3.53 (6.0), 3.86 (6.6)** |
| Text: increase "0.4--0.9 mm" | 0.43--0.85 | **0.4--0.8 mm** (0.44--0.84) |
| Text and abstract: "no sweep exceeded 8.5 mm" | 8.5 | **8.4** (claim still holds) |
| Text: "87--100 % of the frames were posed" | ? | `coverage_pct` is 100 % for all four occluded tracks at both windows: find the source of 87 % before editing |

**Unchanged (already 2 s):** F1-test 2.34 / 1.72 (± 0.47); F2 rows and F2 mean 7.92 / 2.69 (± 2.56); F2 oracle rows and 6.48 / 3.17; self-mapped seeds 2.34 / 2.22 / 2.25; oracle seeds 1.85 / 1.95 / 2.12; P-ref exam vs. generic Wilcoxon p = 0.0078 (8 of 8).

**Seed gap (text):** "a gap of 0.30 mm (0.13--0.49 mm per seed)" becomes **0.29 mm (0.13--0.48 mm)** (unrounded means; oracle mean 1.98, not 1.97).

**ORB-SLAM3 (all old values are 1 s; new from `runs/paper_final/numbers/`)**

| Statement | Old (1 s) | New (2 s) |
|---|---|---|
| Each frame relocalised, all 63 sweeps | lower on 52, 1.96 [1.30, 2.61], p < 0.001 | **lower on 51, 1.95 [1.28, 2.61], p < 0.001** |
| Full SLAM, all 63 | lower on 51 | **lower on 50**, 2.28 [1.60, 3.02] |
| Localisation only, all 63 | lower on 49 | lower on 49, 0.68 [−2.14, 2.38] |
| Localisation only, 3 runs (ORB-SLAM3 mean, 63 sweeps) | – | **3.09--4.46 mm** |
| `tab:baselines` ORB-SLAM3 row (localisation only): F1-test absolute / shape | 1.84 / 1.30 | **1.85 / 1.29** |
| Same row: F2 (mean of 5 sets) | 8.37 | **8.37** (sets 4.47, 3.80, 4.91, 4.66, 24.00) |
| Same row: jitter F1-test | 0.68 | **0.75** (step over 8 rows rises with the 2 s window; check before replacing) |
| SLAM paragraph, localisation only: F1-test / F2 / phantom | 1.84 / 8.37 / 2.36 | **1.85 / 8.37 / 2.35** |
| SLAM paragraph: F2 without F2-arm | 4.45 | **4.46** |
| SLAM paragraph: generic P-ref scan (localisation only) | 2.88 | **2.88** |
| Each frame relocalised, F1-test / F2 / phantom (supplement, brief) | 1.72 / 4.45 / 2.33 | **1.74 / 4.45 / 2.33**; generic P-ref 2.76 (unchanged) |
| Full SLAM, F2 / phantom | – | 3.56 / 2.33 |

**ORB-SLAM3 under occlusion (localisation only unless noted; `runs/paper_final/slam-5XX{B,C}-exam-occ*`)**

| Statement | Old (1 s) | New (2 s) |
|---|---|---|
| P-rearr1, worst sweep, 30 % / 60 % occluded | 132.2 / 12.9 | **131.9 / 13.0** |
| P-rearr1, 60 %: shape, ORB-SLAM3 vs. ours | 8.44 vs. 3.88 | **8.41** vs. 3.88 |
| Other modes, worst sweeps (P-rearr1, 60 %: online / relocalised) | 38.6 / 39.7 | **38.7 / 39.7** |
| Means, P-rearr1 30 % / 60 %; P-rearr2 30 % / 60 % | – | 17.88 / 3.34; 2.46 / **3.46** |
| "lower mean in three of the four occluded settings" | 3 of 4 | **3 of 4** (ours 5.15, 5.25, 3.53, 3.86): claim holds |
| **Check before use:** P-rearr2 60 %, localisation only, mean 2.65 → 3.46 | | Too large for a window change. The 1 s shape file also had only 3 sweeps for P-rearr2 60 % relocalised. Compare per sweep at 1 s and 2 s (unposed frames or gaps near the smoothing window?). |

**Not changed by the window:** `tab:baselines` rows for odometry, classical, hybrid (own smoothing: pose graph) and SCR with the oracle map (2 s). State their smoothing in the text.

## 8. Where to run

- **Tier 0:** the machine where `runs/` **and the raw data** are (0b reads `--root`, `seq/` and `T_marker_cam.npy`). No checkpoints needed.
- **Tier 1:** the training PC, because the checkpoints and the ORB-SLAM3 build are there.

## 9. Files to move into the repository before the commit

`content.tex` was written outside the repository, so it is not under `paper/` yet. Copy it there first:

```bash
cp <downloaded>/content.tex paper/content.tex
```

## 10. Outputs to keep

```
runs/paper_final/
  README.md              decisions D1-D4, tiers run, dates
  CODE_HASH  GIT_STATUS_AT_RUN.txt  ENV.txt
  slam-<split>[-mode]/   ORB-SLAM3 re-scored at 2 s
  numbers/               missing_numbers.json, missing_numbers_report.md
  coverage_error.md
```




cd /data2/u0137815/US_SCR
git pull
mkdir -p runs/abl
bash tools/paper/ablations.sh 2>&1 | tee runs/abl/ablations.log