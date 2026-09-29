## 2. Settled decisions

| Decision | Choice | Reason |
|---|---|---|
| Reference frame | Room frame | Rigid anatomy + still patient ⇒ room and patient frames differ by one fixed unknown transform |
| Camera direction | Outward, at the room | Room is textured and static; skin is textureless, curved, gelled |
| Method family | Scene coordinate regression | §3 |
| Backbone | EfficientNet-B0, truncated at stride 8 | The contribution is the formulation, not the block design |
| Anatomy | Spine, arm, leg — rigid bone | Removes deformation and breathing from the problem |
| Patient motion | Assumed away by protocol | Valid within a sweep; state as an explicit assumption |
| Hardware | One probe-mounted RealSense; NDI Polaris Vicra for GT only | More cameras possible later for occlusion resilience |
| Network input | Single frame — RGB + depth. No US, no IMU, no sequence | §7 |
| Temporal handling | Post-solver trajectory smoothing | Keeps the stateless-occlusion claim; per-frame estimates survive as fallback |

## 3. Why SCR, not pose regression

Both are supervised and EfficientNet-backed. The difference is where the six numbers come from.

**APR** — image in, pose out. Sattler et al. (CVPR 2019): behaves closer to image retrieval with interpolation than to geometric reasoning, bounded by training poses, decimetre-scale indoors. The target is ~1 mm. Not a tuning gap.

**SCR** — per-pixel 3D coordinates in the room frame; pose from PnP or Kabsch with RANSAC. Fully learned, no descriptors, no map database, no tracking loop, but geometry is *solved* rather than regressed. References: DSAC*, ACE, GLACE, R-SCoRe, unified in SCRStudio (CVPR 2025).

**Depth is not incidental.** Standard SCR regresses 3D from RGB alone and fights scale ambiguity. With metric depth the question becomes "where in the room does this measured 3D point belong" — easier regression, and a principled reason for the RGB-D sensor. Under-explored in the medical context.

**Occlusion advantage.** SCR is stateless. An occluded frame fails and the next recovers, with no tracker to lose lock; SLAM and render-and-compare both need explicit failure detection and re-initialisation. Report solve rate as a metric.

## 4. Literature and positioning

**Probe-mounted:** Buchanan 2024 (stereo VIO + deep inertial odometry, errors comparable to motion capture); He 2024 (binocular + IMU, UKF on Lie groups, 3.78 mm / 0.36°); Zhang 2025 (monocular visual servoing against a *prepared textured* workspace, Hausdorff 0.359–1.171 mm — not markerless in our sense); ProbeSight (camera on skin, inverse rendering against a surface atlas).

**External RGB-D, markerless:** MLRecon 2026 — the closest competitor. Commodity RGB-D on a tripod, FoundationPose render-and-compare against a probe CAD model, SAM2 divergence detection, temporal refinement. 0.88 mm / 0.48° back-and-forth, 1.44 mm spiral; beat ORB-SLAM (2.65 mm) and Zhang (1.46 mm) on matched trajectories.

**Sensorless:** RecON, MoNet/MoNetV2, DualTrack, Li et al., ~5% normalized drift. Dai 2024 uses nylon fiducials in a hydrogel pad — reduces drift, constrains the scanning surface, linear probes only.

**Positioning.** MLRecon explicitly frames probe-mounted sensors as intrusive; we need an answer. The differentiator is **infrastructure**: MLRecon needs an unobstructed external camera with the probe in view, this needs nothing outside the probe. Point-of-care, bedside, ambulance, cramped rooms.

## 5. Accuracy: a constraint, not the contribution

Set by physics, not chosen. Elevational beam width is 1–2 mm, so error much beyond 1 mm blurs the reconstruction and there is little value in being much better. Pass/fail gate.

Rotation dominates: at the 9 cm imaging depth in use, 1° puts 1.6 mm at the bottom of the image.

Reference points: optical ~0.5 mm; MLRecon 0.88 mm; Zhang 1.46 mm; He 3.78 mm; US-only ~1 cm over a 20 cm sweep. Landing among these is the aim, not ahead of them.

