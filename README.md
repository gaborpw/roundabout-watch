# Roundabout Watch

One camera overlooking a roundabout in Cleveland, Ohio, and a small computer
beside it that tracks every vehicle, cyclist and pedestrian, measures how
close they come to each other, and saves a short clip of every near-miss and
possible crash **for a person to review**. Nothing it flags counts until a
person has watched it (`docs/adr/0002`).

**Status (2026-10-17):** designed, not built. The rules, architecture, parts
list and shared types exist; the pipeline arrives one pull request at a time
(`docs/architecture.md`, "Build order").

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
