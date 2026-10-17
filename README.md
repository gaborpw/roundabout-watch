# Roundabout Watch

One camera overlooking a roundabout in Cleveland, Ohio, and Peter's desktop
next to it, which tracks every vehicle, cyclist and pedestrian, measures how
close they come to each other, and saves a short clip of every near-miss and
possible crash **for a person to review**. Nothing it flags counts until a
person has watched it (`docs/adr/0002`).

**Status (2026-10-17):** the near-miss maths and a first look exist: `replay`
finds and follows road users in a video file and draws them on a copy. No
camera yet, and no near-miss numbers until calibration. The rest arrives one
pull request at a time (`docs/architecture.md`, "Build order").

## Where to start

| Read | For |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | The rules every change follows |
| [`docs/next.md`](docs/next.md) | Where things stand and what's waiting on Peter |
| [`docs/vision.md`](docs/vision.md) | What Peter wants, in Peter's own words |
| [`docs/architecture.md`](docs/architecture.md) | How the code fits together, and the build order |
| [`docs/parts.md`](docs/parts.md) | Everything to buy, as a checklist |
| [`docs/research/`](docs/research/) | Who already does this, and Ohio's data sources |
| [`docs/adr/`](docs/adr/) | Why each decision was made |

## Running the checks

Needs [uv](https://docs.astral.sh/uv/getting-started/installation/). On the
Mac, from the folder you cloned into:

```sh
cd ~/roundabout-watch
uv sync
make check
```

`make check` runs formatting, lint, `mypy --strict` and the tests: exactly
what CI runs. Nothing in it needs a camera or a GPU.

On the Windows PC, `make` isn't installed by default; run the same four
commands it runs:

```
cd C:\Users\gabor\roundabout-watch
uv sync
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
```

## Try it on a video (the first look)

On the Mac, with a video of the roundabout from the phone (AirDrop puts it in
Downloads). Landscape works best.

```sh
cd ~/roundabout-watch
git pull
uv sync --extra detector
uv run python -m roundabout_watch replay ~/Downloads/IMG_1234.MOV
```

Use the video's real name in place of `IMG_1234.MOV`. It writes
`IMG_1234.tracked.mp4` next to the video, with a box, a number and a trail on
every car, bike and person; open it in QuickTime.

- The first run downloads PyTorch and the detector's weights (368 MB for the
  default size), so it's slow once.
- `--model medium` finds more and runs slower; `--model nano` the opposite.
- The Mac's GPU is used automatically.
- On the Windows desktop the same commands work, on the CPU only for now:
  PyPI's PyTorch for Windows has no CUDA (its CUDA libraries are listed for
  Linux only in `uv.lock`). Using the 3080 Ti comes with build step 6.
