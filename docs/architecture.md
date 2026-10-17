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
          detect   RF-DETR (PyTorch on the desktop's GPU)     → Detection, pixels
          track    ByteTrack (trackers package)                → tracks, pixels
          ground   homography from calibration.yaml            → Track, metres
          measure  TTC / 2D-TTC, PET, DRAC  (pure maths)       → numbers
          flag     thresholds from config.yaml                 → Event (flagged)
          clip     cut ±N s from the packet buffer, no re-encode → clips/
          store    SQLite: events, measures, review status, paths
   │
   ▼
 review and charts     Streamlit, on the home network only (ADR 0011, 0012):
                       a person confirms or dismisses each clip (ADR 0002)
   │
   ▼
 enrich (later)        OHGO incidents near the roundabout, shown alongside
```

## Modules

All in `src/roundabout_watch/`. Each stage takes and returns the types in
`model.py` and nothing else (CLAUDE.md 29). Today `model.py` and `safety.py` exist;
the rest arrive one pull request at a time, in the order under "Build order".

| Module | Job | Runs in CI? |
|---|---|---|
| `model.py` | The shared types: Detection (pixels), TrackPoint and Track (metres), Event and its status. **Exists.** | yes |
| `config.py` | Reads `config.yaml` (thresholds, retention, camera name) and `.env` (secrets), validates both at load (CLAUDE.md 17). | yes |
| `safety.py` | Pure maths: TTC, PET, DRAC, speed difference (SSAM's DeltaS) and the conflict angle (rear-end below 30°, crossing above 85°, as in FHWA's SSAM). No camera, no GPU, no files (CLAUDE.md 30). **Exists**, with road users as discs; SSAM's rectangles (2D-TTC) are the next step. | yes |
| `ground.py` | Turns pixels into metres. Fits a homography from at least four surveyed points in `calibration.yaml` (OpenCV `findHomography`), reports the reprojection error, and **refuses to run uncalibrated**. Projects each detection's ground-contact point (bottom-middle of its box). | yes |
| `flag.py` | Decides what is worth a look. Near-miss: a pair whose TTC or PET falls under the configured threshold. Possible crash: two tracks overlapping on the ground, then both stopping for more than N seconds (a heuristic; ADR 0002 says a person decides). | yes |
| `store.py` | SQLite through the standard library's `sqlite3`, parameterised queries only (CLAUDE.md 18). Events, their measures, review status and the reviewer's reason; every road user's path and its one-line summary (ADR 0006). | yes |
| `ingest.py` | PyAV reads go2rtc's stream (or a video file, for `replay`). Keeps a ring buffer of compressed packets so clips can start before the event. Reconnects with back-off. Strips URLs from error text before logging (CLAUDE.md 16). | file path only |
| `detect.py` | A `Detector` protocol, with one implementation: RF-DETR through PyTorch, on the desktop's GPU (CUDA), the Mac's GPU (MPS) for `replay`, or the CPU. Maps the detector's classes to `RoadUser`. | no (needs model weights) |
| `track.py` | ByteTrack from `trackers`; OC-SORT is the fallback if occlusion behind buses breaks tracks. | yes (on hand-built detections) |
| `clips.py` | Writes the packet buffer around an event to an MP4 without re-encoding, so a clip costs almost no CPU and keeps the camera's quality (ADR 0007). | yes (on a fixture clip) |
| `pages/` | The Streamlit app (ADR 0012): review (play the clip, confirm or dismiss with a reason), map, when, how close, who, traffic. The numbers behind each page are plain functions. | the functions, yes |
| `enrich.py` | Optional: OHGO incidents near the roundabout, shown next to our events. | yes (on saved JSON) |
| `__main__.py` | `python -m roundabout_watch run` (live), `replay <video>` (a recorded file, on any machine), `calibrate` (helps fill `calibration.yaml`). | — |

**`replay` is how the code gets developed.** Most of the work happens on
the Mac against a recorded clip. The desktop runs it live (ADR 0011).

## Thresholds (starting points, to be tuned)

| Measure | Start | Source |
|---|---|---|
| TTC | ≤ 1.5 s is a conflict; ≤ 1.0 and ≤ 0.5 s are more severe bands | FHWA SSAM default and its manual's severity bands |
| PET | ≤ 5.0 s is SSAM's default; research on intersections often uses tighter values, so tune down from here | FHWA report 10-038 |
| DRAC | 3.35 m/s² | Archer (2005), via secondary sources only: verify (`docs/research/verify.md`) |

Every change to a threshold is recorded with the confirmed and dismissed
counts that justified it (ADR 0002).

## Retention

Set in ADR 0006 (Peter, 2026-10-17):

- Continuous recording: deleted once it is 24 hours old and processed;
  unprocessed files go at 72 hours regardless.
- Clips of flagged and dismissed events: kept 30 days.
- Clips of confirmed events: kept until Peter deletes them.
- Paths (positions and times, no picture): kept in full 90 days; a one-line
  summary of each road user until Peter deletes it.

Sizes, all estimates to measure on the real camera:

- A 4 MP H.264 stream at roughly 4–6 Mbit/s is about 45–65 GB a day
  (general knowledge).
- Paths are tens of MB a day, a few GB for 90 days: about 2,000–3,500
  vehicles a day pass on nearby Bridge Avenue (the City's counts,
  `docs/research/data-sources.md`), each seen for some seconds at up to
  25 positions a second.
- The desktop has two 12 TB hard drives (Peter, 2026-10-17), so none of
  this is tight.

## Where it runs

Decided in ADR 0011 (Peter's choice, 2026-10-17). Everything stays at home.

- **Peter's Windows desktop (RTX 3080 Ti), near the window**, runs it all
  day: go2rtc, the recorder and its sweeper, `roundabout-watch`, the
  database and the pages. RF-DETR runs through PyTorch on the GPU.
- **The camera is cabled straight to the desktop's Ethernet port** through
  the PoE adapter, with no gateway set on either end; the desktop's own
  internet is over Wi-Fi.
- **The pages are served to the home network only**: the desktop itself,
  or a phone on the home Wi-Fi. Nothing is uploaded and nothing is
  forwarded through the router.
- **The M4 MacBook Air is for building and testing**, with `replay` on
  recorded video.
- **Python 3.12 or newer**, from the first pull request that adds PyAV or
  RF-DETR (PyAV 19 needs it). How the pipeline starts by itself on Windows
  is decided at build step 6.

## Licences (CLAUDE.md 25)

| Piece | Licence | Note |
|---|---|---|
| RF-DETR Nano / Small / Medium / Large | Apache-2.0 | Atto to Pico, XL and 2XL are under PML 1.0: don't use those sizes. |
| `trackers` (ByteTrack, OC-SORT) | Apache-2.0 | Depends on `opencv-python`, which clashes with `opencv-python-headless`; install only one. |
| supervision | MIT | Drawing and zones only; its ByteTrack was removed in 0.31.0 (2026-10-16). |
| go2rtc | MIT | |
| Streamlit | Apache-2.0 | Sends usage statistics by default; `.streamlit/config.toml` turns them off (ADR 0012). |
| PyAV | BSD | Its wheels bundle libx264 and libx265, which are GPL (general knowledge): it matters only if the program is ever given to anyone. |
| OpenCV | Apache-2.0 | `findHomography` for `ground.py`. |
| Traffic Intelligence, 2D-TTC | MIT | References for `safety.py`, not dependencies. `safety.py` follows SSAM's definitions; 2D-TTC's rectangle model gets ported, with attribution, in step 1b. |
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

1. `safety.py`: TTC, PET, DRAC, speed difference and conflict angle, with
   road users as discs, tested against hand-worked scenarios. **Done.**
   1b. Rectangles instead of discs (2D-TTC), checked against the 2D-TTC
   repo's results.
2. `config.py` and `ground.py`: calibration file, homography, reprojection
   error, the `calibrate` helper.
3. `track.py` + `flag.py` + `store.py`: from detections to flagged events in
   SQLite, tested with hand-built detections.
4. `ingest.py` (file mode) + `detect.py` + `replay`: the whole pipeline on a
   recorded clip on a laptop. First real numbers.
5. Test against ROCO's sample week (`docs/research/references.md`), once its
   licence is checked.
6. Live: go2rtc, the recorder and sweeper (retention must exist before
   continuous recording does), `ingest.py` live mode, `clips.py`, and the
   pipeline starting by itself on the desktop.
7. `pages/`: review and charts in Streamlit (ADR 0012), once `replay` or
   the camera has put data in the database.
8. `enrich.py`: OHGO incidents.

## Sources (read 2026-10-17)

- RF-DETR model sizes, licences, accuracy and latency:
  https://github.com/roboflow/rf-detr ; export to ONNX and TensorRT:
  https://rfdetr.roboflow.com (via search result)
- Ultralytics licence: https://www.ultralytics.com/license ;
  https://github.com/ultralytics/ultralytics
- `trackers`: https://pypi.org/project/trackers ; supervision 0.31.0
  release notes: https://github.com/roboflow/supervision/releases ; BoxMOT:
  https://github.com/mikel-brostrom/boxmot
- Where it runs, PyAV's Python floor and the power estimate: ADR 0011.
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
