# Revision of the TBME draft (`sn-article.tex`), 11 Nov 2026

This file holds revised text for the draft, section by section, ready to paste into Overleaf. It contains no code: every table below is plain text for you to set in LaTeX, and every new number links to the run file it comes from. Sections not listed here stay as they are.

**Framing (applies to every section).** The paper presents a different, data-driven solution for tracker-free freehand 3D US: a room learned by one scene coordinate network, localising every frame on its own. It does not claim to be more accurate than RGB-D SLAM. ORB-SLAM3 is the reference and is reported honestly: it is more accurate, also like for like, and it does not need the room scan to cover the examination views. What the paper offers instead is (1) the approach itself, new for this application; (2) the conditions under which it works, and a protocol that makes them explicit; (3) properties that follow from per-frame localisation against a fixed learned map: no tracking state, a bounded error under occlusion, and failures that can be detected.

**Wording to use throughout.**
- "a different route", "an alternative to SLAM", "per-frame relocalisation against a learned room model"; never "outperforms", "beats" or "state of the art".
- ORB-SLAM3 modes, always named the same way: *full SLAM* (maps the room scan and keeps mapping during the sweeps), *localisation only* (maps the room scan, then the map is frozen), *each frame relocalised* (frozen map, every sweep frame relocalised with nothing from the previous frame).
- "as tracked" for poses as the system reports them live; "refined at shutdown" for ORB-SLAM3's saved trajectory.

**New figures** (in `figures/`, drawn by `make_fig_results.py` from the result files):
- `fig_orbslam_persweep.pdf`: every sweep, our error against ORB-SLAM3 with each frame relocalised.
- `fig_occlusion.pdf`: per-sweep error under the synthetic occluder, ours and the three ORB-SLAM3 modes.

---

## Paper structure and length (target 10 pages, at most 11)

**Where the draft is now.** The draft has about 8,900 words, four full-width tables, an algorithm and six to seven figures. With the new ORB-SLAM3 and occlusion subsections this comes to roughly 13–14 pages in the IEEE two-column journal format. Reaching 10–11 pages needs about a quarter of the text cut, not only in the introduction. The budget below is a guide; check it after the first compile in Overleaf.

| Part | Now (approx.) | Target | How |
|---|---|---|---|
| Abstract | 250 words | 250 | TBME limit; the revised abstract below fits |
| I. Introduction | 1,050 words | 750 | shortened version below (29 % shorter) |
| II. Related work | 730 words | 550 | four subsections merged into three (below) |
| III. Method | 2,600 words + algorithm + 2 figures | 2,100 | order below; "Design Choices" cut to three sentences, the rest moves to the Discussion; "Implementation" moves to Experiments |
| IV. Experiments | 1,100 words + 1 table | 1,000 | "Compared Systems" split into Baselines and Ablations (below); "Ground Truth" shortened to two sentences, the rest to Limitations |
| V. Results | 2,700 words + 3 wide tables + 4 figures | 2,100 | the US-image tests and the table "Comparison with a tracker-made map for every system" move to the supplementary material; "Probe Calibration" and "Practical Aspects" shortened |
| VI. Discussion, VII. Conclusion | 900 words | 750 | the new paragraphs below replace three old ones |

**Supplementary material.** TBME accepts supplementary files that do not count towards the page limit. Candidates: the ultrasound-image tests (Sec. V on US images), the full comparison table with pose regression and the hybrid system, the per-block S-ctrl table with generic scans, the strict-protocol and real-time variants, the training-length study, and the ground-truth check.

**Method: order of the subsections.** Keep "Training Labels and Loss" before self-mapping: the mapping rounds train the network with this same loss, so it has to be defined first. What should move is "Per-Frame Pose Estimation": self-mapping also localises frames with the Kabsch RANSAC, so define it before self-mapping too. Suggested order:
1. Problem statement and notation
2. Scene coordinate network
3. Training labels and loss
4. Per-frame pose estimation (Kabsch RANSAC, inlier gate)
5. Self-mapping without a tracker (uses 3 and 4; Algorithm 1)
6. Probe calibration
7. Temporal smoothing
8. Room-scan protocol and checks

This reads as "the learned part, how a pose is computed from it, how the map is built from both, and how it is used". "Design Choices" can shrink to three sentences at the end of the method (geometry instead of pose regression; no learned temporal model; X not learnable from images) with the evidence left to the Results.

**Implementation.** Yes, move it to Experiments, as "Implementation Details", after the hardware: it describes the computing set-up and run times, not the method. The run times themselves (60–70 ms per frame; ORB-SLAM3 25–41 ms) are results and belong to the Results or Discussion.

