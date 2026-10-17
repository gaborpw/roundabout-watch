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

1. **Turn on the automatic review** (ADR 0009, Peter chose Anthropic,
   2026-10-17). It needs an Anthropic API key, created at
   console.anthropic.com, preferably in its own workspace with a monthly
   spend limit. It goes in the repository's Actions secrets as
   `OCR_LLM_AUTH_TOKEN`, with `OCR_LLM_URL`. `OCR_LLM_MODEL` and
   `OCR_LLM_PROTOCOL` go in its variables. Until then the review job
   passes without reviewing. The exact steps are in the chat of
   2026-10-17. Never put the key in chat or the repo.
2. **Order the parts** once the camera pull request is merged. Re-check
   stock first.

## Next

1. The camera for the window, ADR 0005 and the parts list. Peter said yes
   on 2026-10-17. The window is on the second floor, 30–40 feet (about
   9–12 m) from the circle.
2. Build step 1 in `docs/architecture.md`: `safety.py` (TTC, 2D-TTC, PET,
   DRAC, conflict angle), as its own pull request with hand-worked tests. It
   needs no hardware, so it can start before the parts arrive.
