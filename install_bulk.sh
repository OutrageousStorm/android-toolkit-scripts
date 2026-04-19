#!/bin/bash
# install_bulk.sh -- Batch install APKs from a folder via ADB
# Usage: ./install_bulk.sh /path/to/apks/folder [--skip-errors] [--force]

set -e

FOLDER="${1:-.}"
SKIP_ERRORS=false
FORCE=false

[[ "$2" == "--skip-errors" ]] && SKIP_ERRORS=true
[[ "$2" == "--force" ]] && FORCE=true
[[ "$3" == "--force" ]] && FORCE=true

[[ ! -d "$FOLDER" ]] && echo "Folder not found: $FOLDER" && exit 1

echo "📲 APK Batch Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━"

if ! adb devices | grep -q "device$"; then
    echo "❌ No device connected."
    exit 1
fi

SUCCESS=0; FAIL=0; SKIP=0

for apk in "$FOLDER"/*.apk; do
    [[ ! -f "$apk" ]] && continue
    name=$(basename "$apk")
    
    # Check if already installed
    pkg=$(unzip -p "$apk" AndroidManifest.xml 2>/dev/null | grep -oP '(?<=package=")[^"]+' 2>/dev/null || echo "")
    if [[ -z "$pkg" ]]; then
        echo "  ⚠️  $name (could not read package)"
        ((SKIP++))
        continue
    fi
    
    if adb shell pm list packages | grep -q "^package:$pkg$" && [[ "$FORCE" != "true" ]]; then
        echo "  ⏭  $name (already installed, use --force to overwrite)"
        ((SKIP++))
        continue
    fi
    
    # Install
    opts="-r"  # replace
    [[ "$FORCE" == "true" ]] && opts="$opts -d"  # downgrade
    result=$(adb install $opts "$apk" 2>&1)
    if echo "$result" | grep -q "Success"; then
        echo "  ✓ $name"
        ((SUCCESS++))
    else
        echo "  ✗ $name"
        [[ "$SKIP_ERRORS" != "true" ]] && exit 1
        ((FAIL++))
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Installed: $SUCCESS   ⏭  Skipped: $SKIP   ❌ Failed: $FAIL"
