set -e

# slam-3XX-loc-r2: old smooth=1.0, old out=runs/slam-3XX-loc-r2
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_3XX --scan-runs room-301 room-302 --seq runs/slam-3XX/seq --traj runs/slam-3XX-loc-r2/online.txt --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-3XX-loc-r2

# slam-3XX-loc-r3: old smooth=1.0, old out=runs/slam-3XX-loc-r3
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_3XX --scan-runs room-301 room-302 --seq runs/slam-3XX/seq --traj runs/slam-3XX-loc-r3/online.txt --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-3XX-loc-r3

# slam-3XX-loc: old smooth=1.0, old out=runs/slam-3XX-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_3XX --scan-runs room-301 room-302 --seq runs/slam-3XX/seq --traj runs/slam-3XX-loc/online.txt --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-3XX-loc

# slam-3XX-online: old smooth=1.0, old out=runs/slam-3XX-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_3XX --scan-runs room-301 room-302 --seq runs/slam-3XX/seq --traj runs/slam-3XX-online/online.txt --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-3XX-online

# slam-3XX-reloc: old smooth=1.0, old out=runs/slam-3XX-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_3XX --scan-runs room-301 room-302 --seq runs/slam-3XX/seq --traj runs/slam-3XX-reloc/online.txt --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-3XX-reloc

# slam-3XX: old smooth=1.0, old out=runs/slam-3XX
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_3XX --scan-runs room-301 room-302 --seq runs/slam-3XX/seq --traj runs/slam-3XX/CameraTrajectory.txt --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-3XX

# slam-4XXA-loc-r2: old smooth=1.0, old out=runs/slam-4XXA-loc-r2
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-401 room-402 --runs run-401 run-402 run-403 run-404 run-405 run-406 run-407 run-408 --seq runs/slam-4XXA/seq --traj runs/slam-4XXA-loc-r2/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXA-loc-r2

# slam-4XXA-loc-r3: old smooth=1.0, old out=runs/slam-4XXA-loc-r3
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-401 room-402 --runs run-401 run-402 run-403 run-404 run-405 run-406 run-407 run-408 --seq runs/slam-4XXA/seq --traj runs/slam-4XXA-loc-r3/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXA-loc-r3

# slam-4XXA-loc: old smooth=1.0, old out=runs/slam-4XXA-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-401 room-402 --runs run-401 run-402 run-403 run-404 run-405 run-406 run-407 run-408 --seq runs/slam-4XXA/seq --traj runs/slam-4XXA-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXA-loc

# slam-4XXA-online: old smooth=1.0, old out=runs/slam-4XXA-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-401 room-402 --runs run-401 run-402 run-403 run-404 run-405 run-406 run-407 run-408 --seq runs/slam-4XXA/seq --traj runs/slam-4XXA-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXA-online

# slam-4XXA-reloc: old smooth=1.0, old out=runs/slam-4XXA-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-401 room-402 --runs run-401 run-402 run-403 run-404 run-405 run-406 run-407 run-408 --seq runs/slam-4XXA/seq --traj runs/slam-4XXA-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXA-reloc

# slam-4XXA: old smooth=1.0, old out=runs/slam-4XXA
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-401 room-402 --runs run-401 run-402 run-403 run-404 run-405 run-406 run-407 run-408 --seq runs/slam-4XXA/seq --traj runs/slam-4XXA/CameraTrajectory.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXA

# slam-4XXB-loc-r2: old smooth=1.0, old out=runs/slam-4XXB-loc-r2
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-403 room-404 --runs run-409 run-410 run-411 run-412 --seq runs/slam-4XXB/seq --traj runs/slam-4XXB-loc-r2/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXB-loc-r2

# slam-4XXB-loc-r3: old smooth=1.0, old out=runs/slam-4XXB-loc-r3
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-403 room-404 --runs run-409 run-410 run-411 run-412 --seq runs/slam-4XXB/seq --traj runs/slam-4XXB-loc-r3/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXB-loc-r3

