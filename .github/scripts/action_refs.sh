#!/usr/bin/env bash
# Fails unless every `uses: owner/repo@ref` in the workflows names a tag or
# branch that exists on GitHub. Some actions publish only full versions
# (astral-sh/setup-uv has v10.3.0 but no v10), and a missing ref fails the
# job before any step runs (docs/lessons.md, 2026-10-17). Needs network.
# Local actions (./) and docker:// images are skipped; so is a ref pinned to
# a full commit SHA, which ls-remote can't look up.
set -euo pipefail
dir="${1:-$(dirname "$0")/../workflows}"
bad=0
while IFS= read -r ref; do
  action="${ref%@*}"
  version="${ref##*@}"
  repo="$(cut -d/ -f1-2 <<<"$action")"
  if [[ "$version" =~ ^[0-9a-f]{40}$ ]]; then
    continue
  fi
  if ! git ls-remote --exit-code "https://github.com/$repo" "refs/tags/$version" "refs/heads/$version" >/dev/null 2>&1; then
    echo "$ref: no tag or branch '$version' in github.com/$repo"
    bad=1
  fi
# Only real `uses:` keys (optionally after a list dash) count; the word in
# a comment does not.
done < <(grep -hE '^[[:space:]]*(-[[:space:]]+)?uses:' "$dir"/*.yml \
  | sed -E 's/^[[:space:]]*(-[[:space:]]+)?uses:[[:space:]]*//; s/[[:space:]]*#.*$//' \
  | grep -vE '^(\./|docker://)' | sort -u)
exit "$bad"
