# Where things stand

Read this at the start of a new session. It is the part of the conversation
with Peter that isn't anywhere else in the repo. Update it when things move.

Last updated 2026-10-21.

## Done

- **The project's starting point is on `main`** (PR #1, merged
  2026-10-17). It covers:
  - the rules, review rules, lessons and vision;
  - ADRs 0001–0008;
  - the research, the architecture and the parts list;
  - the shared types in `model.py`, with tests;
  - CI: `make check` on Python 3.12 (3.10 until the first look; ADR 0011),
    plus the lessons check.
- **Peter's answers (2026-10-17, `docs/vision.md`):**
  - the roundabout is the new mini-roundabout at West 45th and Bridge
    Avenue;
  - the camera looks out through one of Peter's windows;
  - a camera around $100;
  - the results are for personal interest;
  - yes to ADRs 0003, 0004, 0006, 0007 and 0008, now accepted;
  - the window is on the second floor, 30–40 feet (about 9–12 m) from
    the circle, so the camera is a Reolink CX410 (ADR 0005, accepted).
- **Automatic review is on** (ADR 0010). Peter added
  `CLAUDE_CODE_OAUTH_TOKEN` on 2026-10-17, so OpenCodeReview reviews each
  pull request on Peter's Claude subscription.
- **The near-miss maths exists** (PR #7, build step 1): `safety.py`, with
  road users as discs.
- **Peter's desktop runs it, at home** (ADR 0011, 2026-10-17). No Jetson,
  no cloud: the RTX 3080 Ti desktop near the window runs everything, the
  camera is cabled straight to it, and the M4 Air is for testing.
- **What's kept, and the charts** (ADR 0006 and 0012, 2026-10-17): a day
  of recording, deleted once processed; every road user's path for 90 days
  and a summary of each until deleted; review and charts in Streamlit. The
  desktop has two 12 TB drives.
- **The first look works on Peter's own video** (2026-10-21): an iPhone
  clip of the roundabout at night, through the window. Once phone videos
  were turned upright (PR #12), it found and followed the 2 cars Peter saw.
- **The "Try a video" app** (ADR 0012, 2026-10-21): drop in a video on the
  Mac, get it back marked up with statistics (README).
- **Retention confirmed** (Peter, 2026-10-21: "sure this works"): 30 days
  for clips not confirmed, 90 days for full paths (ADR 0006).
- **The desktop can use its 3080 Ti** (2026-10-21): Windows installs
  PyTorch's CUDA build. Not yet run on the desktop; Peter is testing on
  the Mac for now.

Nothing watches a camera yet.

## Waiting on Peter

Oldest first. Each stays here until it's done or Peter drops it.

1. **Pick and order the camera**, then the PoE adapter ($8.00). The CX410
   is out of stock (2026-10-21); the in-stock match is the CX810 at
   $110.49, or Peter waits for the CX410 (`docs/parts.md`). Peter,
   2026-10-17: "ill get the camera and adapter soon".

## Next

1. **Calibration**, in three pull requests (Peter's yes, 2026-10-21).
   Pixels become metres, so speeds and near-misses can be measured. A
   phone video can be calibrated from points read off a satellite map;
   the camera gets its own once it's mounted.
   1. The maths, `ground.py` (this pull request).
   2. A "Calibrate" page in the app: click the points on a frame and paste
      their map positions, to write `calibration.yaml`.
   3. Speeds in "Try a video".
2. Build step 1b: rectangles instead of discs in `safety.py` (2D-TTC).
   Needs no hardware.
