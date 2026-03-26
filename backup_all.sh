#!/bin/bash
# backup_all.sh — Backup Android device (APKs + shared storage)
# Usage: ./backup_all.sh [output_dir]

set -e
BOLD='\033[1m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

OUT="${1:-./android_backup_$(date +%Y%m%d_%H%M%S)}"
mkdir -p "$OUT"

echo -e "\n${BOLD}💾 Android Backup Tool${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! adb devices | grep -q "device$"; then
  echo -e "${RED}❌ No device connected.${NC}"; exit 1
fi

MODEL=$(adb shell getprop ro.product.model)
ANDROID=$(adb shell getprop ro.build.version.release)
DATE=$(date +%Y-%m-%d)
echo -e "Device: ${BOLD}$MODEL${NC} (Android $ANDROID)"
echo -e "Output: ${BOLD}$OUT${NC}\n"

# 1. Device info snapshot
echo -e "${YELLOW}📋 Device info...${NC}"
{
  echo "Backup Date: $DATE"
  echo "Model: $MODEL"
  echo "Android: $ANDROID"
  echo "Serial: $(adb get-serialno)"
  echo "Build: $(adb shell getprop ro.build.fingerprint)"
  echo "Security patch: $(adb shell getprop ro.build.version.security_patch)"
} > "$OUT/device_info.txt"
echo "  ✓ device_info.txt"

# 2. Installed packages list
echo -e "${YELLOW}📦 Package list...${NC}"
adb shell pm list packages -3 | sort > "$OUT/user_packages.txt"
adb shell pm list packages -s | sort > "$OUT/system_packages.txt"
echo "  ✓ user_packages.txt ($(wc -l < "$OUT/user_packages.txt") apps)"
echo "  ✓ system_packages.txt"

# 3. Extract user APKs
echo -e "${YELLOW}📲 Extracting user APKs...${NC}"
mkdir -p "$OUT/apks"
apk_count=0
while IFS= read -r line; do
  pkg="${line#package:}"
  path=$(adb shell pm path "$pkg" 2>/dev/null | head -1 | sed 's/package://')
  if [[ -n "$path" ]]; then
    adb pull "$path" "$OUT/apks/$pkg.apk" 2>/dev/null && ((apk_count++)) || true
  fi
done < "$OUT/user_packages.txt"
echo "  ✓ $apk_count APKs extracted"

# 4. Shared storage
echo -e "${YELLOW}🗂  Shared storage (DCIM, Documents, Downloads)...${NC}"
for folder in DCIM Documents Download Music; do
  count=$(adb shell ls /sdcard/$folder 2>/dev/null | wc -l)
  if [[ $count -gt 0 ]]; then
    mkdir -p "$OUT/storage/$folder"
    adb pull "/sdcard/$folder" "$OUT/storage/$folder" 2>/dev/null || true
    echo "  ✓ $folder ($count items)"
  fi
done

# 5. Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Backup complete!${NC}"
du -sh "$OUT"
echo "Location: $(realpath $OUT)"