# slam-4XXB-loc: old smooth=1.0, old out=runs/slam-4XXB-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-403 room-404 --runs run-409 run-410 run-411 run-412 --seq runs/slam-4XXB/seq --traj runs/slam-4XXB-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXB-loc

# slam-4XXB-online: old smooth=1.0, old out=runs/slam-4XXB-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-403 room-404 --runs run-409 run-410 run-411 run-412 --seq runs/slam-4XXB/seq --traj runs/slam-4XXB-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXB-online

# slam-4XXB-reloc: old smooth=1.0, old out=runs/slam-4XXB-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-403 room-404 --runs run-409 run-410 run-411 run-412 --seq runs/slam-4XXB/seq --traj runs/slam-4XXB-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXB-reloc

# slam-4XXB: old smooth=1.0, old out=runs/slam-4XXB
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-403 room-404 --runs run-409 run-410 run-411 run-412 --seq runs/slam-4XXB/seq --traj runs/slam-4XXB/CameraTrajectory.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXB

# slam-4XXC-loc-r2: old smooth=1.0, old out=runs/slam-4XXC-loc-r2
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-413 run-414 run-415 run-416 --seq runs/slam-4XXC/seq --traj runs/slam-4XXC-loc-r2/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXC-loc-r2

# slam-4XXC-loc-r3: old smooth=1.0, old out=runs/slam-4XXC-loc-r3
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-413 run-414 run-415 run-416 --seq runs/slam-4XXC/seq --traj runs/slam-4XXC-loc-r3/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXC-loc-r3

# slam-4XXC-loc: old smooth=1.0, old out=runs/slam-4XXC-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-413 run-414 run-415 run-416 --seq runs/slam-4XXC/seq --traj runs/slam-4XXC-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXC-loc

# slam-4XXC-online: old smooth=1.0, old out=runs/slam-4XXC-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-413 run-414 run-415 run-416 --seq runs/slam-4XXC/seq --traj runs/slam-4XXC-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXC-online

# slam-4XXC-reloc: old smooth=1.0, old out=runs/slam-4XXC-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-413 run-414 run-415 run-416 --seq runs/slam-4XXC/seq --traj runs/slam-4XXC-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXC-reloc

# slam-4XXC: old smooth=1.0, old out=runs/slam-4XXC
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-413 run-414 run-415 run-416 --seq runs/slam-4XXC/seq --traj runs/slam-4XXC/CameraTrajectory.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXC

# slam-4XXD-loc-r2: old smooth=1.0, old out=runs/slam-4XXD-loc-r2
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-418 run-419 run-420 run-421 run-423 run-424 --seq runs/slam-4XXD/seq --traj runs/slam-4XXD-loc-r2/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXD-loc-r2

# slam-4XXD-loc-r3: old smooth=1.0, old out=runs/slam-4XXD-loc-r3
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-418 run-419 run-420 run-421 run-423 run-424 --seq runs/slam-4XXD/seq --traj runs/slam-4XXD-loc-r3/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXD-loc-r3

# slam-4XXD-loc: old smooth=1.0, old out=runs/slam-4XXD-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-418 run-419 run-420 run-421 run-423 run-424 --seq runs/slam-4XXD/seq --traj runs/slam-4XXD-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXD-loc

# slam-4XXD-online: old smooth=1.0, old out=runs/slam-4XXD-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-418 run-419 run-420 run-421 run-423 run-424 --seq runs/slam-4XXD/seq --traj runs/slam-4XXD-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXD-online

# slam-4XXD-reloc: old smooth=1.0, old out=runs/slam-4XXD-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-418 run-419 run-420 run-421 run-423 run-424 --seq runs/slam-4XXD/seq --traj runs/slam-4XXD-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXD-reloc

# slam-4XXD: old smooth=1.0, old out=runs/slam-4XXD
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-418 run-419 run-420 run-421 run-423 run-424 --seq runs/slam-4XXD/seq --traj runs/slam-4XXD/CameraTrajectory.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXD

