#!/usr/bin/env bash
# Every "fix" commit must add what it taught to docs/lessons.md (CLAUDE.md
# rule 49), so the next session starts from what broke before. Copied from
# Playthroughd's script of the same name.
#
#   .github/scripts/lessons.sh <range>    e.g. abc123..def456, or a single
#                                         commit as <sha>^!
#
# Only commits whose subject starts "fix:" or "fix(...):" are held to it.
# Merge commits are skipped. Prints each offending commit and exits 1 if
# there is any.
set -euo pipefail

range="${1:?usage: lessons.sh <git range>}"
missing=0
while IFS= read -r c; do
  [ -n "$c" ] || continue
  subject=$(git log -1 --format=%s "$c")
  case "$subject" in
    fix:*|fix\(*) ;;
    *) continue ;;
  esac
  if ! git diff-tree --no-commit-id --name-only -r "$c" | grep -qx 'docs/lessons.md'; then
    printf 'No lesson recorded: %s %s\n' "$(git log -1 --format=%h "$c")" "$subject"
    missing=1
  fi
done < <(git rev-list --no-merges "$range")

if [ "$missing" = 1 ]; then
  echo "A fix commit must add an entry to docs/lessons.md: what broke, why, and what now stops it happening again."
  exit 1
fi
echo "Every fix commit in $range records its lesson."
