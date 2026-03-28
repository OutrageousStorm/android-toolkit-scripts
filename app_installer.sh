#!/bin/bash
# app_installer.sh -- Batch install APKs
set -e
DIR="${1:-.}"
APKS=($(find "$DIR" -maxdepth 1 -name "*.apk"))
[[ ${#APKS[@]} -eq 0 ]] && echo "No APKs in $DIR" && exit 1
echo "📲 Installing ${#APKS[@]} APKs"
success=0; fail=0
for apk in "${APKS[@]}"; do
    echo -n "  $(basename "$apk")... "
    if adb install -r "$apk" 2>&1 | grep -q "Success"; then
        echo "✓"; ((success++))
    else
        echo "✗"; ((fail++))
    fi
done
echo "✅ $success OK, $fail failed"
