# rgbd-us
free hand markerless US tracking

# Markerless Probe Pose Estimation from a Probe-Mounted RGB-D Camera 

## 1. Problem and claim

Freehand 3D ultrasound needs the 6-DoF pose of every B-mode frame. External optical or EM trackers are accurate but expensive, line-of-sight constrained, and tie the exam to a prepared room. US-only sensorless estimation drifts far beyond the sub-millimetre budget set by the elevational beam width.

Given `{I_t_rgb, D_t, I_t_US}`, output `T_t ∈ SE(3)` in a room-fixed frame established at the start of the exam, from a single probe-mounted RGB-D camera — no markers, no fiducial pattern, no external infrastructure. Downstream: 3D volume reconstruction, and navigation relative to previously scanned anatomy.

**The goal is not a more accurate tracking system.** Sub-millimetre freehand US tracking already exists (optical ~0.5 mm, MLRecon 0.88 mm); beating it is neither likely nor interesting. The goal is a *useful* pose estimate with nothing outside the probe. Accuracy is a threshold to clear, not the axis of competition: miss it and the result is useless, clear it and the infrastructure argument becomes available. The claim is "this works without a prepared room", and the experiments should be built to support that, not a millimetre table.
