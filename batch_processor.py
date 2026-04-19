#!/usr/bin/env python3
"""
batch_processor.py -- Batch process multiple APK files
Extract, patch, sign, and push bulk APKs in parallel.
Usage: python3 batch_processor.py --input ./apks --action extract
       python3 batch_processor.py --input ./apks --action audit-perms --output results.csv
"""
import subprocess, os, sys, argparse, concurrent.futures, csv
from pathlib import Path

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

def extract_apk(apk_path):
    """Extract APK to inspect"""
    name = apk_path.stem
    out_dir = f"./{name}_extracted"
    r = subprocess.run(f"apktool d {apk_path} -o {out_dir} -f", shell=True, capture_output=True)
    return out_dir if r.returncode == 0 else None

def audit_permissions(apk_path):
    """Scan APK for requested permissions"""
    r = subprocess.run(f"aapt dump badging {apk_path} | grep uses-permission", 
                       shell=True, capture_output=True, text=True)
    perms = [line.split("'")[1] for line in r.stdout.splitlines() if "permission" in line]
    return perms

def install_batch(apk_dir):
    """Install all APKs from directory"""
    installed = 0
    for apk in Path(apk_dir).glob("*.apk"):
        r = subprocess.run(f"adb install {apk}", shell=True, capture_output=True, text=True)
        if "Success" in r.stdout:
            installed += 1
            print(f"  ✓ {apk.name}")
        else:
            print(f"  ✗ {apk.name}")
    return installed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input directory with APKs")
    parser.add_argument("--action", required=True, 
                       choices=["extract", "audit-perms", "install", "sign-all"])
    parser.add_argument("--output", help="Output CSV for audit-perms")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    apk_files = list(Path(args.input).glob("*.apk"))
    if not apk_files:
        print(f"No APKs found in {args.input}")
        sys.exit(1)

    print(f"\n🔄 Batch Processor — {args.action} on {len(apk_files)} files")
    print("=" * 50)

    if args.action == "extract":
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
            for apk in apk_files:
                ex.submit(lambda a: print(f"  Extracted: {extract_apk(a)}"), apk)

    elif args.action == "audit-perms":
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(audit_permissions, apk): apk for apk in apk_files}
            for future in concurrent.futures.as_completed(futures):
                apk = futures[future]
                perms = future.result()
                results.append((apk.name, len(perms), ", ".join(perms[:5])))
                print(f"  {apk.name}: {len(perms)} permissions")
        
        if args.output:
            with open(args.output, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["APK", "Perm Count", "Sample Perms"])
                for row in results:
                    w.writerow(row)
            print(f"\n✅ Saved to {args.output}")

    elif args.action == "install":
        print(f"Installing {len(apk_files)} APKs...\n")
        count = install_batch(args.input)
        print(f"\n✅ {count}/{len(apk_files)} installed")

    elif args.action == "sign-all":
        print(f"Signing {len(apk_files)} APKs...\n")
        for apk in apk_files:
            ks = Path.home() / ".android" / "debug.keystore"
            signed = apk.parent / f"{apk.stem}_signed.apk"
            cmd = f"apksigner sign --ks {ks} --ks-pass pass:android --out {signed} {apk}"
            r = subprocess.run(cmd, shell=True, capture_output=True)
            status = "✓" if r.returncode == 0 else "✗"
            print(f"  {status} {apk.name}")

if __name__ == "__main__":
    main()
