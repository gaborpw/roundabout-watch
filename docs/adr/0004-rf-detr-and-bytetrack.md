# 4. RF-DETR to detect, ByteTrack to track

- **Status:** accepted (Peter's yes, 2026-10-17)
- **Date:** 2026-10-17

## Context

The detector finds road users in each frame; the tracker links them across
frames. Both are the heart of the accuracy, and both come with licences that
reach the whole program. The project may stay personal, or may one day be
offered to the city or sold, so the licence has to allow either.

The best-known option, Ultralytics YOLO (YOLO26 today), is AGPL-3.0, and
Ultralytics says models trained with it are AGPL-3.0 too. Offering it as a
service means open-sourcing everything or buying their Enterprise licence.

## Decision

- **Detector: RF-DETR Small or Medium** (Roboflow, Apache-2.0). On COCO,
  Small scores 53.0 AP at 3.5 ms and Medium 54.7 AP at 4.4 ms (T4 GPU,
  TensorRT FP16, Roboflow's figures). Exported to ONNX, then built into a
  TensorRT FP16 engine on the Jetson itself. Pick between Small and Medium
  by measuring both on our own footage.
- Only the Apache-2.0 sizes (Nano, Small, Medium, Large). Atto, Femto,
  Pico, XL and 2XL are under PML 1.0 and are not used.
- **Tracker: ByteTrack** from Roboflow's `trackers` package (Apache-2.0),
  compared with OC-SORT from the same package, which recovers better after
  an object is hidden (MOT17 HOTA: ByteTrack 60.1, OC-SORT 61.9, BoT-SORT
  63.7, from the package README).
- **Distant vehicles:** raise the input resolution or slice the frame with
  supervision's InferenceSlicer if the far side of the roundabout is missed.

## Consequences

- Exporting RF-DETR needs a heavy PyTorch toolchain once; the Jetson then
  runs only the TensorRT engine.
- **Trade-off:** we give up Ultralytics' larger ecosystem and tutorials for
  a licence that never forces the code open or costs a fee.
- `trackers` depends on `opencv-python`; we must not also install
  `opencv-python-headless`, or the two collide.
- supervision 0.31.0 (2026-10-16) removed its own ByteTrack, so older
  tutorials using `sv.ByteTrack` no longer work.
- Neither choice has been measured on an Orin Nano or on this camera yet.
  Roboflow measured RF-DETR Nano at 6.0 ms on an Orin NX, a faster board.

## Sources (read 2026-10-17)

- RF-DETR: https://github.com/roboflow/rf-detr
- RF-DETR on Jetson: https://roboflow.com/blog/rf-detr-nvidia-deepstream
- Ultralytics licence: https://www.ultralytics.com/license
- trackers: https://pypi.org/project/trackers
- supervision releases: https://github.com/roboflow/supervision/releases
- BoxMOT (AGPL-3.0, avoided): https://github.com/mikel-brostrom/boxmot