**Experiments: Baselines and Ablations instead of "Compared Systems".** The current subsection mixes two kinds of experiment. Split it:
- *Baselines* (other methods, to compare with): the classical feature pipeline (SIFT anchors and odometry), pose regression, US-only motion estimation (Li et al.), and ORB-SLAM3 in its three modes.
- *Ablations* (our system with one part changed, to explain it): the oracle map (tracker labels instead of self-mapping), self-mapping without loop closures or without the calibration, odometry added (the hybrid), odometry only, and the room-scan variants (exam-view vs. generic scan, both scans in one map, scan length).
- The controlled occlusion is a third kind, a robustness test; keep it as its own subsection.

The Results can then follow the same split: "Ablations" (what each part contributes, what the scan must contain) and "Comparison With Baselines" (with RGB-D SLAM as its own subsection), then "Robustness: scene changes and occlusion".

**Related work: application first, then methods.** The current order, from the clinical problem (tracked and sensorless freehand 3D US, camera-based probe tracking) to the methods (visual relocalisation, SCR, SLAM), is the usual order for TBME, whose readers come for the application. The method sections then explain where the technique comes from. Keep it, and merge the last two subsections into one (text below).

---

## Abstract (replace)

*Objective:* Freehand three-dimensional (3D) ultrasound (US) needs the six-degree-of-freedom pose of every US image, which is usually measured by an external optical or electromagnetic tracker. We present a data-driven alternative that obtains these poses from a probe-mounted RGB-D camera alone, and we establish when it is accurate enough for 3D compounding. *Methods:* Before the examination, the operator scans the room with the probe camera for 1–2 min. One scene coordinate regression network maps this scan itself, is trained on its own labels, and then localises every examination frame independently by a Kabsch RANSAC fit to the measured depth. We evaluated 63 test sweeps in three sessions in one room, on two subjects and a phantom, against an optical tracker, and compared with ORB-SLAM3 under the same protocol. *Results:* With a room scan along the examination views, the error at the US image was 2.2–3.1 mm (volume shape 1.7–1.9 mm), 0.4–0.5 mm above the same network trained on tracker poses. A scan that missed the examination views raised the error on the same sweeps from 2.28 to 13.57 mm, and to 10.95 mm even with tracker labels. ORB-SLAM3 was more accurate, also with its map frozen after the room scan (2.33 vs. 3.58 mm), and did not need this coverage. Under a synthetic occluder covering 60 % of the image, our error rose by at most 0.9 mm on average with no sweep above 8.5 mm, whereas ORB-SLAM3 failed on single sweeps by 13–132 mm while reporting successful tracking. *Conclusion:* Per-frame localisation against a self-mapped, learned room model is a feasible tracker-free alternative for freehand 3D US when the room scan covers the examination views; it trades accuracy for a bounded error and detectable failures. *Significance:* The approach removes external tracking hardware, and the identified operating conditions translate into a short scanning protocol with checks before the examination.

Sources: [summary.md 4.9–4.11](../summary.md), [stats-orbslam.md](../runs/stats-orbslam.md), [stats-occ60.md](../runs/stats-occ60.md), [shape-reloc-occ.md](../runs/shape-reloc-occ.md).

Note: the old abstract said "65 sweeps in four sessions"; 2 of the 65 are validation sweeps (S-val), so "63 test sweeps in three sessions" is the accurate count for results. Keep "65 sweeps in four sessions" in the Methods paragraph of the paper if you prefer, but not in the Results sentence.

---

## I. Introduction (shortened: replace the whole section)

About 750 words instead of 1,050 (29 % shorter). The roadmap sentence at the end of the section is dropped (IEEE journals do not need it). Citation keys are those of the draft.

Freehand three-dimensional (3D) ultrasound (US) reconstructs a volume from 2D images acquired while the operator sweeps a conventional probe, giving access to organ and lesion volumes, vessel courses and planes for needle guidance [TODO-3dus-clinical-applications]. Reconstruction needs the six-degree-of-freedom (6-DoF) pose of every image, which in practice comes from an optical or electromagnetic tracker [TODO-freehand-3dus-review]. Optical tracking needs a line of sight that the operator, the patient and staff interrupt; electromagnetic tracking needs a field generator next to the patient and is disturbed by metal [TODO-em-tracking-distortion]. Both must be installed and calibrated in each room, which rules them out where a volume would be useful at short notice: at the bedside, in the emergency department, or in a crowded operating room [TODO-point-of-care-3dus].

A replacement does not have to match optical tracking; it has to be good enough for compounding, which we take as about 2–3 mm at the US image, of the order of the elevational beam width [TODO-elevational-beamwidth]. For a camera on the probe, rotation dominates this budget: the image lies about 16 cm from the camera, so 1° of rotation moves it by up to 2.8 mm.

