#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GORZ_BIN="$ROOT_DIR/bin/gorz"

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

[ -f "$GORZ_BIN" ] || fail "bin/gorz does not exist"
[ -x "$GORZ_BIN" ] || fail "bin/gorz is not executable"

bash -n "$GORZ_BIN" || fail "bin/gorz has a bash syntax error"

help_output="$("$GORZ_BIN" help)"
case "$help_output" in
  *"gorz local prototype CLI"*) ;;
  *) fail "help output did not include expected CLI title" ;;
esac

"$GORZ_BIN" version >/dev/null || fail "version command failed"
"$GORZ_BIN" path >/dev/null || fail "path command failed"

doctor_status=0
doctor_output="$("$GORZ_BIN" doctor 2>&1)" || doctor_status=$?

case "$doctor_output" in
  *"Gorz doctor"*) ;;
  *) fail "doctor output did not include diagnostic heading" ;;
esac

case "$doctor_output" in
  *"PASS "*|*"FAIL "*) ;;
  *) fail "doctor output did not include PASS or FAIL checks" ;;
esac

case "$doctor_output" in
  *docker*) ;;
  *) fail "doctor output did not mention docker checks" ;;
esac

if [ "$doctor_status" -gt 8 ]; then
  fail "doctor returned unexpected status $doctor_status"
fi

printf 'PASS gorz CLI shell checks\n'
