# Reducing pose noise in the SCR pipeline

Based on `runs/scr2`: 50 epochs, `REPORTABLE: true`, real hand-eye, val runs
`room-001` and `run-205`.

Final: train coord 8.4 mm, val coord 17.9 mm, pose 7.97 mm / 0.802 deg,
centroid baseline 877 mm.

Done: trajectory smoothing (`smoothing.py`, causal median + light smooth,
weighted by RANSAC inlier count), rejecting solves below an inlier threshold
before they reach the trajectory (`eval.py --min-inliers/--min-inlier-ratio`,
with a diagnostic plot to pick the threshold from data), `huber_delta`
moved from 0.05 to 0.008 to sit near the now-settled ~18 mm median error, and
the solver already runs on `depth_mask` rather than the GT `xyz_mask` (the
existing "D4 fix" in `train.py`/`eval.py`).

Remaining work is ordered by value per unit effort. Item 1 needs **no
retraining**. Item 2 needs a retrain. Items 3 and 4 are the real ceilings.

---

## Diagnosis first

Three things the history and the plot say together.

**The median is fine; the tail is broken.** Pose median is 7.97 mm but p95 in
the earlier eval was 41 mm — 5x the median. The spikes in the trajectory plot
are individual frames failing, not a uniformly noisy estimator. Median
interframe translation in this data is 0.44 mm at 30 fps, so a 40 mm excursion
between neighbouring frames is not a probe motion. It is a bad solve. Every one
of those is removable without touching the network.

**The network has converged to the calibration floor.** Val coordinate error
settles at 17.9 mm; the two calibration sessions disagree by 16.0 mm in
translation. Coordinate error cannot go below the self-consistency of the
labels. From epoch 39 the val curve moves 18.1 -> 17.9 while train continues
9.5 -> 8.4, so the remaining epochs buy train/val gap, not accuracy.

**Pose error is still largely common-mode.** 7.97 mm pose from 17.9 mm
coordinate error is a factor of 2.2. With 3600 independent per-cell errors it
should approach sqrt(N). A ratio near 2 means the predicted cloud is displaced
coherently rather than scattered, which is the signature of a systematic label
transform -- i.e. the residual hand-eye error -- not of network noise.

Consequence: **model-side work cannot reduce coordinate error much below
~17 mm.** But pose error is dominated by outliers rather than by the floor,
and that outlier tail is what the completed smoothing/rejection work above
targets.

---

## 1. Split the metrics per validation run (no retraining)

`room-001` and `run-205` are different in kind -- the plot axes show `room-001`
spanning roughly 200 x 300 x 400 mm and `run-205` about 70 x 160 x 130 mm --
and pooling them produces a number that describes neither. Report per run.

If one is a broad exploration run and the other a realistic inference
trajectory, the second is the number that answers the gate question, and the
pooled figure is hiding it.

---

## 2. Turn on the uncertainty head (needs retraining)

`uncertainty: false` currently. With it on, the network emits a per-cell
confidence that can weight RANSAC and down-weight cells it cannot place.

Two caveats from `loss.py`, both real. The predicted quantity minimises at
`ln(2 * huber)`, so it is closer to a Laplace scale than a log-variance -- it
is usable as a confidence ordering but must not be reported as a learned
variance. And the network can reduce its loss by declaring everything
uncertain, so watch the distribution rather than trusting it.

Worth trying after the `huber_delta` fix, not before: the confidence is only
meaningful once the loss it is fitted against is behaving sensibly.

---

## 3. The calibration floor (~16 mm)

Nothing above gets coordinate error below the self-consistency of the labels.
To go further, the hand-eye translation has to improve -- the two sessions
currently disagree by 16.0 mm, while their rotation agrees to 0.355 deg.

Rotation is the half that dominates the error budget and it is already
settled. The translation is not observable without large rotations, so a better
session means **discrete static poses** -- move, hold two seconds, move again,
30 to 40 times -- with the board filling more of the frame, and 60 to 90
degrees of orientation spread. That removes motion blur and any camera/tracker
timing offset by construction.

Until then, treat ~16 mm as the floor and do not attribute anything near it to
the model.

## 4. Pose-space coverage (the generalisation gap)

Train 8.4 mm against val 17.9 mm, a ratio of 2.1. Part of that is the floor,
but part is genuine: the model is better on views it has seen.

Recorded runs span roughly a 15 cm translation envelope and a 26 degree viewing
cone. That is not pose-space coverage, and it is the binding constraint on
everything the project wants to claim. More runs, at varied heights, standing
positions and paths, will do more for held-out performance than any
hyperparameter here.

Validate on held-out *trajectories* that differ from the training paths. A
split over runs tracing similar paths measures interpolation.

---

## Also worth changing, smaller

- **`sched_epochs: null`.** The cosine schedule is tied to `--epochs`, so the
  learning rate is a few percent of peak by epoch 45 and the flattening from
  epoch 39 onward is partly the schedule finishing rather than the model
  saturating. Set `--sched-epochs` longer than `--epochs` to see a real knee.
- **Run the `seq_len: 1` ablation.** The config uses `seq_len: 3,
  seq_stride: 2` with `aux_weight: 0.5`, but the note describes the method as
  single-frame and rests the occlusion argument on statelessness. Measure what
  the window actually buys before deciding whether to keep it -- and if it is
  kept, rewrite the claim to "no tracking state to lose" rather than
  "stateless".
- **Report pose metrics on more than a quarter of the validation set.**
  `solve_every: 4` makes `trans_mm` a noisy subsample, which is why it swings
  between 8.7 and 16.2 mm across neighbouring epochs while `coord_mm` moves
  smoothly. For the final evaluation, solve every frame.

---

## Suggested order

1. Item 1, on the existing checkpoint. No retraining.
2. Item 2 (uncertainty head), now that `huber_delta` is fixed.
3. Then coverage (item 4), then calibration (item 3).
