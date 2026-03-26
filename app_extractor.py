#!/usr/bin/env python3
"""
app_extractor.py — Extract APKs from connected Android device
Usage: python3 app_extractor.py [--output ./apks] [--user-only] [--filter keyword]
"""
import subprocess, os, sys, argparse
from pathlib import Path

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def adb_pull(src, dst):
    r = subprocess.run(f"adb pull {src} {dst}", shell=True, capture_output=True, text=True)
    return r.returncode == 0

def get_packages(user_only=False, filter_kw=None):
    flag = "-3" if user_only else ""
    out = adb(f"pm list packages {flag}")
    pkgs = [l.split(":")[1] for l in out.splitlines() if l.startswith("package:")]
    if filter_kw:
        pkgs = [p for p in pkgs if filter_kw.lower() in p.lower()]
    return pkgs

def get_apk_path(pkg):
    out = adb(f"pm path {pkg}")
    if out.startswith("package:"):
        return out[8:]
    return None

def main():
    parser = argparse.ArgumentParser(description="Extract APKs from Android device")
    parser.add_argument("--output", default="./extracted_apks", help="Output directory")
    parser.add_argument("--user-only", action="store_true", help="Only extract user-installed apps")
    parser.add_argument("--filter", help="Filter packages by keyword")
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📦 APK Extractor → {out_dir.resolve()}")
    print("=" * 50)

    pkgs = get_packages(args.user_only, args.filter)
    print(f"Found {len(pkgs)} packages\n")

    success, fail = 0, 0
    for pkg in pkgs:
        apk_path = get_apk_path(pkg)
        if not apk_path:
            print(f"  ✗ {pkg} — path not found")
            fail += 1
            continue

        out_file = out_dir / f"{pkg}.apk"
        ok = adb_pull(apk_path, str(out_file))
        if ok:
            size = out_file.stat().st_size // 1024
            print(f"  ✓ {pkg} ({size} KB)")
            success += 1
        else:
            print(f"  ✗ {pkg} — pull failed")
            fail += 1

    print(f"\n{'='*50}")
    print(f"✅ Extracted: {success}   ❌ Failed: {fail}")
    print(f"Output: {out_dir.resolve()}")

if __name__ == "__main__":
    main()
