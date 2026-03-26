#!/usr/bin/env python3
"""
permission_audit.py — Scan every installed app for dangerous permissions
Usage: python3 permission_audit.py [--csv output.csv] [--user-only]
"""
import subprocess, sys, csv, argparse
from pathlib import Path

DANGEROUS_PERMISSIONS = [
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_BACKGROUND_LOCATION",
    "android.permission.READ_CALL_LOG",
    "android.permission.WRITE_CALL_LOG",
    "android.permission.PROCESS_OUTGOING_CALLS",
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.SEND_SMS",
    "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.READ_MEDIA_VIDEO",
    "android.permission.READ_MEDIA_AUDIO",
    "android.permission.GET_ACCOUNTS",
    "android.permission.USE_BIOMETRIC",
    "android.permission.USE_FINGERPRINT",
    "android.permission.BODY_SENSORS",
    "android.permission.ACTIVITY_RECOGNITION",
    "android.permission.READ_PHONE_STATE",
    "android.permission.READ_PHONE_NUMBERS",
    "android.permission.ANSWER_PHONE_CALLS",
    "android.permission.BLUETOOTH_SCAN",
    "android.permission.BLUETOOTH_CONNECT",
    "android.permission.UWB_RANGING",
]

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_packages(user_only=False):
    flag = "-3" if user_only else ""
    out = adb(f"pm list packages {flag}")
    return [l.split(":")[1] for l in out.splitlines() if l.startswith("package:")]

def get_granted_permissions(pkg):
    out = adb(f"dumpsys package {pkg}")
    granted = []
    in_granted = False
    for line in out.splitlines():
        if "install permissions:" in line.lower() or "runtime permissions:" in line.lower():
            in_granted = True
        if in_granted and "granted=true" in line:
            for perm in DANGEROUS_PERMISSIONS:
                if perm in line:
                    granted.append(perm.split(".")[-1])
    return granted

def get_app_name(pkg):
    out = adb(f"cmd package resolve-activity --brief {pkg} 2>/dev/null | head -2 | tail -1")
    return out if out and "/" in out else pkg

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", help="Export results to CSV file")
    parser.add_argument("--user-only", action="store_true", help="Only scan user-installed apps")
    args = parser.parse_args()

    print("\n🔍 Android Permission Auditor")
    print("=" * 50)

    devices = subprocess.run("adb devices", shell=True, capture_output=True, text=True).stdout
    if "device" not in devices.split("List")[1] if "List" in devices else "":
        print("❌ No device connected.")
        sys.exit(1)

    packages = get_packages(args.user_only)
    print(f"Scanning {len(packages)} packages...\n")

    results = []
    for i, pkg in enumerate(packages):
        perms = get_granted_permissions(pkg)
        if perms:
            results.append((pkg, perms))
            print(f"  ⚠️  {pkg}")
            for p in perms:
                print(f"       └─ {p}")

        if (i + 1) % 20 == 0:
            print(f"  ... {i+1}/{len(packages)} scanned")

    print(f"\n{'='*50}")
    print(f"Found {len(results)} apps with dangerous permissions")
    print(f"Clean:  {len(packages) - len(results)} apps")

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Package", "Permissions"])
            for pkg, perms in results:
                writer.writerow([pkg, ", ".join(perms)])
        print(f"\n✅ Exported to {args.csv}")

    print("\n💡 Revoke with:")
    print("   adb shell pm revoke <package> android.permission.<PERMISSION>")

if __name__ == "__main__":
    main()
