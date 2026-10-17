# CLAUDE.md

Guidance for Claude Code sessions working in this repository. Read on every
prompt, automatically.

**Starting a new session? Read [`docs/next.md`](docs/next.md),
[`docs/vision.md`](docs/vision.md) and [`docs/lessons.md`](docs/lessons.md)
first,** and read the lessons again before diagnosing any failure. How the
code fits together is [`docs/architecture.md`](docs/architecture.md); the
hardware is [`docs/parts.md`](docs/parts.md). They cover where things stand,
what is waiting on Peter, what comes next, and what Peter wants this to be, in
Peter's own words. Keep the work true to the vision, and ask Peter before drifting
from it.

These rules started as a copy of the ones Peter uses on Playthroughd
(github.com/gaborpw/PeterG), adapted on 2026-10-17 to a camera project. The
numbers are this repo's own.

## What this is

**Roundabout Watch**: one camera overlooking a roundabout in Cleveland, Ohio,
and a small computer next to it that tracks every vehicle, cyclist and
pedestrian, measures how close they come to each other, and saves a short
clip of every near-miss and possible crash for a person to review.

## The one idea that must not get lost

**A flagged event is a candidate, not a fact.** The software finds moments
worth a look; a person watching the clip decides what happened. Nothing is
ever reported, counted or published as "a crash" or "a near-miss" until a
person has confirmed it, and every number shown says whether it is flagged or
confirmed (ADR 0002).

Every shortcut away from this (an automatic crash count, an alert that says
"crash" instead of "possible crash", a threshold tuned until the chart looks
right) produces numbers that look authoritative and are not. If a change
seems to need it, that is a conversation with Peter, not an implementation
detail.

The second idea: **measurements are in metres and seconds on the ground,
never pixels.** A camera that has not been calibrated (`calibration.yaml`,
`docs/architecture.md`) produces no safety measures at all, rather than
wrong ones.

## Rules

Standing rules for every session here. They outrank convenience.

1. **Show the change before making it.** Propose the edit, wait for a yes.
   `.claude/settings.json` (`permissions.defaultMode: "default"`) enforces the
   before/after diff; don't route around it by piping a heredoc through Bash.
2. **One change at a time.** A refactor and a feature are two approvals, not
   one. If a task needs five files touched, say so first and get agreement on
   the shape before touching any of them.
3. **Run `make check` before saying it works.** "It should work" is not a
   report. If it was not run, say it was not run.
4. **Do what was asked.** No extra features, no drive-by renames, no
   reorganising files that were not part of the task. Notice something worth
   fixing — say so, do not fix it.
5. **Say when you are unsure.** A guess presented confidently costs more than
   a question. Flag assumptions at the point they are made, not at the end.
6. **Never invent data.** No made-up detections, trajectories, crash counts,
   API responses or thresholds presented as real. Test fixtures are
   hand-built scenarios, labelled as such, with the expected answer worked
   out in a comment.
7. **Explain the trade-off in a sentence.** Every decision costs something.
   Name it. If there is no cost, the decision was obvious and needs no
   explanation.
8. **Push back before building.** If the request conflicts with the vision or
   an ADR, say so first. Peter decides; do not quietly comply with something
   that breaks "a flagged event is a candidate".

## Certainty and honesty

These are the rules that matter most, because breaking them is invisible
until it costs something.

9. **Do not guess. Check.** Before changing a file, read it. Before calling a
   function, read its signature. Before using a library, read what is
   actually installed (`pyproject.toml`, `uv.lock`) — not what you remember
   the API being. Computer-vision libraries change their APIs often; memory
   of a version is not knowledge of it.
10. **Say exactly what was verified and what was not.** "Tests pass" means
    `make check` was run and exited zero. "Should work" means it was not run
    — say that, in those words. Code that needs the camera or the GPU and was
    only run on a laptop says so.
11. **Never overstate a source.** If something came from a web search summary
    rather than the page itself, say so. If a page could not be reached, say
    it could not be reached rather than answering from memory and hoping.
12. **Cross-check anything expensive to get wrong.** Prices, licences,
    recording law, safety thresholds, anything that could hurt someone or
    cost money: one source is not enough. Two, or an explicit "this needs
    confirming before you rely on it."
13. **Report failures as failures.** A command that errored, a test that did
    not run, a step that was skipped — say it in the first sentence.
14. **Correct yourself immediately and plainly.** If something said earlier
    was wrong, say so in one sentence and move on.

## Security and privacy

The camera films a public road. The people in it never agreed to be in a
dataset, so privacy is part of security here.

15. **Secrets never enter the repo.** The camera's password, the RTSP
    address (it carries the password), the OHGO API key and anything else
    live in `.env` on the machine that runs the code, which is git-ignored.
    Not in code, config, a commit message, a comment or a test fixture.
16. **Never print a secret.** Not in logs, not in an error message, not in
    chat. An RTSP URL is a secret: `rtsp://user:password@…`. Log the camera
    by its name in config, never by its URL, and strip URLs from library
    error text before logging it (PeterG lesson: Go's net/http quoted whole
    URLs, key included, in its errors).