A replacement must also give an absolute pose for every frame, need no preparation of the room or the patient, and keep everything on the probe. Sensorless methods estimate motion from the US images [prevost2018, guo2023tbme, li2024longterm, li2025tusrec], and probe-mounted cameras track skin features [sun2014skin] or use visual–inertial odometry [buchanan2024vio, he2024probemounted]; all integrate relative motion and drift. Absolute camera-based methods rely on something prepared in advance: a surface model of the anatomy [wang2017probesight], a marker-textured workspace [huang2025lightweight, zhang2026seeing] or a simulated replica of the scene [zhang2025servoing]; markerless tracking from an external camera [zhang2026mlrecon] brings back a line-of-sight constraint. RGB-D simultaneous localisation and mapping (SLAM), such as ORB-SLAM3 [campos2021orbslam3], meets all three requirements, and inside-out SLAM from a probe-mounted RGB-D camera has been shown for transrectal 3D US [busam2018insideout]. It represents the room by keypoints, tracks the camera from frame to frame and relocalises when tracking is lost, and it is the natural reference for any tracker-free design.

We take a different, data-driven route: every frame is relocalised independently against a learned model of the room, built from a 1–2 min scan with the probe camera before the examination. A scene coordinate regression (SCR) network [shotton2013, brachmann2022dsac, brachmann2023ace] predicts, for every image cell, the 3D room point it observes, and the pose follows from an exact fit to the measured depth. The network only has to memorise one room; RANSAC over thousands of dense correspondences discards cells on moved objects or hands; and the network maps the room scan itself, as in ACE0 [brachmann2024ace0] but with the measured depth, so no tracker is needed to build the map. There is no tracking state that can be lost or carry a wrong pose forward, and the accuracy is fixed by the map before the first sweep: the map, and how the room scan is recorded, become the object of study.

We ask four questions on 63 test sweeps in three sessions: what removing the tracker from mapping costs, what decides the accuracy, how a learned per-frame localiser compares with RGB-D SLAM, and when it fails. With a room scan along the examination views, the error at the US image is 2.2–3.1 mm, 0.4–0.5 mm more than with tracker labels. A scan that misses these views costs about 9 mm even with perfect labels, because the network cannot place viewpoints it has not seen. ORB-SLAM3 is more accurate in every session, also with its map frozen after the room scan, and does not need this coverage; our approach instead keeps a bounded error under occlusion, where ORB-SLAM3 occasionally loses a whole sweep while reporting successful tracking.

The contributions of this paper are:
- A tracker-free probe-tracking approach for freehand 3D US: one SCR network maps a 1–2 min room scan by itself, with depth-aided self-mapping (ICP seeding, a pose graph with loop closures, a camera-frame probe calibration), and then localises every frame independently.
- A validation against an optical tracker at the US image, on 63 test sweeps with two subjects and a phantom, that separates mapping from tracking and placement from volume shape, and compares with US-only motion estimation, a classical feature pipeline, pose regression and ORB-SLAM3 in three modes.
- The operating conditions of the approach from controlled experiments (coverage of the examination views, map quality, scene changes and occlusion) and a resulting room-scan protocol with checks before the examination.

The ablation numbers of the old second contribution (5.77 and 11.49 mm without loop closures or calibration) stay in the Results; they do not need to be in the introduction.

Sources: as in the paragraphs of the earlier revision; [stats-orbslam.md](../runs/stats-orbslam.md), [summary.md 4.11](../summary.md).

---

## II. Related Work

### A. Tracked and Sensorless Freehand 3D US: unchanged

### B. Camera-Based Probe Tracking: delete the last sentence

Delete "Apart from inside-out SLAM, our setting differs from the methods above: ..." to the end of the subsection; the introduction already says it.

### C and D merged: "Visual Relocalisation and SLAM" (replace both subsections)

Absolute pose regression maps an image directly to a pose [TODO-posenet], but such networks behave more like image retrieval than geometric estimation, which limits their accuracy [sattler2019]. Scene coordinate regression instead predicts dense image-to-scene correspondences and solves the pose robustly. It was introduced with regression forests on RGB-D images [shotton2013], adapted to new scenes online [cavallari2017onthefly, cavallari2019online], trained end to end through a differentiable RANSAC in DSAC* [brachmann2022dsac], made fast to train by ACE [brachmann2023ace], and improved for viewpoints far from the mapping images by ACE-G [bruns2025aceg]. ACE0 removes the need for mapping poses by alternating between training the relocaliser on the images registered so far and registering further images with it [brachmann2024ace0]. Our self-mapping follows this scheme but uses the measured depth for metric labels, ICP seeding and extension and a 3D–3D solver, refines the poses by a pose graph with ICP loop closures instead of joint refinement, and adds a camera-frame probe calibration. Keypoint-based RGB-D SLAM, such as ORB-SLAM3 [campos2021orbslam3], tracks keypoints from frame to frame, optimises keyframes by bundle adjustment and relocalises by place recognition; ACE-SLAM uses SCR as the map of a real-time RGB-D SLAM system, training it online [alzugaray2025aceslam]. We instead map once before the examination and keep the network fixed. In medicine, relocalisation against a prior reconstruction has been studied mainly in endoscopy, where the map is of the anatomy [TODO-endoscopic-relocalisation]; to our knowledge, SCR has not been used for freehand 3D US.

