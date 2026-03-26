#!/bin/bash
# smart_debloat.sh — Interactive Android debloater with safety checks
# Usage: ./smart_debloat.sh [listfile]
# Example: ./smart_debloat.sh lists/samsung.txt

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

SAFE_CORE=(
  "com.android.systemui"
  "com.android.settings"
  "com.android.providers.settings"
  "com.android.providers.contacts"
  "com.android.providers.telephony"
  "com.google.android.gms"
  "com.android.phone"
  "com.android.server.telecom"
  "com.android.nfc"
  "com.android.bluetooth"
  "android"
)

is_safe_core() {
  for safe in "${SAFE_CORE[@]}"; do
    [[ "$1" == "$safe" ]] && return 0
  done
  return 1
}

check_device() {
  if ! adb devices | grep -q "device$"; then
    echo -e "${RED}❌ No device connected. Enable USB debugging.${NC}"
    exit 1
  fi
}

pkg_exists() {
  adb shell pm list packages "$1" 2>/dev/null | grep -q "^package:$1$"
}

remove_pkg() {
  local pkg="$1"
  if is_safe_core "$pkg"; then
    echo -e "  ${RED}⛔ BLOCKED (core system) — $pkg${NC}"
    return 1
  fi
  if ! pkg_exists "$pkg"; then
    echo -e "  ${YELLOW}⏭  Not found — $pkg${NC}"
    return 0
  fi
  result=$(adb shell pm uninstall -k --user 0 "$pkg" 2>&1)
  if echo "$result" | grep -q "Success"; then
    echo -e "  ${GREEN}✓ Removed — $pkg${NC}"
    return 0
  else
    echo -e "  ${RED}✗ Failed — $pkg ($result)${NC}"
    return 1
  fi
}

# ── Main ──────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}${CYAN}🗑️  Smart Android Debloater${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_device

MODEL=$(adb shell getprop ro.product.model 2>/dev/null)
ANDROID=$(adb shell getprop ro.build.version.release 2>/dev/null)
echo -e "Device: ${BOLD}$MODEL${NC} (Android $ANDROID)"
echo ""

if [[ -z "$1" ]]; then
  echo "Usage: $0 <package-list.txt>"
  echo ""
  echo "Available lists:"
  find . -name "*.txt" -not -path "./.git/*" | sort | sed 's/^/  /'
  echo ""
  echo "Or enter package names interactively:"
  echo -n "Package name (or q to quit): "
  while read -r line; do
    [[ "$line" == "q" ]] && break
    [[ -z "$line" ]] && { echo -n "Package name: "; continue; }
    remove_pkg "$line"
    echo -n "Package name (or q to quit): "
  done
  exit 0
fi

if [[ ! -f "$1" ]]; then
  echo -e "${RED}File not found: $1${NC}"
  exit 1
fi

removed=0; failed=0; skipped=0

while IFS= read -r pkg; do
  [[ "$pkg" =~ ^#.*$ ]] && continue
  [[ -z "${pkg// }" ]] && continue
  pkg=$(echo "$pkg" | tr -d '\r' | xargs)
  if remove_pkg "$pkg"; then
    ((removed++)) || true
  else
    ((failed++)) || true
  fi
done < "$1"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Removed: $removed${NC}   ${RED}❌ Failed/Skipped: $failed${NC}"
echo ""
echo "💡 Restore any package with:"
echo "   adb shell cmd package install-existing <package.name>"
