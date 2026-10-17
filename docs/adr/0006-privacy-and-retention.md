# 6. Positions, not people: privacy and retention

- **Status:** accepted (Peter's yes, 2026-10-17). Retention changed the
  same day, at Peter's ask: a day of recording instead of 72 hours, and
  the paths kept.
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
- **Retention** (Peter, 2026-10-17: "it should collect it for a day,
  process it as its going and then if its process and it has that data it
  can delete it, i really dont wanna keep video for that long"):
  - **Continuous recording: one day.** A file is deleted once it is 24
    hours old **and** the pipeline has processed it. A file the pipeline
    missed (it was down) waits to be processed, but is deleted at 72 hours
    whatever happens, so an outage can't keep video for long.
  - Clips of flagged and dismissed events: 30 days, so there's time to
    review them.
  - Clips of confirmed events: until Peter deletes them.
  - **Paths:** each road user's path on the ground (positions and times,
    no picture) is kept in full for 90 days. A one-line summary of each
    (what it was, when, which way it came and went, its speed) is kept
    until Peter deletes it. Neither is linked to a person, or to the same
    road user on another day (CLAUDE.md 19).

  The sweeper that deletes old footage ships in the same pull request as
  the recorder, never after it.
- **Footage stays at home, on Peter's desktop** (ADR 0011; this said the
  Jetson before). Nothing is uploaded. Sharing a clip with anyone (the
  city, the police, online) is Peter's decision each time, after checking
  with a lawyer before the first time.
- **The camera stays on its own network**, with no route to the internet
  (CLAUDE.md 22).

## Consequences

- **Trade-off:** a crash Peter hears about has to be looked for within a
  day, and so does the check for crashes the software missed, which is how
  its miss rate is measured. Anything older than a day that wasn't flagged
  is gone. In exchange, very little video is ever kept.
- The paths cover most of what the charts need (ADR 0012) without keeping
  any picture. A pattern that needs months of raw video can't be studied.
- The 72-hour limit for unprocessed files was Claude's addition, not
  Peter's words: it stops an outage from quietly keeping days of video.
- Peter set these numbers on 2026-10-17. Changing them is Peter's call and
  updates this ADR.

## Sources (read 2026-10-17)

- Ohio recording law, one-party consent: https://www.rcfp.org/reporters-recording-guide/ohio/
  and https://www.dmlp.org/legal-guide/ohio/ohio-recording-law (secondary
  sources; statute text not read).
- This is research, not legal advice (CLAUDE.md 46).
