# Empty cells (--) in Tables III to V

Source: `/data2/u0137815/US_SCR/paper/main.tex`. Group: A not applicable (layout), B computable from existing files, C a run would be needed, ? no rule yet.

## Table III (`tab:test`)

| row | column | group | source | value / note |
|---|---|---|---|---|
| Proposed, exam-view scan \Prearra{} | Ref. | C | `runs/track-v2-5XXB-exam/scr_track.json` | no oracle checkpoint or track for this set (only P-ref has one) |
| Proposed, exam-view scan \Prearrb{} | Ref. | C | `runs/track-v2-5XXC-exam/scr_track.json` | no oracle checkpoint or track for this set (only P-ref has one) |
| Proposed, exam-view scan \Ppeople{} | Ref. | C | `runs/track-v2-5XXD-exam/scr_track.json` | no oracle checkpoint or track for this set (only P-ref has one) |
| Proposed, exam-view scan \Pempty{} | Ref. | C | `runs/track-v2-5XXE-exam/scr_track.json` | no oracle checkpoint or track for this set (only P-ref has one) |
| \quad strict protocol \Ftest{} | Map err. | A | `-` | same map as the row above / single seed |
| \quad strict protocol \Ftest{} | Seeds | A | `-` | same map as the row above / single seed |
| \quad real time / causal \Ftest{} | Ref. | A | `-` | no oracle run in real time |
| \quad real time / causal \Ftest{} | Map err. | A | `-` | same map as the row above / single seed |
| \quad real time / causal \Ftest{} | Seeds | A | `-` | same map as the row above / single seed |
| Epochs 20/40/80/120 \Pref{} | Ref. | A | `-` | ablation row: column exists only for the headline rows |
| Epochs 20/40/80/120 \Pref{} | Map err. | A | `-` | ablation row: column exists only for the headline rows |
| Epochs 20/40/80/120 \Pref{} | Seeds | A | `-` | ablation row: column exists only for the headline rows |
| Without loop closures \Ftest{} | Map err. | A | `-` | ablation row: column exists only for the headline rows |
| Without loop closures \Ftest{} | Seeds | A | `-` | ablation row: column exists only for the headline rows |
| Without correction $\Tcorr$ \Ftest{} | Map err. | A | `-` | ablation row: column exists only for the headline rows |
| Without correction $\Tcorr$ \Ftest{} | Seeds | A | `-` | ablation row: column exists only for the headline rows |
| $\Tcorr$ refitted per session \Ftwo{}$^{c}$ | Map err. | A | `-` | ablation row: column exists only for the headline rows |
| $\Tcorr$ refitted per session \Ftwo{}$^{c}$ | Seeds | A | `-` | ablation row: column exists only for the headline rows |
| No smoothing (oracle map) \Ftest{} | Map err. | A | `-` | ablation row: column exists only for the headline rows |
| No smoothing (oracle map) \Ftest{} | Seeds | A | `-` | ablation row: column exists only for the headline rows |
| 30 instead of 120 epochs$^{a}$ \Fval{} | Map err. | A | `-` | ablation row: column exists only for the headline rows |
| 30 instead of 120 epochs$^{a}$ \Fval{} | Seeds | A | `-` | ablation row: column exists only for the headline rows |
| PnP instead of Kabsch \Fval{} | Map err. | A | `-` | ablation row: column exists only for the headline rows |
| PnP instead of Kabsch \Fval{} | Seeds | A | `-` | ablation row: column exists only for the headline rows |
| With geometric augmentation \Fval{} | Map err. | A | `-` | ablation row: column exists only for the headline rows |
| With geometric augmentation \Fval{} | Seeds | A | `-` | ablation row: column exists only for the headline rows |
| Full-resolution input$^{b}$ \Fval{} | Map err. | A | `-` | ablation row: column exists only for the headline rows |
| Full-resolution input$^{b}$ \Fval{} | Seeds | A | `-` | ablation row: column exists only for the headline rows |

## Table IV (`tab:ctrl`)

