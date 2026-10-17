# Architecture

How Roundabout Watch fits together, and the order it gets built in. The
reasons behind each choice are in `docs/adr/`; what to buy is in
`docs/parts.md`. Researched 2026-10-17 (sources at the end). Keep this true
when anything changes (CLAUDE.md 50).

## The whole thing in one picture

```
 Camera (PoE, RTSP, H.264)          ── its own network, no internet (CLAUDE.md 22)
   │  one RTSP connection
   ▼
 go2rtc  (restreamer: the only thing that talks to the camera)
   ├──► recorder: ffmpeg copies the stream into 5-minute files, no re-encode
   │      └─ sweeper deletes files older than the retention window (ADR 0006)
   │
   └──► roundabout-watch  (one Python process)
          ingest   PyAV reads the stream; keeps the last ~30 s of compressed
                   packets in memory; decodes frames
          detect   RF-DETR (TensorRT FP16 on the Jetson)      → Detection, pixels
          track    ByteTrack (trackers package)                → tracks, pixels
          ground   homography from calibration.yaml            → Track, metres
          measure  TTC / 2D-TTC, PET, DRAC  (pure maths)       → numbers
          flag     thresholds from config.yaml                 → Event (flagged)
          clip     cut ±N s from the packet buffer, no re-encode → clips/
          store    SQLite: events, measures, review status
   │
   ▼
 review page (local)   a person watches each clip: confirm or dismiss (ADR 0002)
   │
   ▼
 enrich (later)        OHGO incidents near the roundabout, shown alongside
```

## Modules

All in `src/roundabout_watch/`. Each stage takes and returns the types in
`model.py` and nothing else (CLAUDE.md 29). Today only `model.py` exists;
the rest arrive one pull request at a time, in the order under "Build order".

