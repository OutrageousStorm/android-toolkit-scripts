#!/usr/bin/env python3
"""
notification_sniffer.py -- Sniff and log all Android notifications in real time
Shows package, app label, title, text, and timestamp. Zero dependencies.
Usage: python3 notification_sniffer.py [--json] [--filter keyword]
"""
import subprocess, re, sys, argparse, json
from datetime import datetime
from collections import defaultdict

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_label(pkg):
    parts = pkg.split('.')
    return parts[-1] if len(parts) > 1 else pkg

def sniff():
    """Live sniff via logcat"""
    proc = subprocess.Popen(
        "adb logcat -v time NotificationManager NotificationService StatusBar:D *:S",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )
    
    print("🔔 Notification Sniffer — press Ctrl+C to stop\n")
    for line in iter(proc.stdout.readline, ''):
        # Catch "enqueue" or "post" lines with package info
        if any(x in line for x in ['enqueue', 'post', 'notify']):
            pkg_m = re.search(r'pkg[=:\s]+([a-z][a-z0-9_.]+)', line)
            if pkg_m:
                pkg = pkg_m.group(1)
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] {get_label(pkg):<20} {line[:80]}")

def dump_json(output_file=None):
    """Dump all active notifications as JSON"""
    raw = adb("dumpsys notification --noredact")
    notifications = []
    for line in raw.splitlines():
        if 'NotificationRecord' in line and 'pkg=' in line:
            pkg_m = re.search(r'pkg=([^,\s]+)', line)
            pkg = pkg_m.group(1) if pkg_m else ""
            notifications.append({"pkg": pkg, "time": datetime.now().isoformat(), "raw": line[:100]})
    
    result = json.dumps(notifications, indent=2)
    if output_file:
        with open(output_file, 'w') as f:
            f.write(result)
        print(f"✅ Saved to {output_file}")
    else:
        print(result)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Dump to JSON")
    parser.add_argument("--output", help="JSON output file")
    parser.add_argument("--filter", help="Filter by keyword")
    args = parser.parse_args()

    if args.json:
        dump_json(args.output)
    else:
        try:
            sniff()
        except KeyboardInterrupt:
            print("\n\nStopped.")

if __name__ == "__main__":
    main()
