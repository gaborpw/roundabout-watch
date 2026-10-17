# 10. OpenCodeReview in delegation mode, on Peter's Claude subscription

- **Status:** accepted (Peter's choice, 2026-10-17)
- **Date:** 2026-10-17. Supersedes ADR 0009.

## Context

ADR 0009 set up OpenCodeReview with an Anthropic API key, paid per token.
Peter then said:

> wait i want the alibaba review thats free not the antropic one

> ahhhh ok ok ill connect my claude code then

OpenCodeReview is free software (Apache-2.0), but it brings no AI of its own:
something has to read the code. The free or already-paid-for options, read on
2026-10-17:

- **Delegation mode on a Claude subscription.** OpenCodeReview's docs: "OCR
  handles deterministic engineering (file selection, rule resolution) while
  the host agent performs the actual code review using its own LLM
  capabilities. No LLM endpoint is required on the OCR side", designed for
  "subscription-based AI coding agents — such as Claude Code". Peter already
  pays for a Claude subscription, and Playthroughd's review runs on it in CI
  through `anthropics/claude-code-action` and `CLAUDE_CODE_OAUTH_TOKEN`.
- **GitHub Models:** retired on July 30, 2026 (GitHub's docs).
- **Gemini API free tier:** free, but Google's pricing page says free-tier
  content is "Used to improve our products: Yes".
- **Cloudflare Workers AI:** 10,000 free Neurons a day. With gpt-oss-120b
  (31,818 Neurons per million input tokens) that is roughly 300,000 input
  tokens a day; whether it works with OpenCodeReview isn't confirmed.
- **Alibaba Model Studio (Qwen):** a free quota for new users, Singapore
  region only, about 90 days, then paid (via search result).

## Decision

- **Delegation mode, run by Claude Code on Peter's subscription.**
  - `.github/workflows/ocr-review.yml` installs OpenCodeReview 1.13.1 and
    runs `anthropics/claude-code-action@v1` (the same action and token as
    Playthroughd).
  - Claude follows OpenCodeReview's own `delegate-review` steps:
    `ocr delegate preview` for the files, `ocr delegate rule` for each
    file's checklist (which includes `.opencodereview/rule.json`), then the
    diffs.
  - Its tools are limited to reading, those `ocr` and `git` commands, and
    posting comments.
- **It reports and never fixes.** OpenCodeReview's command fixes High and
  Medium issues itself; in CI that would push code nobody reviewed, so the
  prompt forbids changing files.
- **Re-reviews** start from the last commit a review saw (a hidden marker in
  its summary) and report only Must fix findings, as REVIEW.md says.
- **One secret,** `CLAUDE_CODE_OAUTH_TOKEN`. Until it is set, the job passes
  and says so in its log.

## Consequences

- **No new bill.** Reviews use the subscription's quota, which Peter's own
  Claude Code use shares; a busy day of pull requests uses some of it.
- **No new data sharing.** The diff goes to Anthropic through Claude Code,
  as Playthroughd's already does.
- **Changes to this workflow aren't reviewed by it.** claude-code-action
  only runs a workflow identical to the one on `main` (noted in
  Playthroughd's review workflow).
- **Trade-off:** OpenCodeReview's own review engine (its agent loop,
  incremental comments, sticky summary) isn't used, only its file selection
  and rules; in exchange the review costs nothing extra and needs no new
  account.
- **Not yet confirmed:** that OpenCodeReview's delegate commands run cleanly
  in CI (its docs describe a local agent). The first reviewed pull request
  shows it.

## Sources (read 2026-10-17)

- OpenCodeReview delegation mode: `pages/src/content/docs/en/integrations/delegate.md`
  and `plugins/open-code-review/claude-code/commands/delegate-review.md` in
  https://github.com/alibaba/open-code-review (read from the repository).
- GitHub Models retirement: https://docs.github.com/en/github-models/use-github-models/prototyping-with-ai-models
- Gemini API pricing and free-tier data use: https://ai.google.dev/gemini-api/docs/pricing
- Workers AI free allocation and gpt-oss-120b Neurons: https://developers.cloudflare.com/workers-ai/platform/pricing/
- Alibaba Model Studio free quota: https://www.alibabacloud.com/help/model-studio/
  (via search result)
- Playthroughd's `.github/workflows/claude-review.yml` for the action, the
  token and the permissions.
