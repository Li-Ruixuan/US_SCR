# Clean re-run plan for the paper numbers

**Status:** plan only. Nothing has been run. Run it on the training PC.
**Scope:** results and tables only. No change to the method code, no new experiments, no tuning on test sets.

## 1. Rules

1. **Freeze first.** One code version, one configuration, three seeds (0, 1, 2), recorded before the first run (section 3).
2. **Same rule for every row.** Re-run a whole table or a whole block of it. Never re-run only the rows that look odd.
3. **Report the first complete run** on the frozen pipeline. If a number gets worse, it stays. Do not repeat a run to get a better number.
4. **Settings are chosen on F1-val only.** The test sets are not used to choose anything.
5. **Keep the old values.** Every number that is replaced goes to `content.tex` with its old value and the reason.
6. **Do not delete old runs.** Write results to new folders under `runs/` (for example `runs/paper_final/`).

## 2. Decisions to make before the first run

| # | Decision | Recommendation |
|---|---|---|
| D1 | Smoothing window | **2 s offline everywhere.** F1-test, F2 and the seed values already use 2 s. Only the phantom numbers and `runs/stats-orbslam.md` use 1 s. |
| D2 | Mean of set means or mean over sweeps | Keep "mean over the five sets" for F2 and the phantom, as the paper says (F2 7.92, phantom 3.58). Add the over-sweeps values (F2 7.75, n = 26; phantom 3.47, n = 32) to the supplement. |
| D3 | Number of ORB-SLAM3 runs per mode | Three runs per mode (`loc`, `loc-r2`, `loc-r3`, `reloc`), reported as run-to-run spread. The paper already says failures vary between runs (81.5 and 28.2 mm on one sweep). |

Write the chosen options at the top of `runs/paper_final/README.md`.

## 3. Freeze checklist (do once, before anything else)

```bash
conda activate usrgbd      # or use /data2/u0137815/conda/envs/usrgbd/bin/python; there is no bare python on the PATH
mkdir -p runs/paper_final
git rev-parse HEAD > runs/paper_final/CODE_HASH
git status --short > runs/paper_final/GIT_STATUS_AT_RUN.txt      # must contain no modified code files
python -c "import numpy, scipy, torch; print(numpy.__version__, scipy.__version__, torch.__version__)" > runs/paper_final/ENV.txt
```

Also record in `runs/paper_final/README.md`:

- the ORB-SLAM3 build, with the one-line change in `Tracking.cc` (`if(mState==LOST || mState==RECENTLY_LOST)`);
- the list of sweeps per set (F1-val 2, F1-test 5, P-ref 8, P-rearr1 8, P-rearr2 8, P-people 4, P-empty 4, F2-new 8, F2-small 4, F2-large 4, F2-subj2 6, F2-arm 4);
- the training configuration (Table I of the paper: 120 epochs, AdamW, batch size 8, learning rates 10^-3 / 10^-4).

## 4. Tier 0: no re-run, read-only (do this first)

Several of the open inconsistencies need no training. The per-sweep errors for both windows are already in `runs/<track>/scr_track.json` under `per_sweep[<window>][<sweep>]["us_median"]`.

| Item | Action | Command |
|---|---|---|
| Phantom, five sets at 2 s | Read the 2 s values from the existing tracks (`runs/track-v2map-5XX{A..E}-exam`). The 2 s values given in `missing_numbers.md` are 2.26, 4.41, 3.09, 2.19, 5.86 mm. | `python tools/paper/missing_numbers.py --out runs/paper_final/numbers` (set the window to 2 s in the script) |
| Paired ORB-SLAM3 comparison at 2 s | Repeat the paired statistics with the 2 s window | `python tools/compare_stats.py --modes final online loc loc-r2 loc-r3 reloc --window 2.0 > runs/paper_final/stats-orbslam-2s.md` |
| Means and SDs | Recompute with `ddof=1` at 2 s for all sets | `tools/paper/missing_numbers.py`, item M2 |
| Per-sweep ORB-SLAM3 table | Needed for the supplement | `tools/paper/missing_numbers.py`, item M8 |

