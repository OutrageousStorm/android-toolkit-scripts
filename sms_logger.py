#!/usr/bin/env python3
"""sms_logger.py -- Log all SMS messages from device"""
import subprocess, re

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

out = adb("dumpsys telephony.registry | grep -A5 'SMS'")
if not out:
    out = adb("content query --uri content://sms --projection address,date,body")

print("\n📱 SMS Messages:")
print("─" * 60)
for line in out.splitlines():
    if '|' in line:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 3:
            print(f"  From: {parts[0]:<20} [{parts[1][:10]}]")
            print(f"  Text: {parts[2][:70]}")
            print()
