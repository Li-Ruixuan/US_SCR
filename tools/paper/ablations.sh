#!/bin/bash
# Clean accuracy and ablation runs for the paper (training PC, GPU). Existing options only, no method change.
#
# Every ablation is the final system with ONE change, measured the same way: tracking error at the US image,
# absolute / shape, smoothing 2 s, on the two sets with covering room scans (F1-test 5 sweeps, P-ref 8 sweeps).
# Settings stay as chosen on F1-val: these runs analyse the components, they choose nothing.
#
#   1. oracle maps for P-rearr1, P-rearr2, P-people, P-empty (P-ref already has one), so that the cost of
#      self-mapping is measured on every covering set, not on two;
#   2. P-ref: no loop closures, no camera correction (F1-test has both in runs/repro/), no inlier gate;
#   3. both sets: small head, depth-edge labels kept, frozen encoder (ACE-style), geometric augmentation;
#   4. both sets, mapped again from scratch: no pose graph, joint refinement of network and poses (ACE0-style).
#
# New folders only, under runs/abl/ (rule 6); a step whose output folder exists is skipped, so the script can be
# stopped and started again. Steps run one after the other. Usage, from the repository root:
#   bash tools/paper/ablations.sh 2>&1 | tee runs/abl/ablations.log

cd "$(dirname "$0")/../.." || exit 1
mkdir -p runs/abl
D=/data2/u0137815/rgbd-us/data
CAL=runs/repro/map-3XX/map.json            # camera correction of F1-test, reused on the phantom (as in the paper)
fails=0

step() {                                     # step <output folder> <command...>
    local out=$1; shift
    if [ -e "$out" ]; then echo "SKIP $out (exists)"; return; fi
    echo "=== $(date '+%F %T') $out"
    "$@" || { echo "FAILED $out"; fails=$((fails+1)); }
}

# per set: root, scan runs, final map, final network, calibration option of scr_map.py
set_3XX()  { R=$D/train_3XX; SCANS="room-301 room-302"; MAP=runs/repro/map-3XX;  NET=runs/repro/v2map-3XX;  MAPCAL=(); S=3XX; }
set_5XXA() { R=$D/test_5XXA; SCANS="room-502";           MAP=runs/map-5XXA-exam;   NET=runs/v2map-5XXA-exam;  MAPCAL=(--cam-calib-from $CAL); S=5XXA-exam; }

train_on() {                                 # train_on <net out> <map folder> [extra train options]
    local net=$1 map=$2; shift 2
    step "$net" python scr_anchor.py train --root "$R" --scan-runs $SCANS --map "$map" \
        --label-poses $(for s in $SCANS; do echo "$map/poses_$s.json"; done) --out "$net" "$@"
}
track_on() {                                 # track_on <track out> <net folder> <map folder> [extra track options]
    local out=$1 net=$2 map=$3; shift 3
    step "$out" python scr_anchor.py track --ckpt "$net/best.pt" --test-root "$R" --every 2 \
        --cam-calib "$map/map.json" --out "$out" "$@"
}
net_ablation() {                             # net_ablation <name> [train options]: same map, network changed
    local name=$1; shift
    train_on runs/abl/v2map-$S-$name "$MAP" "$@"
    track_on runs/abl/track-v2map-$S-$name runs/abl/v2map-$S-$name "$MAP"
}
map_ablation() {                             # map_ablation <name> [scr_map options]: map changed, then train + track
    local name=$1; shift
    step runs/abl/map-$S-$name python scr_map.py --root "$R" --scan-runs $SCANS --out runs/abl/map-$S-$name "$@"
    train_on runs/abl/v2map-$S-$name runs/abl/map-$S-$name
    track_on runs/abl/track-v2map-$S-$name runs/abl/v2map-$S-$name runs/abl/map-$S-$name
}

# ---- 1. oracle maps (tracker labels) for the other phantom sets; P-people uses P-rearr2's scan, as ours -----------
for b in B:505 C:507 E:509; do
    blk=${b%%:*}; scan=room-${b##*:}
    step runs/abl/v2-5XX$blk-exam python scr_anchor.py train --root $D/test_5XX$blk --scan-runs $scan --out runs/abl/v2-5XX$blk-exam
    step runs/abl/track-v2-5XX$blk-exam python scr_anchor.py track --ckpt runs/abl/v2-5XX$blk-exam/best.pt \
        --test-root $D/test_5XX$blk --every 2 --out runs/abl/track-v2-5XX$blk-exam
done
step runs/abl/track-v2-5XXD-exam python scr_anchor.py track --ckpt runs/abl/v2-5XXC-exam/best.pt \
    --test-root $D/test_5XXD --every 2 --out runs/abl/track-v2-5XXD-exam

# ---- 2. cheap ablations: pose graph again without loops, re-alignment without correction, no inlier gate ---------
set_5XXA
map_ablation noloops --from "$MAP" --loop-k 0 "${MAPCAL[@]}"
map_ablation nocalib --from "$MAP" --realign --no-cam-calib
for set in set_3XX set_5XXA; do
    $set
    track_on runs/abl/track-v2map-$S-nogate "$NET" "$MAP" --gate 0
done

# ---- 3. network and training ablations on the same self-made map ------------------------------------------------
for set in set_5XXA set_3XX; do
    $set
    net_ablation smallhead --head small
    net_ablation depthedges --keep-depth-edges
    net_ablation frozenenc --freeze-encoder
    net_ablation geomaug --aug-scale 0.667 1.5 --aug-rot 15
done

# ---- 4. mapped again from scratch ------------------------------------------------------------------------------
for set in set_5XXA set_3XX; do
    $set
    map_ablation nograph --no-graph "${MAPCAL[@]}"
    map_ablation jointrefine --refine-steps 4000 "${MAPCAL[@]}"
done

# ---- shape error of every new track ----------------------------------------------------------------------------
python tools/us_analysis.py shape --json runs/abl/track-*/poses/*.json --out runs/abl/shape-abl.md \
    || { echo "FAILED shape"; fails=$((fails+1)); }
echo "=== done $(date '+%F %T'), failed steps: $fails"