# slam-4XXE-loc-r2: old smooth=1.0, old out=runs/slam-4XXE-loc-r2
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-425 run-426 run-427 run-428 --seq runs/slam-4XXE/seq --traj runs/slam-4XXE-loc-r2/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXE-loc-r2

# slam-4XXE-loc-r3: old smooth=1.0, old out=runs/slam-4XXE-loc-r3
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-425 run-426 run-427 run-428 --seq runs/slam-4XXE/seq --traj runs/slam-4XXE-loc-r3/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXE-loc-r3

# slam-4XXE-loc: old smooth=1.0, old out=runs/slam-4XXE-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-425 run-426 run-427 run-428 --seq runs/slam-4XXE/seq --traj runs/slam-4XXE-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXE-loc

# slam-4XXE-online: old smooth=1.0, old out=runs/slam-4XXE-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-425 run-426 run-427 run-428 --seq runs/slam-4XXE/seq --traj runs/slam-4XXE-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXE-online

# slam-4XXE-reloc: old smooth=1.0, old out=runs/slam-4XXE-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-425 run-426 run-427 run-428 --seq runs/slam-4XXE/seq --traj runs/slam-4XXE-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXE-reloc

# slam-4XXE: old smooth=1.0, old out=runs/slam-4XXE
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/train_4XX --scan-runs room-405 room-406 --runs run-425 run-426 run-427 run-428 --seq runs/slam-4XXE/seq --traj runs/slam-4XXE/CameraTrajectory.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-4XXE

# slam-5XXA-exam-loc-r2: old smooth=1.0, old out=runs/slam-5XXA-exam-loc-r2
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXA --scan-runs room-502 --seq runs/slam-5XXA-exam/seq --traj runs/slam-5XXA-exam-loc-r2/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXA-exam-loc-r2

# slam-5XXA-exam-loc-r3: old smooth=1.0, old out=runs/slam-5XXA-exam-loc-r3
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXA --scan-runs room-502 --seq runs/slam-5XXA-exam/seq --traj runs/slam-5XXA-exam-loc-r3/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXA-exam-loc-r3

# slam-5XXA-exam-loc: old smooth=1.0, old out=runs/slam-5XXA-exam-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXA --scan-runs room-502 --seq runs/slam-5XXA-exam/seq --traj runs/slam-5XXA-exam-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXA-exam-loc

# slam-5XXA-exam-online: old smooth=1.0, old out=runs/slam-5XXA-exam-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXA --scan-runs room-502 --seq runs/slam-5XXA-exam/seq --traj runs/slam-5XXA-exam-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXA-exam-online

# slam-5XXA-exam-reloc: old smooth=1.0, old out=runs/slam-5XXA-exam-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXA --scan-runs room-502 --seq runs/slam-5XXA-exam/seq --traj runs/slam-5XXA-exam-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXA-exam-reloc

# slam-5XXA-exam: old smooth=1.0, old out=runs/slam-5XXA-exam
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXA --scan-runs room-502 --seq runs/slam-5XXA-exam/seq --traj runs/slam-5XXA-exam/CameraTrajectory.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXA-exam

# slam-5XXA-generic-loc: old smooth=1.0, old out=runs/slam-5XXA-generic-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXA --scan-runs room-501 --seq runs/slam-5XXA-generic/seq --traj runs/slam-5XXA-generic-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXA-generic-loc

# slam-5XXA-generic-online: old smooth=1.0, old out=runs/slam-5XXA-generic-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXA --scan-runs room-501 --seq runs/slam-5XXA-generic/seq --traj runs/slam-5XXA-generic-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXA-generic-online

# slam-5XXA-generic-reloc: old smooth=1.0, old out=runs/slam-5XXA-generic-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXA --scan-runs room-501 --seq runs/slam-5XXA-generic/seq --traj runs/slam-5XXA-generic-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXA-generic-reloc

# slam-5XXB-exam-loc-r2: old smooth=1.0, old out=runs/slam-5XXB-exam-loc-r2
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXB --scan-runs room-505 --seq runs/slam-5XXB-exam/seq --traj runs/slam-5XXB-exam-loc-r2/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXB-exam-loc-r2

