# Changelog

Every change that reaches `main`, newest first, in one or two plain lines
each. CLAUDE.md rule 47: a code change adds its line here in the same commit.
Dates are when the change landed.

## Unreleased

- **Pull requests get an automatic AI review** (Peter's ask, 2026-10-17;
  ADR 0009). Alibaba's OpenCodeReview runs on Anthropic, comments on each
  push, and does nothing until Peter adds the API key.
- **The project starts** (Peter's ask, 2026-10-17). Rules and steering files
  adapted from Playthroughd, the architecture, the parts list, the research
  so far, and the shared types every stage will pass between them
  (`model.py`), with tests. Nothing watches a camera yet.