| Module | Job | Runs in CI? |
|---|---|---|
| `model.py` | The shared types: Detection (pixels), TrackPoint and Track (metres), Event and its status. **Exists.** | yes |
| `config.py` | Reads `config.yaml` (thresholds, retention, camera name) and `.env` (secrets), validates both at load (CLAUDE.md 17). | yes |
| `safety.py` | Pure maths: TTC and 2D-TTC, PET, DRAC, and the conflict angle (rear-end below 30°, crossing above 85°, as in FHWA's SSAM). No camera, no GPU, no files (CLAUDE.md 30). | yes |
| `ground.py` | Turns pixels into metres. Fits a homography from at least four surveyed points in `calibration.yaml` (OpenCV `findHomography`), reports the reprojection error, and **refuses to run uncalibrated**. Projects each detection's ground-contact point (bottom-middle of its box). | yes |
| `flag.py` | Decides what is worth a look. Near-miss: a pair whose TTC or PET falls under the configured threshold. Possible crash: two tracks overlapping on the ground, then both stopping for more than N seconds (a heuristic; ADR 0002 says a person decides). | yes |
| `store.py` | SQLite through the standard library's `sqlite3`, parameterised queries only (CLAUDE.md 18). Events, their measures, review status and the reviewer's reason. | yes |
| `ingest.py` | PyAV reads go2rtc's stream (or a video file, for `replay`). Keeps a ring buffer of compressed packets so clips can start before the event. Reconnects with back-off. Strips URLs from error text before logging (CLAUDE.md 16). | file path only |
| `detect.py` | A `Detector` protocol, with one implementation: RF-DETR via TensorRT on the Jetson, or via PyTorch on a laptop for `replay`. Maps the detector's classes to `RoadUser`. | no (needs model weights) |
| `track.py` | ByteTrack from `trackers`; OC-SORT is the fallback if occlusion behind buses breaks tracks. | yes (on hand-built detections) |
| `clips.py` | Writes the packet buffer around an event to an MP4 without re-encoding; the Orin Nano has no hardware video encoder (NVIDIA's multimedia guide lists its encoding as software only). | yes (on a fixture clip) |
| `review/` | A small local web page: list of flagged events, play the clip, confirm or dismiss with a reason. | partly |
| `enrich.py` | Optional: OHGO incidents near the roundabout, shown next to our events. | yes (on saved JSON) |
| `__main__.py` | `python -m roundabout_watch run` (live), `replay <video>` (a recorded file, on any machine), `calibrate` (helps fill `calibration.yaml`). | — |

**`replay` is how the code gets developed.** Most of the work happens on
the Mac or the Windows PC against a recorded clip, on the CPU, slowly. The
Jetson is needed only for live speed.

## Thresholds (starting points, to be tuned)

| Measure | Start | Source |
|---|---|---|
| TTC | ≤ 1.5 s is a conflict; ≤ 1.0 and ≤ 0.5 s are more severe bands | FHWA SSAM default and its manual's severity bands |
| PET | ≤ 5.0 s is SSAM's default; research on intersections often uses tighter values, so tune down from here | FHWA report 10-038 |
| DRAC | 3.35 m/s² | Archer (2005), via secondary sources only: verify (`docs/research/verify.md`) |

Every change to a threshold is recorded with the confirmed and dismissed
counts that justified it (ADR 0002).

## Retention

Proposed in ADR 0006, waiting on Peter's yes:

- Continuous recording: kept 72 hours, then deleted by the sweeper.
- Clips of flagged and dismissed events: kept 30 days.
- Clips of confirmed events: kept until Peter deletes them.

A 4 MP H.264 stream at roughly 4–6 Mbit/s is about 45–65 GB a day (general
knowledge estimate, to be measured on the real camera), so 72 hours fits on
the 1 TB SSD with room for clips.

## Where it runs

- **The Jetson** (NVIDIA Jetson Orin Nano Super, `docs/parts.md`) next to
  the camera, indoors: go2rtc, the recorder and `roundabout-watch`, each as a
  systemd service so they restart on failure and after a power cut.
- **JetPack 7.2.1** (Ubuntu 24.04, Python 3.12, CUDA 13.2, TensorRT 10.16),
  which NVIDIA's quick-start guide installs today. The code stays
  compatible with Python 3.10 so JetPack 6.2.x (Python 3.10, CUDA 12.6,
  TensorRT 10.3) is a fallback (ADR 0003).
- **On the Jetson, PyTorch and ONNX Runtime come from NVIDIA's Jetson AI Lab
  index**, not PyPI, and TensorRT comes with JetPack.

## Licences (CLAUDE.md 25)

| Piece | Licence | Note |
|---|---|---|
| RF-DETR Nano / Small / Medium / Large | Apache-2.0 | Atto to Pico, XL and 2XL are under PML 1.0: don't use those sizes. |
| `trackers` (ByteTrack, OC-SORT) | Apache-2.0 | Depends on `opencv-python`, which clashes with `opencv-python-headless`; install only one. |
| supervision | MIT | Drawing and zones only; its ByteTrack was removed in 0.31.0 (2026-10-16). |
| go2rtc | MIT | |
| PyAV | BSD | Its aarch64 wheel bundles libx264 and libx265, which are GPL (general knowledge): check before shipping a device image to anyone. |
| OpenCV | Apache-2.0 | The PyPI wheel has no GStreamer, so no Jetson hardware decoding through it. |
| Traffic Intelligence, 2D-TTC | MIT | Ported into `safety.py` with attribution, not depended on. |
| **Avoided:** Ultralytics YOLO | AGPL-3.0 | Trained models are AGPL too; using it as a service means open-sourcing everything or a paid licence. |
| **Avoided:** BoxMOT | AGPL-3.0 | |
| **Avoided for now:** NVIDIA DeepStream | NVIDIA EULA | Python bindings deprecated from 9.0 (no more wheel files). |

**Patent:** US 10,522,040 B2 (Kennesaw State) covers real-time conflict
detection from video and is listed as active until 2037. Personal,
non-commercial use is unlikely to matter, but before this is ever sold or
offered as a service, a patent attorney reviews it (CLAUDE.md 46).

## Build order

One pull request each, each with its tests, each after Peter's yes
(CLAUDE.md 1, 2). The order puts the pure, checkable parts first.

1. `safety.py`: TTC, 2D-TTC, PET, DRAC and conflict angle, tested against
   hand-worked scenarios and checked against the 2D-TTC repo's results.
2. `config.py` and `ground.py`: calibration file, homography, reprojection
   error, the `calibrate` helper.
3. `track.py` + `flag.py` + `store.py`: from detections to flagged events in
   SQLite, tested with hand-built detections.
4. `ingest.py` (file mode) + `detect.py` + `replay`: the whole pipeline on a
   recorded clip on a laptop. First real numbers.
5. Test against ROCO's sample week (`docs/research/references.md`), once its
   licence is checked.
6. Live: go2rtc, the recorder and sweeper (retention must exist before
   continuous recording does), `ingest.py` live mode, `clips.py`, systemd
   units. On the Jetson, with TensorRT.
7. `review/`: the review page.
8. `enrich.py`: OHGO incidents.

## Sources (read 2026-10-17)

- RF-DETR model sizes, licences, accuracy and latency:
  https://github.com/roboflow/rf-detr ; export to ONNX and TensorRT:
  https://rfdetr.roboflow.com (via search result); Orin NX timing:
  https://roboflow.com/blog/rf-detr-nvidia-deepstream
- Ultralytics licence: https://www.ultralytics.com/license ;
  https://github.com/ultralytics/ultralytics
- `trackers`: https://pypi.org/project/trackers ; supervision 0.31.0
  release notes: https://github.com/roboflow/supervision/releases ; BoxMOT:
  https://github.com/mikel-brostrom/boxmot
- Jetson multimedia (nvv4l2decoder, Orin Nano encoding):
  https://docs.nvidia.com/jetson/archives/r36.4.3/DeveloperGuide/SD/Multimedia/AcceleratedGstreamer.html
- Jetson Orin Nano quick start (installs JetPack 7.2.1):
  https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/quick_start.html ;
  JetPack 6.2.3: https://developer.nvidia.com/embedded/jetpack-sdk-623 ;
  JetPack 7.2.1: https://developer.nvidia.com/embedded/jetpack/downloads/archive-7.2.1 ;
  Ubuntu 22.04 Python: https://packages.ubuntu.com/jammy/python3
- DeepStream Python bindings: https://github.com/NVIDIA-AI-IOT/deepstream_python_apps
- go2rtc: https://github.com/AlexxIT/go2rtc
- SSAM TTC default and conflict angles:
  https://www.fhwa.dot.gov/publications/research/safety/08051/02.cfm ;
  TTC and PET defaults: https://www.fhwa.dot.gov/publications/research/safety/10038/003.cfm ;
  severity bands: https://www.fhwa.dot.gov/publications/research/safety/08050/08050.pdf
- DRAC 3.35 m/s²: https://arxiv.org/pdf/2010.10262 (via search result)
- Review of video conflict analysis: Abdel-Aty et al. 2023,
  https://arxiv.org/abs/2303.15231 ; Jackson et al. 2013, TRR 2365,
  doi 10.3141/2365-12 (via search result)
- Patent: https://patents.google.com/patent/US10522040B2/en
