# Changelog

Every change that reaches `main`, newest first, in one or two plain lines
each. CLAUDE.md rule 47: a code change adds its line here in the same commit.
Dates are when the change landed.

## Unreleased

- **Phone videos filmed upright are turned the right way up** (found on
  Peter's first video, 2026-10-21). They were read sideways, and the
  detector missed most of what was in them; upright, it found the 2 cars
  Peter saw.

- **A first look on a video** (Peter's yes, 2026-10-17; build step 1a).
  `python -m roundabout_watch replay VIDEO` finds cars, bikes and people
  with RF-DETR, follows each with ByteTrack and writes a copy with boxes,
  numbers and trails, so the detector can be seen on the real roundabout
  before calibration. Python moves to 3.12 (ADR 0011), and CI tests 3.12
  only; RF-DETR is an optional extra CI never installs.

- **The near-miss maths exists** (Peter's go-ahead, 2026-10-17; build step
  1). `safety.py` measures time to collision, post-encroachment time, the
  braking needed to avoid a crash, the speed difference and the conflict
  type, following FHWA's SSAM definitions, with road users as discs. 33 new
  tests use hand-worked scenarios. Nothing calls it yet.
- **Automatic reviews run on Peter's Claude subscription, at no extra
  cost** (Peter's choice, 2026-10-17; ADR 0010). OpenCodeReview picks the
  files and rules and Claude Code reviews, instead of a paid API key
  (ADR 0009). Nothing runs until Peter adds the Claude token.
- **Pull requests get an automatic AI review** (Peter's ask, 2026-10-17;
  ADR 0009). Alibaba's OpenCodeReview runs on Anthropic, comments on each
  push, and does nothing until Peter adds the API key.
- **The project starts** (Peter's ask, 2026-10-17). Rules and steering files
  adapted from Playthroughd, the architecture, the parts list, the research
  so far, and the shared types every stage will pass between them
  (`model.py`), with tests. Nothing watches a camera yet.
