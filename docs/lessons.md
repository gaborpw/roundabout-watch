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

## 2026-10-21

- **Streamlit sent Peter's email address to Streamlit on the app's first
  start.** Its first run asks in Terminal for an email "to receive helpful
  onboarding emails"; Peter typed his, and Streamlit posts any address
  typed to its own servers, even with usage statistics off (its
  `credentials.py`). The project's `.streamlit/config.toml` turned off
  usage statistics but not that prompt. Cause: only the setting the docs
  advertise was checked, not what the first run does. Guard:
  `server.showEmailPrompt = false` in `.streamlit/config.toml`, and
  `test_streamlit_config_keeps_everything_local` fails if it, the usage
  statistics, the Deploy button or the localhost address is switched back.

- **A failed video run on the app page kept the last video's result on
  screen** (caught by the automatic review on PR #14, before it merged). A
  full disk or an unreadable file raised `OSError`, which the page didn't
  catch, and no failure cleared the old result, so it read as this run's.
  Cause: the error handling listed the failures the happy-path tests
  produced, not the ones a computer does. Guard:
  `test_a_failed_run_clears_the_last_result` runs a video, then a run that
  fails with a full disk, and checks the error is shown and the old result
  is gone.

- **The camera was called "in stock" when it wasn't.** Twice (2026-10-17
  and 2026-10-21) Claude read the Reolink CX410's stock from the hidden
  product data in the page's source, which said `InStock`. The page a
  person sees showed **Notify Me**; Peter's screenshot caught it. The page
  draws its buy button with JavaScript after loading, and its source holds
  both buttons, so only the rendered page tells the truth. Cause: one
  source, and the wrong one, for something that costs money (CLAUDE.md
  12). Guard: stock is read from the button a real browser shows (headless
  Chromium, preinstalled in the cloud sessions), and `docs/parts.md` says
  so beside every stock claim.

- **Peter's first iPhone video came out sideways, and the detector missed
  most of it.** `replay` found 3 car tracks, only in the last few seconds,
  where Peter saw 2 cars. An iPhone held upright stores the picture sideways
  with a note to turn it (PyAV's `VideoFrame.rotation`, -90 here), and
  `ingest.py` ignored the note. Sideways, the cars scored 0.44–0.74, mostly
  under the 0.7 needed to start a track; upright, 0.85–0.95, and the run
  found exactly the 2 cars. Cause: the tests used videos written by our own
  helper, which never carries a rotation. Guard:
  `test_a_phone_video_filmed_upright_is_turned_upright` writes a video with
  an iPhone's -90 note and checks the frames come out upright.

## 2026-10-17

- **A merged pull request never reached `main`.** PR #9 was opened on top
  of PR #8's branch, so it could be reviewed before #8 merged. Peter merged
  #8, then #9, and #9 went into #8's old branch instead of `main`: its
  retention and chart decisions were missing from `main`. Cause: a stacked
  pull request keeps the base it was opened with; nothing retargets it when
  that base merges. The change reached `main` through PR #10, which was
  built on #9. Guard: CI fails any pull request whose base isn't `main`
  ("Pull requests merge into main", in the Lessons job), so a stacked one
  is red until it's pointed at `main`.
- **CI never ran on the first pull request.** Both `make check` jobs failed
  in seconds with "unable to find version `v10`" (PR #1). The workflow said
  `astral-sh/setup-uv@v10`, written from the releases page (v10.3.0) on the
  assumption that a floating major tag exists, as it does for
  `actions/checkout@v7`. setup-uv publishes only full versions. Guard:
  `.github/scripts/action_refs.sh` checks every `uses:` ref against GitHub
  with `git ls-remote` and runs in `make check`, so a missing tag fails
  before the push.

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