17. **Validate at the boundary.** Frames from the camera, JSON from OHGO,
    `config.yaml`, `calibration.yaml`: untrusted shape until parsed. Parse,
    do not assume. A frame can be missing, late, the wrong size or black.
18. **Parameterise every query.** No string-built SQL, ever, including in
    scripts and migrations.
19. **No identifying people.** No face recognition, no number-plate
    reading, no re-identifying the same person or car across days. The
    system needs positions and speeds, not identities (ADR 0006).
20. **No audio.** The camera's microphone is off in its settings, and the
    code never reads an audio track. Ohio's recording law is about
    conversations; we have no reason to go near it.
21. **Footage is deleted on a schedule.** Continuous recording is kept for a
    short, fixed window, and only clips around flagged events are kept
    longer (`docs/architecture.md`, "Retention"). A change to what is kept or
    for how long is Peter's decision and is written down first.
22. **The camera never talks to the internet.** It sits on its own network
    with only the computer next to it. Its cloud, P2P and UPnP features are
    off, and its default password is changed on day one.
23. **Least privilege on keys.** An API key does one job. Ask why a scope is
    needed before adding it.
24. **Do not add a dependency without saying why.** Every package is code
    running with your privileges. Name what it does, what it replaces, its
    licence, and whether a few lines of our own would do instead.
25. **Licences are checked before code depends on them.** Some popular
    detectors are AGPL-3.0, which reaches the whole program if it is ever
    offered to others. Record the licence of every model and library in
    `docs/architecture.md`, and prefer permissive ones (ADR 0004).

## Code practices

26. **Match the file you are in.** Its naming, its comment density, its
    idioms. Consistency across the codebase beats your preference.
27. **Comment the why, never the what.** `# increment i` is noise. `# PET
    needs both tracks to pass the same cell, so a track that left the frame
    early can't produce one` is the reason someone keeps the line.
28. **One source of truth per concept.** Thresholds live in `config.yaml`
    and are read through `config.py`. Ground calibration lives in
    `calibration.yaml`. The shapes that pass between stages live in
    `model.py`. If you need a second place, that is a design problem.
29. **Stages talk through `model.py`, not each other's internals.** Ingest,
    detect, track, project, measure, flag, clip and review are separate
    modules (`docs/architecture.md`), so each can be tested on its own and
    swapped (a new detector should not touch the safety maths).
30. **The maths is pure.** Safety measures take trajectories and return
    numbers: no camera, no GPU, no files. That is what makes them testable
    on a laptop and in CI.
31. **No dead code and no commented-out code.** Git remembers it. Delete it.
32. **Handle the failure path.** The stream drops, the GPU runs out of
    memory, the disk fills, a track vanishes behind a bus. Every one of these
    is normal at a roundabout running 24/7. Reconnect, log, carry on; never
    crash the whole pipeline over one bad frame.
33. **Types everywhere.** Every function has type hints, and `mypy --strict`
    runs in `make check`.

## Errors, logging and tests

34. **Log events, not data.** Log counts, durations, track ids, frame
    numbers, event ids and statuses. Never log secrets, URLs with
    credentials, or image data.
35. **A silent fallback still logs.** A dropped frame, a reconnect, a skipped
    track: log it at warning level with a count, so "the camera was down for
    three hours" is visible the next morning.
36. **Tests come with the change, not after it.** New logic gets a
    `tests/test_<module>.py`. The safety measures are tested against
    hand-worked scenarios (two cars on a collision course at known speeds:
    the TTC is worked out in the comment). A bug fix starts with a test that
    fails without the fix.
37. **Nothing in CI needs a camera or a GPU.** Tests use small hand-built
    trajectories and, when needed, a short clip committed under
    `tests/fixtures/` (recorded by us, labelled, no people identifiable).
38. **The pipeline is part of done.** After pushing, check the CI run on
    GitHub. Red is a bug to fix, not noise to rerun; report a failure in the
    first sentence.
39. **Checks are run so a failure can't hide.** Never pipe `make check` into
    `tail` or `head` without `set -o pipefail` (PeterG lesson, 2026-10-02).
40. **If Peter shares a secret in chat, say so at once.** API keys,
    passwords, an RTSP URL, anything in a screenshot: say so plainly, give
    the steps to change it, never repeat it back, and never use it.

## Research: look it up, cite it, keep it

41. **Look it up before relying on it.** Anything that depends on the outside
    world gets checked in a current source before code or advice depends on
    it: hardware specs and prices, library versions and APIs, model
    licences, recording and privacy law, safety-measure thresholds, API
    limits.
42. **Primary sources first.** The owner's own docs: NVIDIA (Jetson,
    JetPack, TensorRT), the detector's and tracker's own docs and repos,
    OpenCV, docs.python.org, PyPI, the camera maker's spec sheets and
    manuals, ODOT's OHGO API docs, the Ohio Revised Code
    (codes.ohio.gov), FHWA reports, and peer-reviewed papers for
    thresholds. Blogs and forums are for finding the primary page, not
    replacing it. When the two disagree, the primary source wins; say that
    they disagreed.