# slam-5XXB-exam-loc-r3: old smooth=1.0, old out=runs/slam-5XXB-exam-loc-r3
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXB --scan-runs room-505 --seq runs/slam-5XXB-exam/seq --traj runs/slam-5XXB-exam-loc-r3/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXB-exam-loc-r3

# slam-5XXB-exam-loc: old smooth=1.0, old out=runs/slam-5XXB-exam-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXB --scan-runs room-505 --seq runs/slam-5XXB-exam/seq --traj runs/slam-5XXB-exam-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXB-exam-loc

# slam-5XXB-exam-occ30-loc: old smooth=1.0, old out=runs/slam-5XXB-exam-occ30-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXB --scan-runs room-505 --seq runs/slam-5XXB-exam-occ30/seq --traj runs/slam-5XXB-exam-occ30-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXB-exam-occ30-loc

# slam-5XXB-exam-occ30-online: old smooth=1.0, old out=runs/slam-5XXB-exam-occ30-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXB --scan-runs room-505 --seq runs/slam-5XXB-exam-occ30/seq --traj runs/slam-5XXB-exam-occ30-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXB-exam-occ30-online

# slam-5XXB-exam-occ30-reloc: old smooth=1.0, old out=runs/slam-5XXB-exam-occ30-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXB --scan-runs room-505 --seq runs/slam-5XXB-exam-occ30/seq --traj runs/slam-5XXB-exam-occ30-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXB-exam-occ30-reloc

# slam-5XXB-exam-occ60-loc: old smooth=1.0, old out=runs/slam-5XXB-exam-occ60-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXB --scan-runs room-505 --seq runs/slam-5XXB-exam-occ60/seq --traj runs/slam-5XXB-exam-occ60-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXB-exam-occ60-loc

# slam-5XXB-exam-occ60-online: old smooth=1.0, old out=runs/slam-5XXB-exam-occ60-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXB --scan-runs room-505 --seq runs/slam-5XXB-exam-occ60/seq --traj runs/slam-5XXB-exam-occ60-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXB-exam-occ60-online

# slam-5XXB-exam-occ60-reloc: old smooth=1.0, old out=runs/slam-5XXB-exam-occ60-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXB --scan-runs room-505 --seq runs/slam-5XXB-exam-occ60/seq --traj runs/slam-5XXB-exam-occ60-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXB-exam-occ60-reloc

# slam-5XXB-exam-online: old smooth=1.0, old out=runs/slam-5XXB-exam-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXB --scan-runs room-505 --seq runs/slam-5XXB-exam/seq --traj runs/slam-5XXB-exam-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXB-exam-online

# slam-5XXB-exam-reloc: old smooth=1.0, old out=runs/slam-5XXB-exam-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXB --scan-runs room-505 --seq runs/slam-5XXB-exam/seq --traj runs/slam-5XXB-exam-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXB-exam-reloc

# slam-5XXB-exam: old smooth=1.0, old out=runs/slam-5XXB-exam
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXB --scan-runs room-505 --seq runs/slam-5XXB-exam/seq --traj runs/slam-5XXB-exam/CameraTrajectory.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXB-exam

# slam-5XXC-exam-loc-r2: old smooth=1.0, old out=runs/slam-5XXC-exam-loc-r2
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-507 --seq runs/slam-5XXC-exam/seq --traj runs/slam-5XXC-exam-loc-r2/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-exam-loc-r2

# slam-5XXC-exam-loc-r3: old smooth=1.0, old out=runs/slam-5XXC-exam-loc-r3
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-507 --seq runs/slam-5XXC-exam/seq --traj runs/slam-5XXC-exam-loc-r3/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-exam-loc-r3

# slam-5XXC-exam-loc: old smooth=1.0, old out=runs/slam-5XXC-exam-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-507 --seq runs/slam-5XXC-exam/seq --traj runs/slam-5XXC-exam-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-exam-loc

