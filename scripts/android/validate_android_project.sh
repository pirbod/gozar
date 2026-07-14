#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ANDROID_DIR="$ROOT/android/gorz"
APP_DIR="$ANDROID_DIR/app"
MAIN_MANIFEST="$APP_DIR/src/main/AndroidManifest.xml"
DEMO_MANIFEST="$APP_DIR/src/demo/AndroidManifest.xml"

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "Missing required file: ${path#$ROOT/}" >&2
    exit 1
  fi
}

require_grep() {
  local pattern="$1"
  local path="$2"
  local message="$3"
  if ! grep -q "$pattern" "$path"; then
    echo "$message" >&2
    exit 1
  fi
}

require_file "$ANDROID_DIR/settings.gradle.kts"
require_file "$ANDROID_DIR/build.gradle.kts"
require_file "$APP_DIR/build.gradle.kts"
require_file "$MAIN_MANIFEST"
require_file "$DEMO_MANIFEST"
require_file "$APP_DIR/src/main/java/com/pirbod/gorz/MainActivity.kt"
require_file "$APP_DIR/src/main/java/com/pirbod/gorz/GorzVpnService.kt"
require_file "$APP_DIR/src/main/java/com/pirbod/gorz/ProfileApiClient.kt"
require_file "$APP_DIR/src/main/java/com/pirbod/gorz/ProfileCrypto.kt"
require_file "$APP_DIR/src/main/java/com/pirbod/gorz/SafetyGuards.kt"
require_file "$ROOT/README.md"

require_grep "android.net.VpnService" "$DEMO_MANIFEST" "Demo AndroidManifest.xml must declare android.net.VpnService intent action"
require_grep "android.permission.BIND_VPN_SERVICE" "$DEMO_MANIFEST" "Demo AndroidManifest.xml must protect the VPN service"
require_grep "android.permission.INTERNET" "$MAIN_MANIFEST" "Main AndroidManifest.xml must declare INTERNET permission"
require_grep "Android Phase 2 Prototype" "$ROOT/README.md" "README.md must document Android Phase 2"

python3 "$ROOT/scripts/android/check_android_safety_wording.py"

if command -v java >/dev/null 2>&1 && command -v gradle >/dev/null 2>&1 && [[ -n "${ANDROID_HOME:-}" || -n "${ANDROID_SDK_ROOT:-}" ]]; then
  (cd "$ANDROID_DIR" && ./gradlew testDemoDebugUnitTest testInternalDebugUnitTest)
else
  echo "Warning: Java, Gradle, or Android SDK not available; skipped Android Gradle unit tests." >&2
fi

echo "Android project validation passed."
