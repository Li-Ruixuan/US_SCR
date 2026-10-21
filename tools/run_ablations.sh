#!/usr/bin/env bash
# Evaluation-only runs for note §8 (training PC, repo root; no training):
#   1. the two missing cells of the fair table (RPRNet + SCR anchors; classical odometry + anchor network)
#   2. ablation B: anchor interval 0.5 / 2 / 5 s / inf (= odometry only); 1 s exists already
#   3. anchors only, no odometry (an anchor every step, --odometry-source zero)
#   4. US-image error (poses.py) for every new anchored trajectory
# Needs the existing classical-vo caches, SCR models and anchor networks (all made before).
#   nohup bash tools/run_ablations.sh > ablations.log 2>&1 &
# Only the US-image exports (step 4), e.g. after an interrupted run; already exported trajectories are skipped:
#   EXPORT_ONLY=1 nohup bash tools/run_ablations.sh > ablations_export.log 2>&1 &
set -u
EXPORT_ONLY=${EXPORT_ONLY:-0}
O12=runs/rpr-rgb-gap8-12XX-gru8                  # odometry for 3XX (1XX + 2XX)
O=runs/rpr-rgb-gap8-123XX-gru8                   # odometry for 4XX (1XX + 2XX + 3XX)
declare -A S=([A]="room-401 room-402" [B]="room-403 room-404" [C]="room-405 room-406" [D]="room-405 room-406" [E]="room-405 room-406")
declare -A SC=([A]=A [B]=B [C]=C [D]=C [E]=C)    # whose room scans (and SCR / adapted models) each block uses
BLOCKS="A B C D E"

# 3XX: sweeps of 3XX against their own room scans (as runs/anchoring-final, ...-map-room-301+room-302)
e3() { python anchoring.py evaluate --root data/train_2XX --scan-runs room-201 room-202 --pairs runs/anchor-pairs/pairs_2XX.json \
       --odometry $O12 --test-root data/train_3XX --map-root data/train_3XX --map-scans room-301 room-302 \
       --pgo --out runs/ablation-3XX "$@"; }
e4() { b=$1; shift; python anchoring.py evaluate --root data/test_4XX$b --scan-runs ${S[$b]} --pairs runs/anchor-pairs/pairs_4XX$b.json \
       --odometry $O --test-root data/test_4XX$b --pgo --out runs/ablation-4XX$b "$@"; }

if [ "$EXPORT_ONLY" != 1 ]; then
echo "=== 1a. RPRNet odometry + SCR anchors"
e3 --anchor scr --scr-ckpt runs/scr-3XX/best.pt
for b in $BLOCKS; do e4 $b --anchor scr --scr-ckpt runs/scr-4XX${SC[$b]}/best.pt; done

echo "=== 1b. classical odometry + anchor network (unadapted and adapted)"
e3 --ckpts runs/anchor-rgbd-e20/fold0/best.pt --odometry-source classical-vo-train_3XX
e3 --ckpts runs/anchor-rgbd-e20-adapt3XX/fold0/best.pt --odometry-source classical-vo-train_3XX
for b in $BLOCKS; do
  e4 $b --ckpts runs/anchor-rgbd-23XX-adapt4XX${SC[$b]}/fold0/best.pt --odometry-source classical-vo-test_4XX$b
done

echo "=== 2. anchor interval (classical anchors + classical odometry; 3XX also with RPRNet odometry)"
for iv in 0.5 2 5 inf; do
  e3 --anchor classical --odometry-source classical-vo-train_3XX --interval $iv
  e3 --anchor classical --interval $iv
  for b in $BLOCKS; do e4 $b --anchor classical --odometry-source classical-vo-test_4XX$b --interval $iv; done
done

echo "=== 3. anchors only: no odometry, a classical anchor every step"
e3 --anchor classical --odometry-source zero --interval 0.01
for b in $BLOCKS; do e4 $b --anchor classical --odometry-source zero --interval 0.01; done
fi

echo "=== 4. US-image error of the ablation trajectories (pose graph; anchors only also raw = causal); existing ones skipped"
p() { python poses.py --ckpts $1/fold0/best.pt --test-root $2 --out $3 --no-plot --source $4; }
# the trajectories these runs make: anchor intervals, anchors only, SCR anchors on RPRNet odometry, anchor network on classical odometry
ablation_sources() {   # $1 = preds folder, $2 = test name (train_3XX, test_4XXA, ...)
  for f in "$1"/anchored-pgo-*-every{0.5,2,5,inf}s-*"$2"*_fold0.npz "$1"/anchored-{pgo,causal}-*odo-zero*"$2"*_fold0.npz \
           "$1"/anchored-pgo-scr-*-odometry-"$2"*_fold0.npz "$1"/anchored-pgo-anchor-rgbd-*odo-classical-vo*"$2"*_fold0.npz; do
    [ -e "$f" ] && basename "$f" _fold0.npz
  done | sort -u
}
export_missing() {     # $1 = odometry arm, $2 = test root, $3 = output folder, $4 = test name
  for src in $(ablation_sources $1/preds $4); do
    if [ -e "$3/compound/summary_$src.json" ]; then echo "  done already: $src"; else p $1 $2 $3 $src; fi
  done
}
export_missing $O12 data/train_3XX $O12/test_3XX_ablation train_3XX
for b in $BLOCKS; do export_missing $O data/test_4XX$b $O/test_4XX$b test_4XX$b; done
echo "=== done"