# slam-5XXC-exam-occ30-loc: old smooth=1.0, old out=runs/slam-5XXC-exam-occ30-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-507 --seq runs/slam-5XXC-exam-occ30/seq --traj runs/slam-5XXC-exam-occ30-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-exam-occ30-loc

# slam-5XXC-exam-occ30-online: old smooth=1.0, old out=runs/slam-5XXC-exam-occ30-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-507 --seq runs/slam-5XXC-exam-occ30/seq --traj runs/slam-5XXC-exam-occ30-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-exam-occ30-online

# slam-5XXC-exam-occ30-reloc: old smooth=1.0, old out=runs/slam-5XXC-exam-occ30-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-507 --seq runs/slam-5XXC-exam-occ30/seq --traj runs/slam-5XXC-exam-occ30-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-exam-occ30-reloc

# slam-5XXC-exam-occ60-loc: old smooth=1.0, old out=runs/slam-5XXC-exam-occ60-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-507 --seq runs/slam-5XXC-exam-occ60/seq --traj runs/slam-5XXC-exam-occ60-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-exam-occ60-loc

# slam-5XXC-exam-occ60-online: old smooth=1.0, old out=runs/slam-5XXC-exam-occ60-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-507 --seq runs/slam-5XXC-exam-occ60/seq --traj runs/slam-5XXC-exam-occ60-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-exam-occ60-online

# slam-5XXC-exam-occ60-reloc: old smooth=1.0, old out=runs/slam-5XXC-exam-occ60-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-507 --seq runs/slam-5XXC-exam-occ60/seq --traj runs/slam-5XXC-exam-occ60-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-exam-occ60-reloc

# slam-5XXC-exam-online: old smooth=1.0, old out=runs/slam-5XXC-exam-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-507 --seq runs/slam-5XXC-exam/seq --traj runs/slam-5XXC-exam-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-exam-online

# slam-5XXC-exam-reloc: old smooth=1.0, old out=runs/slam-5XXC-exam-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-507 --seq runs/slam-5XXC-exam/seq --traj runs/slam-5XXC-exam-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-exam-reloc

# slam-5XXC-exam: old smooth=1.0, old out=runs/slam-5XXC-exam
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-507 --seq runs/slam-5XXC-exam/seq --traj runs/slam-5XXC-exam/CameraTrajectory.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-exam

# slam-5XXC-oldB-loc: old smooth=1.0, old out=runs/slam-5XXC-oldB-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-504 --seq runs/slam-5XXC-oldB/seq --traj runs/slam-5XXC-oldB-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-oldB-loc

# slam-5XXC-oldB-online: old smooth=1.0, old out=runs/slam-5XXC-oldB-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-504 --seq runs/slam-5XXC-oldB/seq --traj runs/slam-5XXC-oldB-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-oldB-online

# slam-5XXC-oldB-reloc: old smooth=1.0, old out=runs/slam-5XXC-oldB-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-504 --seq runs/slam-5XXC-oldB/seq --traj runs/slam-5XXC-oldB-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-oldB-reloc

# slam-5XXC-oldB: old smooth=1.0, old out=runs/slam-5XXC-oldB
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXC --scan-runs room-504 --seq runs/slam-5XXC-oldB/seq --traj runs/slam-5XXC-oldB/CameraTrajectory.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXC-oldB

# slam-5XXD-exam-loc-r2: old smooth=1.0, old out=runs/slam-5XXD-exam-loc-r2
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXD --scan-runs room-507 --seq runs/slam-5XXD-exam/seq --traj runs/slam-5XXD-exam-loc-r2/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXD-exam-loc-r2

# slam-5XXD-exam-loc-r3: old smooth=1.0, old out=runs/slam-5XXD-exam-loc-r3
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXD --scan-runs room-507 --seq runs/slam-5XXD-exam/seq --traj runs/slam-5XXD-exam-loc-r3/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXD-exam-loc-r3

# slam-5XXD-exam-loc: old smooth=1.0, old out=runs/slam-5XXD-exam-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXD --scan-runs room-507 --seq runs/slam-5XXD-exam/seq --traj runs/slam-5XXD-exam-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXD-exam-loc