---

## IV. Experiments

### E. Baselines (was "Compared Systems"): the ORB-SLAM3 paragraph (replace the sentences on ORB-SLAM3; the oracle map, hybrid and odometry-only systems move to the new "Ablations" subsection)

*ORB-SLAM3* [campos2021orbslam3] in RGB-D mode with its default ORB vocabulary, 1250 ORB features on 8 pyramid levels (scale factor 1.2), viewer off, playing each sequence in real time. Each session is exported as one sequence: the room scan(s), then the sweeps. We run it in three modes. *Full SLAM:* it maps the room scan and keeps mapping during the sweeps, with loop closing. *Localisation only:* it maps the room scan, after which mapping is switched off, so the sweeps are tracked against a frozen room-scan map, the information our system has. *Each frame relocalised:* as localisation only, but before every sweep frame the tracking state is reset, so each frame is relocalised against the frozen map with nothing from the previous frame, the task our network solves. In localisation mode, ORB-SLAM3 relocalises only after it has declared the camera lost, which in this mode never happens; we changed one line so that it relocalises as soon as tracking fails. We score the poses as tracked, i.e. as a live system would show them, and for full SLAM also the trajectory refined at shutdown. The alignment and ORB-SLAM3's own probe calibration are fitted on the room-scan frames only, as for ours; its S-test calibration is reused on the other sessions; poses are smoothed over 1 s; frames not tracked count as without a pose.

To fill in: the ORB-SLAM3 version (commit) you built.

### New subsection after E: "Controlled Occlusion"

To test how each system degrades when part of the view is blocked, as by the operator's hand or arm, we added a synthetic occluder to the sweep frames of S-ctrl B and C (16 sweeps). It is a band over the full image height and 30 % or 60 % of the image width, filled with a skin-like colour and a fixed texture, so that keypoint detectors find corners on it, at a depth of 0.4 m. It appears for 3 s every 10 s, starting 5 s into each sweep and alternating between the left and right side, so that about 30 % of the sweep time is occluded. The room scans are not occluded. Both systems receive identical frames.

Source: `occlusion.py` (repository root).

### C. Protocol and Reporting Rules (add at the end)

Seed spread was measured with three training seeds on S-test and on every S-ctrl block. To compare with ORB-SLAM3 we pair the systems by sweep and report the mean difference with a 95 % bootstrap interval and a Wilcoxon signed-rank test. As a check that the tracker does not reach the reported numbers through the smoothing, we also smoothed every sweep as one piece instead of restarting at the breaks caused by tracker dropouts; the results were identical to two decimals on all splits.

Sources: [stats-orbslam.md](../runs/stats-orbslam.md) (seeds at the end), the `*-gapfree` track folders, e.g. [track-v2map-4XXA-gapfree](../runs/track-v2map-4XXA-gapfree/scr_track.md).

### D. Metrics (add one sentence)

*Worst sweep:* the largest per-sweep median of a split, reported where single sweeps fail.

---

## V. Results

### A. Tracking With a Covering Room Scan: replace the ORB-SLAM3 sentence

Replace "ORB-SLAM3 posed every frame and is more accurate than our system and than our oracle map, in placement (1.79 mm) and in shape (1.34 mm)." with:

ORB-SLAM3 tracked every frame in every mode and is more accurate than our system and than our oracle map: 1.72–1.84 mm absolute and 1.18–1.38 mm shape, also with its map frozen after the room scan (Sec. V-G).

### Table "S-test" (tab:test): replace the ORB-SLAM3 row by four rows

| System | Tracker | Abs. | Shape | Out-of-plane 8 / 30 | Jitter | Posed |
|---|---|---|---|---|---|---|
| ORB-SLAM3, full SLAM, refined at shutdown | own calib. | 1.79 | 1.34 | 0.25 / 0.45 | 0.73 | 100 % |
| ORB-SLAM3, full SLAM, as tracked | own calib. | 1.81 | 1.18 | 0.23 / 0.38 | 0.67 | 100 % |
| ORB-SLAM3, localisation only | own calib. | 1.84 | 1.30 | 0.25 / 0.43 | 0.68 | 100 % |
| ORB-SLAM3, each frame relocalised | own calib. | 1.72 | 1.38 | 0.26 / 0.44 | 0.76 | 100 % |

