# Where things stand

Read this at the start of a new session. It is the part of the conversation
with Peter that isn't anywhere else in the repo. Update it when things move.

Last updated 2026-10-17.

## Done

- **The project's starting point is on `main`** (PR #1, merged
  2026-10-17). It covers:
  - the rules, review rules, lessons and vision;
  - ADRs 0001–0008;
  - the research, the architecture and the parts list;
  - the shared types in `model.py`, with tests;
  - CI: `make check` on Python 3.10 and 3.12, plus the lessons check.
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

Nothing watches a camera yet.

## Waiting on Peter

Oldest first. Each stays here until it's done or Peter drops it.

1. **Order the parts** in `docs/parts.md`: the Reolink CX410 and the PoE
   adapter, $92.99, plus cables only if Peter's own are too short. Peter,
   2026-10-17: "ill get the camera and adapter soon".
2. **A phone video of the roundabout from the window**, about 5 minutes, for
   the first test on the Mac. Peter, 2026-10-17: "ikl do the video maybe
   tomorrow".

## Next

1. **First look** (Peter's yes, 2026-10-17): `replay` runs RF-DETR and
   ByteTrack on a video file and writes a copy with a box and a trail on
   every road user. No near-miss numbers yet; those need calibration. It
   moves `pyproject.toml` and CI to Python 3.12 (ADR 0011).
2. Build step 1b: rectangles instead of discs in `safety.py` (2D-TTC).
   Then step 2, `config.py` and `ground.py` (calibration). Neither needs
   hardware.