| row | column | group | source | value / note |
|---|---|---|---|---|
| \Pref{} both scans in one map | Oracle | C | `runs/track-v2-5XXA-both` | no oracle network on the merged map |
| \Prearra{} \textbf{exam-view scan} | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Prearra{} generic scan | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Prearrb{} \textbf{exam-view scan} | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Prearrb{} generic scan | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Ppeople{} \textbf{exam-view scan} | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Ppeople{} generic scan | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Pempty{} \textbf{exam-view scan} | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Pempty{} generic scan | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Fnew{} (8) own generic scans | Map err. | B | `runs/map-4XXA/map_report.md (pose graph, camera position)` | 4.80 |
| \Fsmall{} (4) own generic scans | Map err. | B | `runs/map-4XXB/map_report.md (pose graph, camera position)` | 3.00 |
| \Flarge{} (4) own generic scans | Map err. | B | `runs/map-4XXC/map_report.md (pose graph, camera position)` | 3.40 |
| \Fsubj{} (6) \Flarge{}'s scans | Map err. | B | `runs/map-4XXC/map_report.md (pose graph, camera position)` | 3.40 |
| \Farm{} (4) \Flarge{}'s scans | Map err. | B | `runs/map-4XXC/map_report.md (pose graph, camera position)` | 3.40 |
| \Ftwo{} mean (26) | Map err. | B | `runs/map-4XX{A,B,C}/map_report.md` | 3.60 (mean of the 5 sets) |
| \Pref{} own, scanned after the sweeps | Cov. | B | `runs/map-5XXA-after/poses_room-503.json` | poses exist; coverage needs the coverage computation (30 mm, 10 deg) |
| \Pref{} own, scanned after the sweeps | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Prearra{} \Pref{}'s map | Map err. | A | `-` | the map's own error is in the row of the set it was made on |
| \Prearra{} \Pref{}'s map | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Prearrb{} \Pref{}'s map | Map err. | A | `-` | the map's own error is in the row of the set it was made on |
| \Prearrb{} \Pref{}'s map | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Prearrb{} \Prearra{}'s map | Map err. | A | `-` | the map's own error is in the row of the set it was made on |
| \Prearrb{} \Prearra{}'s map | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Pempty{} \Prearrb{}'s map | Map err. | A | `-` | the map's own error is in the row of the set it was made on |
| \Pempty{} \Prearrb{}'s map | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Prearra{} none | Cov. | A | `-` | same sweeps and map as the exam-view row of the set |
| \Prearra{} none | Map err. | A | `-` | same sweeps and map as the exam-view row of the set |
| \Prearra{} none | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Prearra{} 30\,\% | Cov. | A | `-` | same sweeps and map as the exam-view row of the set |
| \Prearra{} 30\,\% | Map err. | A | `-` | same sweeps and map as the exam-view row of the set |
| \Prearra{} 30\,\% | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Prearra{} 60\,\% | Cov. | A | `-` | same sweeps and map as the exam-view row of the set |
| \Prearra{} 60\,\% | Map err. | A | `-` | same sweeps and map as the exam-view row of the set |
| \Prearra{} 60\,\% | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Prearrb{} none | Cov. | A | `-` | same sweeps and map as the exam-view row of the set |
| \Prearrb{} none | Map err. | A | `-` | same sweeps and map as the exam-view row of the set |
| \Prearrb{} none | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Prearrb{} 30\,\% | Cov. | A | `-` | same sweeps and map as the exam-view row of the set |
| \Prearrb{} 30\,\% | Map err. | A | `-` | same sweeps and map as the exam-view row of the set |
| \Prearrb{} 30\,\% | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |
| \Prearrb{} 60\,\% | Cov. | A | `-` | same sweeps and map as the exam-view row of the set |
| \Prearrb{} 60\,\% | Map err. | A | `-` | same sweeps and map as the exam-view row of the set |
| \Prearrb{} 60\,\% | Oracle | C | `runs/track-v2-5XX?-*` | no oracle checkpoint for these sets or maps |

## Table V (`tab:baselines`)

| row | column | group | source | value / note |
|---|---|---|---|---|
| Odometry only | Jitter | ? | `-` | no rule: source unknown |
| Pose regression | \Fval | ? | `runs/sys-learned-2XX` | folder exists: check that it is the pose-regression system and read it |
| Pose regression | Shape | ? | `-` | no rule: source unknown |
| Pose regression | Strict | ? | `-` | no rule: source unknown |
| Pose regression | Jitter | ? | `-` | no rule: source unknown |
| Hybrid: SCR anchors + odometry | Shape | ? | `-` | no rule: source unknown |
| Hybrid: SCR anchors + odometry | Strict | ? | `-` | no rule: source unknown |
| Proposed, self-mapped | \Fval | B | `runs/track-v2map-2XX/scr_track.json` | 8.06 (2 s) |
| Proposed, self-mapped | Jitter | B | `runs/track-v2map-4XX{A..E}/scr_track.json (step_8rows, 2 s)` | 1.09 (F2, mean of the 5 sets) |
| Classical, self-made map | \Fval | C | `runs/sys-classical-trackerfree-2XX` | no run |
| Classical, self-made map | Strict | ? | `-` | no rule: source unknown |
| Classical, self-made map | Jitter | ? | `-` | no rule: source unknown |
| ORB-SLAM3, localisation only | \Fval | C | `runs/paper_final/slam-2XX* / strict sequence` | no ORB-SLAM3 run (D3: drop the cell) |
| ORB-SLAM3, localisation only | Strict | C | `runs/paper_final/slam-2XX* / strict sequence` | no ORB-SLAM3 run (D3: drop the cell) |
| ORB-SLAM3, localisation only | Jitter | B | `runs/paper_final/slam-4XX{A..E}-loc/slam_eval.json (step_8rows, 2 s)` | 0.82 (F2, mean of the 5 sets) |

Total: ? 9, A 40, B 10, C 27 (86 cells)