Add to the caption: "ORB-SLAM3 poses are smoothed over 1 s, ours over 2 s on S-test (1 s gives 2.36 mm)."

Sources: [slam-3XX/slam_eval.md](../runs/slam-3XX/slam_eval.md), [slam-3XX-online](../runs/slam-3XX-online/slam_eval.md), [slam-3XX-loc](../runs/slam-3XX-loc/slam_eval.md), [slam-3XX-reloc](../runs/slam-3XX-reloc/slam_eval.md); shape and out-of-plane from [shape-slam.md](../runs/shape-slam.md), [shape-slam-fair.md](../runs/shape-slam-fair.md), [shape-reloc-occ.md](../runs/shape-reloc-occ.md).

To fill in: the "Posed" column for our rows (frames passing the 400-inlier gate) from `runs/repro/track-v2map-3XX/scr_track.md`.

### Table "S-ctrl" (tab:ctrl): the ORB-SLAM3 column (localisation only, absolute / shape)

| Block | Room scan | ORB-SLAM3 |
|---|---|---|
| A reference | exam-view | 3.79 / 1.34 |
| A reference | generic | 2.88 / 1.19 |
| B large change | exam-view | 1.70 / 1.17 |
| C very large | exam-view | 2.05 / 1.11 |
| D people moving | exam-view | 1.60 / 1.74 |
| E empty room | exam-view | 2.65 / 0.99 |
| C very large, outdated | B's map | 19.19 / 10.58, sweeps 5–8 only (1–4 not tracked) |
| E empty room, outdated | C's map | 4.19 / 2.51 |

The rows "B with A's map" and "C with A's map" were not run with ORB-SLAM3: put "–". Note that B's outdated map for ORB-SLAM3 is B's generic scan (room-504), as for ours.

Sources: [stats-orbslam.md](../runs/stats-orbslam.md) section "loc"; [shape-slam-fair.md](../runs/shape-slam-fair.md).

### Table "S-new" (tab:snew): the ORB-SLAM3 column (localisation only, absolute / shape)

| Block | ORB-SLAM3 |
|---|---|
| A new session | 4.47 / 1.43 |
| B small change | 3.80 / 1.10 |
| C large change | 4.90 / 1.25 |
| D second subject | 4.64 / 1.58 |
| E arm in view | 24.03 / 7.41 (a) |
| Mean | 8.37 / 2.55; A–D 4.45 / 1.34 |

(a) One sweep with an arm across the view is 81.5 mm off while ORB-SLAM3 reports tracking; over three runs this sweep gave 81.5, 4.65 and 28.2 mm (block E 24.0, 5.0, 10.9 mm); with each frame relocalised, 5.03 mm.

Sources: [slam-4XXE-loc](../runs/slam-4XXE-loc/slam_eval.md), [slam-4XXE-loc-r2](../runs/slam-4XXE-loc-r2/slam_eval.md), [slam-4XXE-loc-r3](../runs/slam-4XXE-loc-r3/slam_eval.md), [slam-4XXE-reloc](../runs/slam-4XXE-reloc/slam_eval.md).

### C. What Decides the Accuracy, S-new paragraph: replace "ORB-SLAM3 gives \ORBP."

ORB-SLAM3 with its map frozen after the same scans gives 4.45 / 1.34 mm on blocks A–D; block E is discussed in Sec. V-H.

### D. Scene Changes: replace "ORB-SLAM3 with the same outdated scans: \ORBP." (after the outdated-map figure)

ORB-SLAM3 also fails after the very large rearrangement when run live: with B's map frozen it does not track the first four C sweeps and is 19.2 mm off on the other four, and in full SLAM it is 43.7 mm off as tracked, recovering only in the trajectory refined at shutdown (4.65 mm), after merging a new map with the old one. With C's map on the emptied room E it gives 4.19 mm.

Sources: [slam-5XXC-oldB-loc](../runs/slam-5XXC-oldB-loc/slam_eval.md), [slam-5XXC-oldB-online](../runs/slam-5XXC-oldB-online/slam_eval.md), [slam-5XXC-oldB](../runs/slam-5XXC-oldB/slam_eval.md), [slam-5XXE-oldC-loc](../runs/slam-5XXE-oldC-loc/slam_eval.md).

### New subsection G: "Comparison With RGB-D SLAM" (insert after "Comparison With Other Approaches")

