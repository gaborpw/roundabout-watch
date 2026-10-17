# 2. A flagged event is a candidate, not a fact

- **Status:** accepted
- **Date:** 2026-10-17

## Context

The software watches for two things: near-misses (two road users came close
to colliding) and crashes. Both are judged from a camera's view through a
detector and a tracker, each of which makes mistakes: a box jumps, two
tracks swap ids, a bus hides a car, headlights at night confuse the
detector. Research systems doing exactly this report detection and tracking
accuracies in the 90s, not 100 (for example the FHWA-funded Glassboro, NJ
study reported 95–98% for trajectories, via search result), and no
standardised specification for video near-miss systems exists yet (NCDOT,
via search result, 2026-10-17).

Fully automatic crash detection from a fixed camera is less mature still: we
found no maintained open-source system that does it (research, 2026-10-17).

## Decision

- Every event the software raises is a **candidate**, stored with status
  `flagged`.
- A person watches its clip and sets it to `confirmed` (with a type: near-miss
  or crash) or `dismissed` (with a reason, which is how thresholds get tuned).
- Anything shown or shared says which it is. Counts of near-misses or crashes
  use confirmed events only. Alerts say "possible crash", never "crash".
- Thresholds are tuned against confirmed and dismissed events, and each
  change is recorded with the counts that justified it.

## Consequences

- Someone has to watch clips. The design keeps that cheap: short clips, a
  review page, and thresholds that get tighter as dismissals teach them.
- Numbers from this project can be trusted by the city or anyone else,
  because each one is a reviewed clip, not a model's guess.
- A fully automatic crash alert (for example to emergency services) is out of
  scope. Changing that is a conversation with Peter and a new ADR.

## Sources (read 2026-10-17)

- US DOT, "A Real-time Proactive Intersection Safety Monitoring System Based
  on Video Data": https://rosap.ntl.bts.gov/view/dot/65763 (via search
  result).
- NCDOT project page on video conflict analysis, cited in research notes
  (via search result).
- Research summary of existing crash-detection code and datasets:
  `docs/research/references.md`.