## 6. Ground truth and calibration

The Vicra changes **supervision**, not just evaluation. Dense SCR labels come straight from pose and depth, with no reconstruction step:

```
T_world_cam = T_world_marker · T_marker_cam
xyz_world   = T_world_cam · backproject(depth, K)
```

Most SCR work bootstraps labels from SfM; we get them metrically, per-pixel, per-frame. COLMAP / RTAB-Map pseudo-GT is now only a fallback. Tracker poses are supervision and evaluation only, never a runtime input.

**Units.** The tracker node publishes millimetres, and the pipeline now works internally in millimetres throughout (geometry, dataset, model, solver — an earlier metres-internally version was refactored away). `pose_units` defaults to `"mm"`, matching `record.py`'s own `--pose-units` default; the actual safety net is per-run rather than the default itself — `SCRDataset.__init__` reads each run's own `record_config.json` and raises if its recorded `pose.units` disagrees with what the dataset was configured for, so a wrong guess does not train silently even though the flag has a default.

**Hand-eye: translation measured, rotation not yet estimated.** 

The guess of calibration matrix si around 110, 20, 75 mm, not direction sign.

The calculated is : 
[[-4.27548383e-02  1.52818278e-02 -9.98968713e-01 -9.92511959e+01]
 [ 1.04557840e-01 -9.94323956e-01 -1.96857427e-02  2.24692641e+01]
 [-9.93599357e-01 -1.05291672e-01  4.09143251e-02  7.53086948e+01]
 [ 0.00000000e+00  0.00000000e+00  0.00000000e+00  1.00000000e+00]]


## 7. Inputs deliberately not used

**US is payload.** Camera-only pose estimation; US frames compounded afterwards. As a pose *input* it has a specific failure mode: US sees anatomy, the room frame is defined by the room, so on a single subject the model learns "this anatomical view implies this probe pose", validation looks excellent because train and validation come from the same body, and it transfers to nobody. If US returns, it returns as a geometric constraint between overlapping sweeps.

**IMU is out of scope.** Keep recording `imu.csv` — it costs nothing and cannot be retrofitted — but nothing reads it.

**Temporal structure goes after the solver.** The probe has mass and a hand on it, so the true trajectory is band-limited while per-frame jitter is not physical. Smooth the per-frame poses weighted by inlier count (SE(3) RTS, B-spline, or Savitzky-Golay with SLERP on rotation) — the same role as MLRecon's temporal refinement. State which downstream use a smoothed number applies to: offline reconstruction may use a non-causal smoother, live navigation may not.

## 8. Known challenges

- **Occlusion** by hand and body — constant, moving, probably the dominant practical failure mode. Statelessness helps; report solve rate and inlier counts. Needs a reproducible protocol, since it is now a headline result rather than a robustness check.
- **Scene specificity.** SCR regressors overfit to training views by design. Partly a feature — an exam room is fixed infrastructure and ACE-style mapping takes minutes, so "train once per room at installation" is plausible — but it must be tested: room A → room B, moved furniture, drawn curtains, people in the way, morning vs evening lighting. ACE-G addresses this via query pre-training.
- **Room-to-anatomy transform unknown.** Room-frame pose alone is not usable for reconstruction; one registration to anatomy is needed. Fine for a single sweep with an arbitrary origin, not for cross-session navigation. Be clear which claim is being made. 
- **Depth noise sets the label floor.** RealSense error grows with the square of range, reaching centimetres at a few metres. Coordinate error will floor there; pose error will not, per §3. Do not mistake one for the other.
- **Lock the capture settings** before the real dataset: RGB exposure and white balance, *and* scanner Depth, Sector Ext, Zoom. Changing scanner depth mid-dataset silently changes mm-per-pixel.

## 9. Data and recording

Runs are now being recorded with `record.py` with the marker pose stream live, so `frames.csv` carries interpolated pose columns per frame. The five original pilot runs predate the tracker, carry no pose, and are unusable for supervised training.

SCR needs pose-space coverage, not frame count. Plan many runs with varied paths, heights and orientations through the same room. Validate on held-out **trajectories**, not held-out frames, and not on runs retracing training paths.