ORB-SLAM3 is more accurate than our system in every session and in every mode (Table X, Fig. Y). With its map frozen after the room scan and every frame relocalised on its own, the task our network solves, it gives 1.72 mm on S-test, 4.45 mm on S-new and 2.33 mm on S-ctrl, against 2.34, 7.92 and 3.58 mm for ours; per sweep it is lower on 52 of 63 sweeps (Wilcoxon p < 0.001). Freezing the map or removing frame-to-frame tracking barely changes its accuracy (S-ctrl 2.15 mm as tracked in full SLAM, 2.36 in localisation only, 2.33 with each frame relocalised), so its advantage lies in its map, not in mapping during the sweeps. In particular, it does not need the room scan to cover the examination views: on S-ctrl A with the generic scan it gives 2.76 mm, where ours gives 13.57 mm. Its keypoints are 3D points with local descriptors that can be matched from viewpoints the room scan did not contain; our network regresses room coordinates and does not extrapolate to such viewpoints. Ours is more accurate only on S-ctrl A with the exam-view scan (2.28 vs. 3.90 mm, all 8 sweeps). Relocalising a frame takes ORB-SLAM3 25–41 ms on the CPU (median), our system 60–70 ms on the GPU.

Table X (absolute / shape, mm; ORB-SLAM3 poses as tracked unless stated):

| System | S-test | S-new | S-ctrl (exam-view) | S-ctrl A, generic scan | S-ctrl C, outdated scan |
|---|---|---|---|---|---|
| Ours | 2.34 / 1.72 | 7.92 / 2.69 | 3.58 / 2.24 | 13.57 / 3.79 | 40.9 / 29.2 |
| ORB-SLAM3, full SLAM, refined at shutdown | 1.79 / 1.34 | 3.55 / 1.29 | 2.33 / 1.11 | – | 4.65 / 1.15 |
| ORB-SLAM3, full SLAM | 1.81 / 1.18 | 4.47 / 2.28 | 2.15 / 1.08 | 3.16 / 1.09 | 43.69 / 3.51 |
| ORB-SLAM3, localisation only | 1.84 / 1.30 | 8.37 / 2.55 (A–D 4.45 / 1.34) | 2.36 / 1.27 | 2.88 / 1.19 | 19.19 / 10.58 (4 of 8 sweeps) |
| ORB-SLAM3, each frame relocalised | 1.72 / 1.38 | 4.45 / 1.44 | 2.33 / 1.10 | 2.76 / 1.17 | 19.97 / 14.95 (3 of 8 sweeps) |

Caption suggestion: "Comparison with ORB-SLAM3 (RGB-D) under the same protocol. Localisation only: map from the room scan, then frozen. Each frame relocalised: frozen map, every sweep frame relocalised with nothing from the previous frame. Session means of per-sweep medians at the US image."

Fig. Y: `figures/fig_orbslam_persweep.pdf`. Caption suggestion: "Every test sweep, our error against ORB-SLAM3 with each frame relocalised against its frozen room-scan map (log scales). Points below the diagonal: ORB-SLAM3 lower (52 of 63 sweeps with current maps). Diamonds: S-ctrl A with the generic scan that misses the examination views."

Sources: [stats-orbslam.md](../runs/stats-orbslam.md) (all modes, paired statistics); per split: `runs/slam-*-reloc/slam_eval.md`, `runs/slam-*-loc/`, `runs/slam-*-online/`, `runs/slam-*/`; shape: [shape-slam.md](../runs/shape-slam.md), [shape-slam-fair.md](../runs/shape-slam-fair.md), [shape-reloc-occ.md](../runs/shape-reloc-occ.md); timing: `runs/slam-*-reloc/times.txt` (training PC) and [summary.md 4.11](../summary.md).

Note on the counts: ORB-SLAM3 is lower on 49–52 of 63 sweeps depending on the mode (full SLAM 51, localisation only 49, each frame relocalised 52). Use "52 of 63" only with the per-frame mode.

### New subsection H: "Robustness to Occlusion"

With the synthetic occluder (Sec. IV-F), our error rises by 0.4–0.9 mm on average and no sweep exceeds 8.5 mm; the inlier gate drops the frames that cannot be placed (87–100 % of frames posed) (Table Z, Fig. W). ORB-SLAM3 stays more accurate on average, but in every mode it fails on single sweeps while reporting successful tracking for every frame: on S-ctrl B, 132 mm in localisation only with 30 % occluded, and 38.6 mm (full SLAM), 39.7 mm (each frame relocalised) and 12.9 mm (localisation only) with 60 % occluded. With 60 % occluded on S-ctrl C, it relocalises only 3 of 8 sweeps when each frame is relocalised. These failures also distort the volume: with 60 % occluded on S-ctrl B, the shape error is 3.88 mm for ours and 7.35–8.44 mm for ORB-SLAM3 in every mode. The same pattern appeared without a synthetic occluder in S-new E, where an arm crossed the view in two sweeps: localisation-only ORB-SLAM3 was 81.5 mm off on one of them in one run and 28.2 mm in another, while ours gave 6.9 mm. The failures are rare and vary from run to run; the evidence covers two blocks and one occluder.