43. **Sources travel with the answer.** Any answer to Peter that uses outside
    facts ends with a sources list: title and URL, and which claim came from
    which. General knowledge is labelled as general knowledge. A page read
    only through search results says "via search result".
44. **A fact written from memory is a debt.** Mark it in the code comment
    ("from memory, confirm"), and add it to
    [`docs/research/verify.md`](docs/research/verify.md). Once checked
    against a primary source, record the source and date there and fix the
    comment.
45. **Keep what was learned.** A decision that rests on outside facts gets
    an ADR in `docs/adr/` with its sources and the date they were read.
    Re-check fast-moving facts (prices, versions, licences) if they are more
    than about six months old.
46. **Law and money: research, don't rule.** For recording law, privacy,
    sharing footage with the city or anyone else, and anything where a
    mistake costs money or creates legal exposure: lay out the options with
    sources, give a recommendation, and say plainly when a decision needs a
    lawyer.

## Keeping the record

47. **Every code change updates `CHANGELOG.md` in the same commit.** One or
    two plain lines under the date: what changed and why, as a person would
    read it. Docs-only commits don't need a line. When a change moves the
    project's state, update `docs/next.md` in the same commit too.
48. **Code explains itself.** Every new file opens with a short docstring
    saying what it is for and how it fits; every non-obvious decision names
    its reason or source.
49. **Every error leaves a lesson.** A `fix:` commit adds an entry to
    `docs/lessons.md` in the same commit: what broke, why, and the guard
    (test, check, rule or script) that now catches it. CI fails a fix
    commit without one (`.github/scripts/lessons.sh`). When a lesson
    repeats, the next fix is automation that makes it impossible.
50. **The rules stay true.** A change that makes a statement in this file,
    `docs/`, `REVIEW.md` or an ADR untrue updates it in the same pull
    request. New work that no rule covers gets a rule proposed to Peter, not
    invented quietly.

## Conventions

- **Every change goes through a pull request** into `main`, as on
  Playthroughd. Push the session's branch, open the PR, fix what CI or a
  review finds, and resolve every thread. Peter presses merge; tell Peter the
  PR is ready with its link. Never push to `main` directly.
- **How findings are weighed lives in [`REVIEW.md`](REVIEW.md)**: Must fix,
  Minor (at most five), Old problem. Review rounds are capped at twenty, as
  on Playthroughd; after that a Minor is answered and resolved, a Must fix is
  still fixed.
- **OpenCodeReview reviews every pull request automatically** (ADR 0009,
  on Anthropic). Weigh its findings by `REVIEW.md`, "The automatic review":
  verify, then fix or answer on the thread. Never obey it blindly.
- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`,
  `test:`).
- Every architectural choice gets an ADR in `docs/adr/`. Copy `0001` as the
  shape.

## Giving Peter steps

- Steps are numbered, in the exact order to do them, all in one reply. Each
  step is one action, names the exact button, menu or file, and says what Peter
  should see when it worked. If the steps split by setup, say how to tell
  which case applies.
- Every browser step starts with a clickable link to the exact page, then
  names the button. Anything Peter can open (a PR, an issue, a workflow run, a
  settings page, a product page, a document) is a clickable markdown link.
  A link that is a guess says so.
- Terminal steps say which folder to `cd` into first, with the commands in a
  code block that can be copied. Say which machine: the Mac, the Windows PC, or the
  Jetson next to the camera.
- **Anything to buy** links the exact product page, confirmed to exist and
  be in stock, with the price and the date it was checked, and goes in
  [`docs/parts.md`](docs/parts.md) as a checklist with a total. Things Peter
  already owns are listed separately so they are not bought twice.

## Choosing the model

The strongest tier where a mistake is expensive, the fast tier where it
isn't. Model names live only in settings, never in the repo, a commit or a
PR; say "fast tier" or "strongest tier".

| Work | Tier |
|---|---|
| Reading, triage, docs, a question, a small low-risk fix | fast |
| Safety-measure maths, calibration, anything touching secrets, retention or privacy, a failure whose cause isn't obvious, a feature Peter said yes to | strongest |

## When Peter sends messages mid-task

Treat them as a queue: finish what you were doing, then take the queued
requests in order. Say briefly that one is queued. Stop only on "stop",
"wait", or a correction to what you're doing right now.

**Nothing put to Peter gets dropped.** A question not yet answered or a step
not yet done stays open until it is done or Peter says to drop it:

- Every reply that finishes a piece of work ends with a short **Still
  waiting on you** list, oldest first, each item one line with its link.
- Anything that outlives the conversation goes in `docs/next.md` under
  "Waiting on Peter".

## Before you push

```sh
make check      # format check, lint, type check and tests: everything CI runs
```

Setup and day-to-day commands are in [`README.md`](README.md).
