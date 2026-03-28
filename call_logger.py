#!/usr/bin/env python3
"""call_logger.py -- Dump call logs from device"""
import subprocess

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

out = adb("content query --uri content://call_log/calls --projection number,date,duration,type")

print("\n☎️  Call Logs:")
print("─" * 70)
print(f"{'Number':<20} {'Type':<10} {'Duration':<12} {'Date'}")
print("─" * 70)

for line in out.splitlines():
    if '|' in line:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 4:
            num = parts[0][:20]
            type_map = {"1":"Incoming", "2":"Outgoing", "3":"Missed"}
            ctype = type_map.get(parts[3], "?")
            dur = f"{int(parts[2])//60}m {int(parts[2])%60}s" if parts[2].isdigit() else "—"
            print(f"{num:<20} {ctype:<10} {dur:<12}")