**Check:** F1-test must still give 2.34 ± 0.47 and F2 7.92 ± 2.56 (over five sets). If either differs, stop and report.

## 5. Tier 1: re-run what depends on an older recipe or network

Only these need new runs. Each one is a whole block.

| Block | Why | What to produce | Replaces in `main.tex` |
|---|---|---|---|
| **B1. Anchor near / far** | The draft values come from "an earlier network version" (oracle map, ten pooled evaluations) | Final-network `scr_eval.json` for the same evaluations, then `python tools/coverage_error.py runs/paper_final/eval_*/scr_eval.json` | Coverage results (2.3--5.6 / 5.7--9.1 mm); Discussion "Coverage Sets the Accuracy" |
| **B2. F1-val ablations** | The anchor ablations (epochs, PnP vs Kabsch, augmentation, resolution) may mix recipes | Oracle map on F1-val, one change at a time, with 30 / 60 / 120 epochs, PnP, geometric augmentation and full-resolution input | Table III lower block; Results, Tracking |
| **B3. Ablations on F1-test with SD** | The rows without loop closures and without the camera correction have no SD | Self-mapping repeated from scratch, three seeds each, per-sweep errors saved | Table III lower block; Results, Self-Mapping |
| **B4. ORB-SLAM3 repeated runs** | Run-to-run spread is quoted from two runs | Three runs per mode on all 63 test sweeps and on the occluded sets | Occlusion results; Discussion (13--132 mm; 81.5 and 28.2 mm) |

Command template. **The scripts and flags are not in this session, so fill them from the run configuration of the existing run** (`runs/<run>/config.json` holds the exact command line of each earlier run):

```bash
# B1 (map, train, track and evaluate with the final code; copy the arguments from runs/<run>/config.json)
python <mapping or training script> --config runs/<run>/config.json --out runs/paper_final/<run>
python tools/coverage_error.py runs/paper_final/<run>/eval_*/scr_eval.json

# B4 (three ORB-SLAM3 runs, one per mode and run index)
python <orbslam runner> --mode loc    --run 1 --out runs/paper_final/slam-<split>-loc-r1
python <orbslam runner> --mode loc    --run 2 --out runs/paper_final/slam-<split>-loc-r2
python <orbslam runner> --mode loc    --run 3 --out runs/paper_final/slam-<split>-loc-r3
```

## 6. Tier 2: full re-run (optional)

Only if Tier 0 and Tier 1 show that the old and new numbers disagree by more than 0.1 mm on the headline rows. Then re-run mapping, training and tracking for all sets, three seeds each, and regenerate Tables III to V and every number in the Results from the new files. Do not mix old and new runs in one table.

## 7. Acceptance and replacement

For every number in Tables III to V:

1. If the new value matches the old one within 0.05 mm, keep the old text.
2. If it differs, replace it in `main.tex` and add the old value to `content.tex`.
3. After the replacements, re-read the abstract, the "Thus" sentences in Results, Discussion and Conclusion. Check these claims against the new numbers:
   - 2.2--3.1 mm and shape 1.7--1.9 mm in a furnished room;
   - 0.3--0.5 mm above the oracle map;
   - 5.85 mm in an emptied room;
   - 2.28 to 13.57 mm with the generic scan;
   - occlusion: at most 0.9 mm and no sweep above 8.5 mm;
   - ORB-SLAM3: lower on 52 of 63 sweeps, 1.96 mm [1.30, 2.61], 13--132 mm.
4. If a claim no longer holds, change the claim, not the run.

## 8. Outputs to keep

```
runs/paper_final/
  README.md            decisions D1-D3, tier run, dates
  CODE_HASH
  GIT_STATUS_AT_RUN.txt
  ENV.txt
  numbers/             missing_numbers.json, missing_numbers_report.md
  stats-orbslam-2s.md
  coverage_error.md
```