**RGB/depth: full sensor, no crop.** `camera_info.json` reports 1280×720. The network input resolution (360×640 by default) is a same-aspect-ratio downsample, not a crop — 640/360 exactly matches 1280/720, so the crop box computed at load time equals the full frame before resizing. Fixed-box cropping is reserved for US only, for the reason above (a stable pixel→mm sector origin); RGB/depth have no equivalent constraint and lose field of view for nothing if cropped.

## 10. Pipeline status

Implemented, running end to end:

- `geometry.py` — `T_a_b` convention, SE(3) exp/log, pose loading with occlusion masking, dense scene-coordinate labels, target-free hand-eye consistency check
- `dataset.py` — per-frame SCR dataset; geometric augmentation with regenerated labels; stride-aligned label sampling; scene normalisation from the training split only; skips ineligible run directories (no pose columns, or no `camera_info.json`) with a printed reason instead of crashing; per-run `pose_units` cross-check against `record_config.json`
- `model.py` — EfficientNet-B0 to stride 8, depth fused at the stem with zero-initialised new channels, dilated fully-convolutional head, no pooling anywhere; Huber or Gaussian-NLL coordinate loss in fp32
- `solver.py` — PnP+RANSAC and Kabsch+RANSAC with inlier reporting
- `train.py` — coordinate loss, solver in the validation loop, epoch-level metric reduction, predict-the-centroid baseline printed before training; hand-eye loading (`load_hand_eye`) with unit conversion, rotation orthonormality/determinant checks, and a lever-arm plausibility bound; `--hand-eye-units` is required whenever `--hand-eye` is passed, with no default 

## 11. Baselines

| Baseline | Purpose |
|---|---|
| ORB-SLAM3 / RTAB-Map on the same stream | The SLAM comparison — must be beaten *under occlusion*, since SLAM is also infrastructure-free |
| APR head on the same encoder | Shows why pooled regression fails |
| ACE or DSAC* off the shelf | SCR reference; isolates what our adaptation adds |
| PnP vs Kabsch | Whether measured depth helps or hurts on the query side |
| Per-frame vs smoothed | How much accuracy is temporal, and at what latency cost |
| A US-only sensorless method | Drift comparison | 


 
### 2.1 `geometry.py`

**POSE_UNITS** — the table now scales *to* millimetres.  

Leave the exp/log, inverse, and quaternion round-trip assertions alone — they are unit-free.

### 2.2 `dataset.py`
 

### 2.3 `model.py`

**`coordinate_metrics` final line** — `scene_scale` is now already in mm. 

The docstring ("Per-pixel coordinate error in millimetres") stays correct.

### 2.4 `solver.py`

**`kabsch_ransac` threshold** 

**`pose_error`**

**Comments only**, no code change: the `xyz_world` parameter annotations in `pnp_ransac` and `kabsch_ransac` say "metres"; change to "millimetres". PnP itself is unit-agnostic as long as the inputs are consistent — `tvec` comes out in whatever unit went in.

### 2.5 `train.py`

**`centroid_baseline`**

**`--max-depth` default** 

### 2.6 Do NOT change these

They are already dimensionless or in non-length units. Touching them is the most likely way to break this refactor.

| Location | Quantity | Why it is unit-free |
|---|---|---|
| `model.py`, `CoordinateLoss(delta=0.05)` | Huber knee | Normalised units (fraction of `scene_scale`). At a ~2000 mm scene radius this is a ~100 mm knee, comparable to the ~75 mm it was before. |
| `dataset.py`, `inv = inv * valid / (1.0 / cfg.min_depth)` | inverse-depth normalisation | Evaluates to `min_depth / depth`, a ratio. |
| `dataset.py`, `xyz_n = (xyz_l - scene_center) / scene_scale` | label normalisation | Numerator and denominator are both mm. |
| `train.py`, `--reproj-threshold` | PnP inlier threshold | Pixels. |
| `dataset.py`, `scale_range`, `brightness`, `contrast`, `noise_std` | augmentation | Fractions. |
| `record.py` | entire file | Already writes mm. **No change at all.** |
 
 
