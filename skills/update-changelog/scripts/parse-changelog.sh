#!/usr/bin/env bash
#
# parse-changelog.sh — Parse a Keep a Changelog format CHANGELOG.md into JSON
#
# Usage:
#   ./parse-changelog.sh [path/to/CHANGELOG.md]
#
# Defaults to CHANGELOG.md in the current directory.
# Outputs JSON array of version entries to stdout.
#
# Useful for:
#   - Migrating an existing CHANGELOG.md into a structured data file
#   - Verifying sync between CHANGELOG.md and a data file
#   - CI/CD scripts that need changelog data

set -euo pipefail

CHANGELOG_FILE="${1:-CHANGELOG.md}"

if [ ! -f "$CHANGELOG_FILE" ]; then
  echo "Error: $CHANGELOG_FILE not found" >&2
  exit 1
fi

awk '
BEGIN {
  print "["
  first = 1
  in_version = 0
  version = ""
  date = ""
  content = ""
}

/^## \[/ {
  # Flush previous entry
  if (in_version) {
    if (!first) printf ","
    first = 0
    # Escape content for JSON
    gsub(/\\/, "\\\\", content)
    gsub(/"/, "\\\"", content)
    gsub(/\n/, "\\n", content)
    gsub(/\t/, "\\t", content)
    # Remove leading/trailing newlines from content
    sub(/^\\n+/, "", content)
    sub(/\\n+$/, "", content)
    printf "\n  {\"version\": \"%s\", \"date\": \"%s\", \"content\": \"%s\"}", version, date, content
  }

  # Parse new version header: ## [1.2.3] - Month DD, YYYY
  line = $0
  sub(/^## \[/, "", line)
  split(line, parts, /\] *- */)
  version = parts[1]
  date = parts[2]
  # Clean trailing whitespace
  sub(/[[:space:]]+$/, "", date)
  content = ""
  in_version = 1
  next
}

/^## \[Unreleased\]/ {
  in_version = 0
  next
}

/^# / { next }

in_version {
  content = content $0 "\n"
}

END {
  if (in_version) {
    if (!first) printf ","
    gsub(/\\/, "\\\\", content)
    gsub(/"/, "\\\"", content)
    gsub(/\n/, "\\n", content)
    gsub(/\t/, "\\t", content)
    sub(/^\\n+/, "", content)
    sub(/\\n+$/, "", content)
    printf "\n  {\"version\": \"%s\", \"date\": \"%s\", \"content\": \"%s\"}", version, date, content
  }
  print "\n]"
}
' "$CHANGELOG_FILE"