Table Z (mean of per-sweep medians at the US image, worst sweep in brackets, then shape; mm):

| Block, occluded | Ours | ORB-SLAM3, full SLAM | localisation only | each frame relocalised |
|---|---|---|---|---|
| B, none | 4.43 (6.3) / 2.81 | 1.79 / 1.22 | 1.70 / 1.17 | 1.63 / 1.20 |
| B, 30 % | 5.16 (7.5) / 3.38 | 1.76 (2.9) / 1.44 | 17.91 (132.2) / 6.14 | 1.78 (2.9) / 1.59 |
| B, 60 % | 5.28 (8.5) / 3.88 | 6.88 (38.6) / 7.42 | 3.32 (12.9) / 8.44 | 6.72 (39.7) / 7.35 |
| C, none | 3.11 (5.1) / 1.76 | 1.67 / 1.09 | 2.05 / 1.11 | 2.27 / 1.06 |
| C, 30 % | 3.54 (6.1) / 2.27 | 2.12 (2.6) / 1.15 | 2.48 (2.9) / 1.38 | 2.01 (2.3) / 1.32 |
| C, 60 % | 3.89 (6.6) / 2.80 | 2.67 (3.3) / 1.83 | 2.65 (3.1) / 2.29 | 2.22 (2.5) / 3.20, 3 of 8 sweeps |

Fig. W: `figures/fig_occlusion.pdf`. Caption suggestion: "Controlled occlusion on S-ctrl B and C: per-sweep error at the US image without the occluder and with 30 % or 60 % of the image width occluded (log scale). Each point is one sweep. Our error stays bounded; ORB-SLAM3 is lower on average but fails on single sweeps while reporting successful tracking."

Sources: [stats-occ30.md](../runs/stats-occ30.md), [stats-occ60.md](../runs/stats-occ60.md), [shape-reloc-occ.md](../runs/shape-reloc-occ.md); ours [track-v2map-5XXB-exam-occ60](../runs/track-v2map-5XXB-exam-occ60/scr_track.md) (and `-occ30`, the 5XXC folders); ORB-SLAM3 `runs/slam-5XX?-exam-occ??-{online,loc,reloc}/slam_eval.md`; without the occluder: [slam-5XXB-exam-online](../runs/slam-5XXB-exam-online/slam_eval.md) and the `-loc`, `-reloc` folders; shape without the occluder from [shape-slam-fair.md](../runs/shape-slam-fair.md) and [shape-5XX.md](../runs/shape-5XX.md).

### Practical Aspects (add)

Three training seeds per S-ctrl block give a spread of 0.03–0.27 mm (A 2.26 ± 0.03, B 4.20 ± 0.23, C 3.17 ± 0.12, D 2.22 ± 0.03, E 6.00 ± 0.27 mm), so the block results do not depend on the seed.

Source: [stats-orbslam.md](../runs/stats-orbslam.md), section "Our seeds".

---

## VI. Discussion

### "Coverage is the central requirement" (replace the paragraph)

*Coverage is the central requirement of a learned map.* A network that learns the room from a scan is accurate only near the viewpoints of that scan: with perfect labels, a scan that misses the examination views still gives 10.95 mm instead of 1.85 mm. This is a limit of regressing scene coordinates, not of self-mapping and not of mapping the room before the examination: ORB-SLAM3 with the same generic scan, frozen, gives 2.76 mm, because its keypoints can be matched from new viewpoints. For the operator, the consequence is concrete: scan along the planned sweep paths, which takes about 1–2 min. More footage does not substitute for the right footage: adding a generic scan made the map worse (3.15 vs. 2.28 mm). Training that makes scene coordinate networks extrapolate to new viewpoints, as ACE-G does for RGB [bruns2025aceg], is the most direct way to relax this requirement.

### "Relation to RGB-D SLAM" (replace the paragraph)

