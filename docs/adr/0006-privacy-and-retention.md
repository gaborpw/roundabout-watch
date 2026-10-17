# 6. Positions, not people: privacy and retention

- **Status:** accepted (Peter's yes, 2026-10-17)
- **Date:** 2026-10-17

## Context

The camera films a public road in Cleveland. Everyone in the footage is
there without having agreed to be in a dataset. Filming a public road from
private property is generally lawful in the US, and Ohio's recording law
(Ohio Revised Code 2933.52, one-party consent) is about conversations, not
video. Being lawful isn't the same as being harmless, though. Footage of who
drove where, and when, is sensitive if it leaks or is kept for years.

The safety measures need positions, speeds and headings. They don't need
identities.

## Decision

- **No identifying people.** No face recognition, no number-plate reading,
  no matching the same person or vehicle across days (CLAUDE.md 19).
- **No audio** (CLAUDE.md 20). The camera's microphone is off in its
  settings, and the code never reads an audio track.
- **Retention:**
  - continuous recording is kept 72 hours, then deleted automatically;
  - clips of flagged and dismissed events are kept 30 days;
  - clips of confirmed events are kept until Peter deletes them.

  The sweeper that deletes old footage ships in the same pull request as
  the recorder, never after it.
- **Footage stays at home, on Peter's desktop** (ADR 0011; this said the
  Jetson before). Nothing is uploaded. Sharing a clip with anyone (the
  city, the police, online) is Peter's decision each time, after checking
  with a lawyer before the first time.
- **The camera stays on its own network**, with no route to the internet
  (CLAUDE.md 22).

## Consequences

- 72 hours means a crash Peter hears about on a Friday can still be found
  on Monday, and crashes the software missed can be counted, which is how
  its miss rate is measured.
- **Trade-off:** no long archive. Anything older than 72 hours that wasn't
  flagged is gone, and a pattern that needs months of raw video can't be
  studied.
- Peter agreed to these retention numbers on 2026-10-17. Changing them is
  Peter's call and updates this ADR.

## Sources (read 2026-10-17)

- Ohio recording law, one-party consent: https://www.rcfp.org/reporters-recording-guide/ohio/
  and https://www.dmlp.org/legal-guide/ohio/ohio-recording-law (secondary
  sources; statute text not read).
- This is research, not legal advice (CLAUDE.md 46).
