# 9. Automatic review with OpenCodeReview, on Anthropic

- **Status:** accepted (Peter's yes, 2026-10-17)
- **Date:** 2026-10-17

## Context

On Playthroughd, every pull request gets an AI review (the Claude review and
PR-Agent), weighed by REVIEW.md. Peter asked for automatic reviews here too,
with Alibaba's OpenCodeReview (github.com/alibaba/open-code-review), and chose
Anthropic as the AI provider ("anthropic i guess", 2026-10-17).

OpenCodeReview is a review CLI plus a GitHub Action (Apache-2.0, about 47k
stars, tag v1.13.1). It brings no AI of its own: it sends the pull request's
diff to the provider it's given and posts inline comments and a summary.
Telemetry is off by default (its `telemetry.md`).

## Decision

- **`.github/workflows/ocr-review.yml`** runs it on every push to a pull
  request (not drafts). After the first review, a push reviews only the new
  commits and doesn't repeat comments on the same lines (`checkpoint_range`,
  `incremental`).
- **Pinned** to the v1.13.1 commit, with the CLI pinned to 1.13.1. The
  project's own docs say `@main`, but this action gets an API key and can
  write on pull requests, so an upstream change must not reach it silently
  (CLAUDE.md 24).
- **`pull_request`, not `pull_request_target`.** The project's example uses
  the latter so pull requests from forks get secrets; a private repository
  with one author has no forks, and `pull_request_target` is the riskier
  trigger.
- **The provider lives in the repository's settings, not the code:**
  - secrets `OCR_LLM_URL` and `OCR_LLM_AUTH_TOKEN`;
  - variables `OCR_LLM_MODEL`, `OCR_LLM_PROTOCOL`, and optionally
    `OCR_LLM_EXTRA_BODY`.

  Changing the model or provider is a settings change. The model is the
  strongest tier, as CLAUDE.md's table asks for review work; its name lives
  only in the variable.
- **Thinking stays on.** The action's default request body turns the model's
  thinking off, which current Claude models reject with an error, so the
  workflow sends an empty body instead.
- **A token ceiling per run** (`max_tokens_budget`, 400,000 to start), so one
  large pull request can't run up the bill. Over the ceiling, the review
  publishes what it has and says which files it skipped.
- **Until the key is set, the job passes** and says in its log that no
  review ran, so CI isn't red for a missing setting.
- **`.opencodereview/rule.json`** gives it REVIEW.md's labels and this
  project's Must-fix list, and points it at REVIEW.md and CLAUDE.md, which
  win if they differ.

## Consequences

- Each pull request's diff goes to Anthropic. The repository holds no
  secrets and no footage (CLAUDE.md 15, 21), so the diff carries nothing
  that shouldn't leave.
- **Cost:** Anthropic's API is pay as you go, per token (prices in the Claude
  API docs; a review's token count isn't measured yet). A monthly spend limit
  on the key's Anthropic Console workspace is the backstop (Anthropic's
  workspaces announcement; the Console steps aren't confirmed). Each run
  also uses a few Actions minutes.
- Its findings are claims to verify, not orders (REVIEW.md, "The automatic
  review"), and the twenty-round cap applies to them as to any review.
- **Trade-off:** a second reviewer that costs money per pull request and
  reads like Claude's own review, in exchange for every change being looked
  at before Peter merges.
- **Not yet confirmed:** that OpenCodeReview's tool-using loop works with
  Claude's thinking turned on. The first pull request after the key is set
  shows it; if it fails, `OCR_LLM_EXTRA_BODY` and the model variable are
  where to fix it, without a code change.

## Sources (read 2026-10-17)

- OpenCodeReview's README, `action.yml`, CI integration docs, review-rules
  and telemetry docs, read from the repository at tag v1.13.1:
  https://github.com/alibaba/open-code-review (the docs site,
  open-codereview.ai, returned 404).
- Tag and commit: `git ls-remote` on the repository; npm
  `@alibaba-group/open-code-review` 1.13.1, Apache-2.0.
- Current Claude models, prices and thinking settings: the Claude API docs
  bundled with Claude Code (cached 2026-10-06).
- Workspace spend limits: https://anthropic.com/news/workspaces and
  https://platform.claude.com/docs/en/api/admin/spend_limits/create.md (via
  search result).
