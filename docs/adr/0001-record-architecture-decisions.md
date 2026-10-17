# 1. Record architecture decisions

- **Status:** accepted
- **Date:** 2026-10-17

## Context

Roundabout Watch is being designed before it is built, and the reasoning
behind the early decisions is the valuable part. Six months from now the
question will not be *what* the threshold is — that is readable from
`config.yaml` — but *why* it is that number, which paper it came from, and
what breaks if it moves.

Copied from Playthroughd's ADR 0001, where the habit has paid for itself.

## Decision

Every decision that would be annoying to reverse gets a numbered file here,
in this format: context, decision, consequences, and sources with the date
they were read. Written before or alongside the implementation, never after.

An ADR is short. If it needs more than a page, the design is not settled
enough to write down yet.

## Consequences

- A new session can read `docs/adr/` in ten minutes and know which arguments
  have already been had.
- Superseded decisions are not deleted. They get `Status: superseded by
  ADR-000N`, because the wrong turns are often the most useful part of the
  record.
