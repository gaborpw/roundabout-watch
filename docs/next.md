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
  - yes to ADRs 0003, 0004, 0006, 0007 and 0008, now accepted.

Nothing watches a camera yet.

## Waiting on Peter

Oldest first. Each stays here until it's done or Peter drops it.

1. **Yes or no on automatic reviews with OpenCodeReview**
   (alibaba/open-code-review), and which AI provider: Cloudflare Workers AI
   (cheap, the same account as Playthroughd's PR-Agent) or an Anthropic API
   key. Proposed in chat on 2026-10-17. It needs an API key that only Peter
   can add, as a GitHub Actions secret.
2. **How far the window is from the circle, and which floor.** That
   decides the lens.
3. **Which camera, around $100, behind glass.** A shortlist is being
   researched; ADR 0005 and `docs/parts.md` get revised in their own pull
   request.
4. **Order the parts** once 3 is settled. Re-check stock first.

## Next

1. The ~$100 camera for a window, and the parts list without the outdoor
   items (ADR 0005, `docs/parts.md`).
2. Build step 1 in `docs/architecture.md`: `safety.py` (TTC, 2D-TTC, PET,
   DRAC, conflict angle), as its own pull request with hand-worked tests. It
   needs no hardware, so it can start before the parts arrive.