# slam-5XXD-exam-online: old smooth=1.0, old out=runs/slam-5XXD-exam-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXD --scan-runs room-507 --seq runs/slam-5XXD-exam/seq --traj runs/slam-5XXD-exam-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXD-exam-online

# slam-5XXD-exam-reloc: old smooth=1.0, old out=runs/slam-5XXD-exam-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXD --scan-runs room-507 --seq runs/slam-5XXD-exam/seq --traj runs/slam-5XXD-exam-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXD-exam-reloc

# slam-5XXD-exam: old smooth=1.0, old out=runs/slam-5XXD-exam
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXD --scan-runs room-507 --seq runs/slam-5XXD-exam/seq --traj runs/slam-5XXD-exam/CameraTrajectory.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXD-exam

# slam-5XXE-exam-loc-r2: old smooth=1.0, old out=runs/slam-5XXE-exam-loc-r2
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXE --scan-runs room-509 --seq runs/slam-5XXE-exam/seq --traj runs/slam-5XXE-exam-loc-r2/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXE-exam-loc-r2

# slam-5XXE-exam-loc-r3: old smooth=1.0, old out=runs/slam-5XXE-exam-loc-r3
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXE --scan-runs room-509 --seq runs/slam-5XXE-exam/seq --traj runs/slam-5XXE-exam-loc-r3/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXE-exam-loc-r3

# slam-5XXE-exam-loc: old smooth=1.0, old out=runs/slam-5XXE-exam-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXE --scan-runs room-509 --seq runs/slam-5XXE-exam/seq --traj runs/slam-5XXE-exam-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXE-exam-loc

# slam-5XXE-exam-online: old smooth=1.0, old out=runs/slam-5XXE-exam-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXE --scan-runs room-509 --seq runs/slam-5XXE-exam/seq --traj runs/slam-5XXE-exam-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXE-exam-online

# slam-5XXE-exam-reloc: old smooth=1.0, old out=runs/slam-5XXE-exam-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXE --scan-runs room-509 --seq runs/slam-5XXE-exam/seq --traj runs/slam-5XXE-exam-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXE-exam-reloc

# slam-5XXE-exam: old smooth=1.0, old out=runs/slam-5XXE-exam
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXE --scan-runs room-509 --seq runs/slam-5XXE-exam/seq --traj runs/slam-5XXE-exam/CameraTrajectory.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXE-exam

# slam-5XXE-oldC-loc: old smooth=1.0, old out=runs/slam-5XXE-oldC-loc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXE --scan-runs room-507 --seq runs/slam-5XXE-oldC/seq --traj runs/slam-5XXE-oldC-loc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXE-oldC-loc

# slam-5XXE-oldC-online: old smooth=1.0, old out=runs/slam-5XXE-oldC-online
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXE --scan-runs room-507 --seq runs/slam-5XXE-oldC/seq --traj runs/slam-5XXE-oldC-online/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXE-oldC-online

# slam-5XXE-oldC-reloc: old smooth=1.0, old out=runs/slam-5XXE-oldC-reloc
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXE --scan-runs room-507 --seq runs/slam-5XXE-oldC/seq --traj runs/slam-5XXE-oldC-reloc/online.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXE-oldC-reloc

# slam-5XXE-oldC: old smooth=1.0, old out=runs/slam-5XXE-oldC
/data2/u0137815/conda/envs/usrgbd/bin/python tools/slam_baseline.py evaluate --root /data2/u0137815/rgbd-us/data/test_5XXE --scan-runs room-507 --seq runs/slam-5XXE-oldC/seq --traj runs/slam-5XXE-oldC/CameraTrajectory.txt --cam-calib-from runs/slam-3XX/slam_eval.json --smooth 2 --source orbslam3 --calib /data2/u0137815/US_SCR/calib_matrix.csv --hand-eye /data2/u0137815/US_SCR/T_marker_cam.npy --out runs/paper_final/slam-5XXE-oldC
