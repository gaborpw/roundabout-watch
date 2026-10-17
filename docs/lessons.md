# Lessons

What broke, why, and what now stops it happening again. The project's
steering record grows with every error, and every session reads it
**before** diagnosing anything, so the same mistake is never paid for twice.

How it works:

- **Read this before you start** (CLAUDE.md, top), and before diagnosing a
  failure: the answer may already be here.
- **Every `fix:` commit adds an entry** in the same commit. CI enforces it
  (`.github/scripts/lessons.sh`, the "Lessons" job).
- **An entry names its guard**: the test, check, rule or script that now
  catches it. "Be careful" is not a guard.
- **The same lesson twice means automate it.** If an entry's kind of failure
  shows up again, the fix is a check that makes it impossible.

Newest first. Format: date, what happened, cause, guard.

## Carried over from Playthroughd (2026-10-17)

These happened on Peter's other project. They are here because the same
traps exist in this one, and the guards were set up from the first commit.

- **A piped `make check` reported success while tests failed.** A pipe
  reports the last command's exit code, so `make check | tail` said green.
  Guard: CLAUDE.md rule 39, and every workflow runs bash with pipefail
  (`defaults: run: shell: bash`, checked by `.github/scripts/pipefail.sh`).
- **A `for` loop in the Makefile hid a failing folder.** A loop's exit code
  is only its last pass. Guard: this Makefile has no loops; each target is
  one command that fails on its own.
- **A secret leaked through a library's error text.** Go's net/http quoted
  the whole request URL, API key included, in its errors. Here the RTSP URL
  carries the camera password, and OpenCV and FFmpeg both print the URL they
  failed to open. Guard: CLAUDE.md rule 16; the camera is logged by its
  config name only, and the ingest module will strip URLs from error text
  before logging, with a test (to be written with that module).
