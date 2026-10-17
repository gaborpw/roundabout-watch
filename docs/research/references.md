# Who already does this: code, datasets and papers

What exists, checked 2026-10-17, so nobody redoes the search. Every page
below was opened directly unless it says "via search result". Star counts
are as of that day. Re-check anything older than about six months
(CLAUDE.md 45).

**Bottom line:** nobody has a maintained, ready-made system that watches a
fixed roundabout camera and flags near-misses and crashes. The pieces exist:
detection and tracking (supervision, the detector in ADR 0004), the safety
maths (Traffic Intelligence, 2D-TTC), and datasets to test against (ROCO).
This project is the glue, the calibration and the review loop.

## Near-miss (traffic conflict) code

| Project | What it does | Licence | Use here |
|---|---|---|---|
| [Traffic Intelligence](https://sourceforge.net/projects/traffic-intelligence/) (Nicolas Saunier) | Tracks road users (YOLO or its own tracker), maps pixels to the ground (`compute-homography.py`), computes TTC, PET, predicted PET and collision probability per pair ([`events.py`](https://sourceforge.net/p/traffic-intelligence/code/ci/default/tree/trafficintelligence/events.py)). Python and C++, updated within the last week. | MIT | **Main reference** for the safety maths and calibration method. |
| [roboflow/supervision](https://github.com/roboflow/supervision) | Detection utilities, ByteTrack tracking, zones, perspective transform; `examples/speed_estimation`, `examples/traffic_analysis`. ~51k stars. | MIT | Tracking and drawing. Its speed example assumes a straight road. |
| [Two-Dimensional-Time-To-Collision](https://github.com/Yiru-Jiao/Two-Dimensional-Time-To-Collision) | 2D TTC, DRAC and MTTC from per-pair position, velocity, heading and size. No PET. Last commit 2025-06-10. | MIT | Reference implementation to test our TTC against. |
| [OTVision](https://github.com/OpenTrafficCam/OTVision) / [OTAnalytics](https://github.com/OpenTrafficCam/OTAnalytics) | YOLO detection, tracking, pixels to UTM; flows and counts. Active. | GPL-3.0 | Reference only (licence would spread to our code). |
| [OpenDataCam](https://github.com/opendatacam/opendatacam) | Line-crossing counts. Last commit 2023-11. | MIT | Not needed. |
| FHWA SSAM ([2008 brief](https://www.fhwa.dot.gov/publications/research/safety/08049/)) | TTC, PET, deceleration measures from simulator trajectory files. Download page returned 403. | unknown | Reference for definitions and thresholds. |

## Crash detection code

| Project | What it does | Licence | Use here |
|---|---|---|---|
| [Frigate NVR](https://github.com/blakeblackshear/frigate) | Local recording and object detection; v0.18.2 this week; ~37k stars. **No crash detection.** | MIT (name trademarked) | Reference for RTSP handling and retention; optional recorder. |
| [Nirikshan](https://github.com/VishalRMahajan/Nirikshan) | YOLO11 accident detector with alerts. Claims 99% mAP@50 (not verified, likely optimistic on new scenes). | MIT | Worth testing as a second opinion. |
| [AI City 2020 baseline](https://github.com/hieplpvip/traffic-anomaly-detection-baseline) | Finds stalled vehicles by background modelling. | none stated | The method is a sensible crash heuristic; don't copy code (no licence). |

## Datasets to test against

| Dataset | Camera | Terms | Use here |
|---|---|---|---|
| [ROCO](https://github.com/michigan-traffic-lab/ROCO) | 4 fisheye CCTV, two-lane roundabout, Ann Arbor MI; 557 conflicts, 17 crashes | README says CC BY-SA, its link says BY-NC-SA; separate dataset terms win. Check before use. | **Best match**: labelled roundabout conflicts to tune thresholds. |
| [rounD](https://levelxdata.com/round-dataset/) | Drone, 3 German roundabouts | Free non-commercial after application | Trajectories to test the maths. |
| [CADP](https://ankitshah009.github.io/accident_forecasting_traffic_camera) | CCTV, 1,416 accident clips | Non-commercial research only | Evaluating a crash detector. |
| [TUMTraf-Accid3nD](https://accident-dataset.github.io/) | Fixed highway gantry cameras | CC BY-NC-SA 4.0 | Real crashes from a fixed view. |
| [AI City 2026 Track 3](https://www.aicitychallenge.org/2026-track3/) | CCTV, 3,670 clips | Annotations CC-BY-4.0; videos per source | Current benchmark for anomalies. |
| DoTA, Car Crash Dataset | Dashcam | MIT | Wrong viewpoint; skip. |

**Licence warning:** most crash datasets are non-commercial only. If this
project ever earns money, check each before training on it (CLAUDE.md 25).

## Papers using the same method

- US DOT, real-time intersection safety monitoring from video (YOLO-v5 +
  DeepSORT, 95–98% trajectory accuracy): https://rosap.ntl.bts.gov/view/dot/65763
  (via search result).
- Multi-camera road safety with PET on NVIDIA Jetson (Chula Vista, CA):
  https://www.alphaxiv.org/abs/2511.12018 (via search result).
- ROCO paper: https://arxiv.org/abs/2303.00563.
- iMOVE / PATREC roundabout safety review with drone video analytics (50
  sites, Perth): https://imoveaustralia.com/project/roundabout-safety-review-using-drone-video-analytics/
  (via search result).
