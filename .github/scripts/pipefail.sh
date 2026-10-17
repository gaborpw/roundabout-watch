#!/usr/bin/env bash
# Fails unless every workflow runs its steps as bash with pipefail. GitHub's
# default shell is `bash -e {0}`, without pipefail, so `cmd | tee` reports
# success when cmd fails; `shell: bash` runs `bash --noprofile --norc -eo
# pipefail {0}` (GitHub's workflow-syntax reference, "defaults.run.shell").
# Copied from Playthroughd, where the same mistake bit twice (docs/lessons.md).
set -euo pipefail
dir="${1:-$(dirname "$0")/../workflows}"
bad=0
for f in "$dir"/*.yml; do
  if ! grep -Pzq '(?m)^defaults:\n  run:\n    shell: bash\n' "$f"; then
    echo "$f: needs a top-level 'defaults: run: shell: bash'"
    bad=1
  fi
  if grep -nE '^\s*shell:' "$f" | grep -vE 'shell:\s*bash\s*$'; then
    echo "$f: a step or job asks for a shell other than bash"
    bad=1
  fi
done
exit "$bad"