*A learned map and a keypoint map.* RGB-D SLAM is the established way to track a probe camera against the room [busam2018insideout], and ORB-SLAM3 is more accurate than our system in every session, also when both use only the room scan; we do not claim higher accuracy. The comparison shows where the difference lies. It is not the tracking over time and not mapping during the examination: ORB-SLAM3 keeps its accuracy with its map frozen and every frame relocalised on its own. It is the map: sparse keypoints with descriptors generalise to viewpoints the room scan missed, and a network that regresses room coordinates does not. What the learned, per-frame approach offers instead is a different failure behaviour. It holds no tracking state, so a wrong pose is not carried into the next frame, and its error stays bounded when part of the view is blocked (no sweep above 8.5 mm with 60 % of the image occluded). ORB-SLAM3, more accurate on average, occasionally loses a whole sweep by tens of millimetres while reporting successful tracking, in every mode, and these failures vary from run to run. For compounding, a silent failure of a whole sweep is harder to handle than a known, bounded error. The two approaches are complementary: ORB-SLAM3 could be guarded by an independent per-frame check, and per-frame scene coordinate relocalisation could be used inside SLAM, as in ACE-SLAM [alzugaray2025aceslam].

### "Failure modes and their detection" (replace the paragraph)

*Failure modes and their detection.* Low coverage is silent: every frame passes the inlier gate, and only the coverage check catches it. An outdated map after a very large change fails with low inlier counts, which a session-level median-inlier check flags; ORB-SLAM3 fails in the same situation when run live. An empty room gives a poor map, which the map error reveals only with a reference; this case calls for adding structure to the room. Occlusion of part of the view degrades our error gradually rather than abruptly.

(The other Discussion paragraphs stay.)

---

## Limitations (replace the subsection)

ORB-SLAM3 is more accurate than our system in every session, also like for like, and does not need the room scan to cover the examination views. Its localisation mode needed a one-line change to relocalise after tracking failures, and it varies from run to run, so single runs of it should be read with care. The occlusion experiment uses one synthetic occluder on two blocks; real hands and arms differ in shape, motion and depth. All data come from one room, two subjects and one phantom, and the test sets are small (5 + 26 + 32 sweeps). $X$ was fitted with the tracker, and the coverage check was computed with the tracker, so the workflow is not yet fully tracker-free. The ground truth was recorded at the near edge of the tracker volume; no trend with distance was found, but a common bias cannot be excluded, and the hand–eye error enters the ground truth. The median-inlier threshold was not tuned on independent data. The tracking ablations and the frame-level coverage analysis use the oracle map; their transfer to a self-made map is assumed. The pooled-scan variant was examined on S-new test blocks. Real time was shown on recorded data, not live.

(Keep the LaTeX math for $X$ as in your draft.)

---

## VII. Conclusion (replace)

A probe-mounted RGB-D camera and one scene coordinate network that maps its own room scan give the pose of every freehand US frame without an external tracker. With a room scan along the examination views, the error at the US image is 2.2–3.1 mm in two sessions, 0.4–0.5 mm more than with tracker labels. Coverage of the examination views decides the accuracy, then map quality, then scene changes; a short exam-view scan, a coverage check and an inlier check make these conditions explicit before the examination. ORB-SLAM3 is more accurate and does not need this coverage; the learned per-frame approach offers a bounded error under occlusion and detectable failures instead. Scene coordinate networks that generalise to new viewpoints, and their combination with SLAM, are the directions that would close the gap.

---

## Figures: status

| Figure in the draft | File | Status |
|---|---|---|
| Comparison with ORB-SLAM3 (new) | `figures/fig_orbslam_persweep.pdf` | done, from result files |
| Controlled occlusion (new) | `figures/fig_occlusion.pdf` | done, from result files |
| Error against coverage | `figures/fig_coverage_error.pdf` | present; check that it is referenced in the text |
| System overview (fig:overview) | `figures/fig_overview.pdf` | missing; `fig_concept.pdf` and `fig_pipeline.pdf` are present, either can replace it |
| Network (fig:architecture) | `figures/fig_architecture.pdf` | present |
| Volume, coverage (fig:volume) | `figures/fig_volume_coverage.png` | to make on the training PC with `make_fig_volumes.py` (S-ctrl A, one sweep: exam-view vs generic map) |
| Volume, S-new (fig:volume_snew) | `figures/fig_volume_snew.png` | to make on the training PC (one S-test and one S-new sweep, as placed and after the rigid fit) |
| Volume, outdated map (fig:volume_outdated) | `figures/fig_volume_outdated.png` | to make on the training PC (S-ctrl C, current vs outdated map, with the inlier count over time) |

The three volume figures need the US images, which are only on the training PC; `make_fig_volumes.py` (restored) draws them, and writes the numbers of the shown sweep next to each figure (`.txt`) for the captions.

## Open items in the draft (not changed by this revision)

- `\NUMQ` placeholders: margin of the motion check in self-mapping, Tukey constant, robust loss of the calibration fit, joint-refinement numbers in Design Choices.
- `\tbd`: funding, probe and scanner model, phantom type, ethics approval, code availability, smoothing window bounds, ORB-SLAM3 version.
- "Posed" column in the S-test table for our rows.
- Bibliography keys starting with `TODO-`.
