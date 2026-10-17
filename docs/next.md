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
  pull request on his Claude subscription.

Nothing watches a camera yet.

## Waiting on Peter

Oldest first. Each stays here until it's done or Peter drops it.

1. **Order the parts** in `docs/parts.md`. The camera is a Reolink CX410
   behind the window (ADR 0005), about $798 in all. Re-check stock first;
   the Jetson at SparkFun is back-ordered.

## Next

1. Build step 1 in `docs/architecture.md`: `safety.py` (TTC, 2D-TTC, PET,
   DRAC, conflict angle), as its own pull request with hand-worked tests. It
   needs no hardware, so it can start before the parts arrive.
