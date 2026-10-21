# Changelog

Every change that reaches `main`, newest first, in one or two plain lines
each. CLAUDE.md rule 47: a code change adds its line here in the same commit.
Dates are when the change landed.

## Unreleased

- **The app no longer asks for an email on its first start** (found on
  Peter's Mac, 2026-10-21). Streamlit sends any address typed there to its
  own servers. A test now checks every setting that keeps the app local.
  Also drops a deprecated chart setting and ignores Streamlit's agent
  "skills" symlinks.

- **An app to try videos, with statistics** (Peter's ask, 2026-10-21; ADR
  0012). `streamlit run src/roundabout_watch/app.py` opens a page on the
  Mac: drop in a video of any length, and get it back marked up, with
  counts by kind, arrivals over time, time in view and a timeline. It runs
  on that computer only, with Streamlit's usage statistics and Deploy
  button off. A video that fails to run says why, even for a full disk or
  a file it can't read, and doesn't leave the previous result on screen.

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
