# 8. Events in SQLite on the Jetson

- **Status:** proposed (waiting on Peter's yes, `docs/next.md`)
- **Date:** 2026-10-17

## Context

The project stores flagged events, their measures, and each review decision
with its reason. One process writes them; one person reviews them; it all
lives on one box. Playthroughd uses Postgres, which Peter already knows.

## Decision

SQLite, through Python's built-in `sqlite3` module, in a file next to the
clips. Parameterised queries only (CLAUDE.md 18). The schema lives in
`store.py` with numbered migrations, like Playthroughd's.

## Consequences

- No database server to install, update, secure or back up separately:
  copying the file copies the data.
- **Trade-off:** if this ever grows to several cameras writing to one place,
  or a website reading the events, it moves to Postgres. The migrations make
  that a port, not a rewrite.

No outside sources: this rests on general knowledge of SQLite and Postgres.
