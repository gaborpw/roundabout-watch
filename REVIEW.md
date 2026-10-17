# Review rules

How pull requests here are reviewed. CLAUDE.md is the standard the code is
held to; this file says how findings are weighed and reported. Kept short on
purpose: a long rules file dilutes the rules that matter. The shape is
copied from Playthroughd's REVIEW.md (its ADR 0013).

## Labels

Start every finding with one of these:

- **Must fix:** it breaks behaviour, leaks a secret (an RTSP URL counts),
  keeps footage longer than the retention rule, identifies a person
  (CLAUDE.md 19), loses data, or breaks a written rule: a change with no test
  (36), no CHANGELOG line (47), a `fix:` with no lesson (49). Also: a
  flagged event shown or counted as a confirmed one (the one idea, ADR 0002),
  safety measures computed in pixels instead of metres, or a change that
  makes a rule, a doc or an ADR untrue without updating it.
- **Minor:** worth doing, not blocking: naming, clarity, a missed edge case
  with no real path to harm, a comment that could say more.
- **Old problem:** a real bug this pull request didn't introduce. Reported so
  Peter knows; never holds up this pull request.

## How much

- At most **five Minor** findings in a review. If there are more, post the
  five that matter most and say "plus N similar" in the summary.
- **Re-reviews** look only at what changed since the last review and post
  **Must fix** findings only, so reviewing and fixing can't loop.

## Before posting a finding

- Name the file and line, and the input or path that makes it fail. A claim
  about what code does comes from reading that code, not from a function's
  name.
- For the safety maths, give the scenario (positions, speeds, headings) and
  the number it should have produced.
- If you can't trace a real path to harm, it is Minor at most, or nothing.

## Don't report

- What CI already checks: formatting, lint, type errors, failing tests.
- `uv.lock`, and committed test fixtures.
- Style the file already uses consistently (CLAUDE.md 26).

## Rules stay true

When a pull request changes how something works, check CLAUDE.md, `docs/`
and the ADRs for statements it makes untrue: a threshold, a retention
period, a file name, a module boundary, a part in `docs/parts.md`. An untrue
rule left behind is a Must fix. A new kind of work with no rule covering it
is worth a Minor suggesting one.

## The automatic review (OpenCodeReview)

Every pull request also gets OpenCodeReview's comments (ADR 0010). Its
findings are claims to verify, not orders:

- Trace a real path from a caller or an input to the failure. If the path is
  real and the fix is in proportion, fix it.
- Otherwise answer its thread with the path you traced and why the fix isn't
  worth its code, and tell Peter.
- A security finding's thread stays open until Peter decides.
- Its rules live in `.opencodereview/rule.json`, and its prompt in
  `.github/workflows/ocr-review.yml`. When this file's labels or the
  Must-fix list change, update both in the same pull request.

## The summary

Open with a one-line tally, such as "1 Must fix, 2 Minor, 0 Old problem", or
"No blocking problems." when there is no Must fix. Then the findings, then
what you could not check (for example: "not run on the desktop's GPU").
