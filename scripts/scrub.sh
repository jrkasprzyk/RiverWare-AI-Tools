#!/bin/sh
# Private-reference scrub gate.
#
# This repository was carved out of a private one. The gate is a regression
# guard: it fails the build if a reference to the author's machine or private
# work reappears in a committed file. It is NOT a secret scanner -- it only
# knows the specific strings listed below. GitHub's push protection covers
# credentials.
#
# Run it yourself before pushing:
#
#     sh scripts/scrub.sh
#
# Exit 0 means clean; exit 1 prints every offending file:line.
#
# ---------------------------------------------------------------------------
# Adding a pattern: prefer the most specific string that still catches the
# leak. A pattern that also matches ordinary water-resources prose or a
# legitimately public model name will fire on innocent content, and a gate
# that cries wolf gets bypassed. `NorthSouth` alone was such a pattern -- a
# public model could carry that name -- so it is anchored to the date suffix
# of the private model file instead.
#
# Escaping a false positive: put the marker `scrub-allow` in a comment on the
# same line. Use it for genuinely public content the patterns cannot express,
# such as a documented Windows install path. Every use is greppable:
#
#     grep -rn scrub-allow .
# ---------------------------------------------------------------------------
set -eu

PATTERNS='joka0958|BorgRWProblems|NorthSouth[0-9]{6,}|scratchpad[/\\]|C:[/\\]'

# -I skips binary files: .pyc bytecode embeds the build machine's absolute
# paths and would otherwise trip the C:\ pattern after any local test run.
hits=$(grep -rniEI "$PATTERNS" \
        --exclude-dir=.git \
        --exclude-dir=__pycache__ \
        --exclude-dir=.venv \
        --exclude-dir=node_modules \
        --exclude=scrub.sh \
        . 2>/dev/null | grep -v 'scrub-allow' || true)

if [ -n "$hits" ]; then
    echo "$hits"
    echo ""
    echo "Private references found. Remove them, or if the match is genuinely"
    echo "public content, add a 'scrub-allow' comment on that line."
    exit 1
fi

echo "scrub clean"
