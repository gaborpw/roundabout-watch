# Where things stand

Read this at the start of a new session. It is the part of the conversation
with Peter that isn't anywhere else in the repo. Update it when things move.

Last updated 2026-10-17.

## Done

- The project's rules (`CLAUDE.md`, adapted from Playthroughd), review rules
  (`REVIEW.md`), lessons, vision, and ADRs 0001–0008.
- Research: who already does this (`docs/research/references.md`), Ohio and
  Cleveland data (`docs/research/data-sources.md`), what's still unverified
  (`docs/research/verify.md`).
- The architecture and build order (`docs/architecture.md`) and the parts
  list (`docs/parts.md`).
- The shared types (`src/roundabout_watch/model.py`) with tests; `make check`
  passes on Python 3.10 and 3.12.

Nothing watches a camera yet.

## Waiting on Peter

Oldest first. Each stays here until it's done or Peter drops it.

1. **Create the GitHub repository** `gaborpw/roundabout-watch` (private,
   empty) and give Claude access to it, so this first commit can be pushed
   and go through a pull request like everything else.
2. **Which roundabout, and where the camera mounts.** Peter's own building,
   someone else's (with their permission), or a city pole (needs the City
   of Cleveland's permission). Also the rough distance from the mount to the
   middle of the roundabout: the recommended lens frames it from about
   30–60 m (ADR 0005).
3. **Camera choice** (ADR 0005): the EmpireTech/Dahua at $261, on the FCC
   Covered List; or the Hanwha at $1,040, not on it.
4. **Yes or no on the proposed ADRs**:
   - 0003, Python on a Jetson with JetPack 7.2.1;
   - 0004, RF-DETR and ByteTrack;
   - 0006, privacy and retention, including the 72 h / 30 day numbers;
   - 0007, go2rtc and PyAV;
   - 0008, SQLite.
5. **What the results are for**: personal interest, evidence for the city
   (Vision Zero), or public. This decides how much review, privacy and legal
   work the results need (`docs/vision.md`).
6. **Order the parts** (`docs/parts.md`), once 2 and 3 are settled. Re-check
   stock: several items said "only a few left" on 2026-10-17.

## Next

Once Peter says yes to the shape: build step 1 in `docs/architecture.md`,
`safety.py` (TTC, 2D-TTC, PET, DRAC, conflict angle), as its own pull
request with hand-worked tests. It needs no hardware, so it can start
before the parts arrive.
