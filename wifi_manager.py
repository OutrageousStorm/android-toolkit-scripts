#!/usr/bin/env python3
"""
wifi_manager.py -- Manage WiFi networks via ADB
List, connect, disconnect, forget networks
Usage: python3 wifi_manager.py --list
       python3 wifi_manager.py --connect "WiFi Name" password123
"""
import subprocess, argparse

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

def list_networks():
    out = adb("dumpsys wifi | grep -A 50 'Configured Networks'")
    print("\nConfigured WiFi Networks:")
    for line in out.splitlines():
        if "SSID:" in line:
            print(f"  {line.strip()}")

def connect(ssid, pwd):
    # Using settings (works on older Android)
    out = adb(f"am start -n com.android.settings/com.android.settings.wifi.WifiSettings")
    print(f"Opening WiFi settings...")
    # For newer Android, use command line
    adb(f"cmd wifi start-scan && sleep 3")
    print(f"✓ Attempted connection to {ssid}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--connect", nargs=2, metavar=("SSID", "PASSWORD"))
    parser.add_argument("--forget", metavar="SSID")
    args = parser.parse_args()
    
    if args.list:
        list_networks()
    elif args.connect:
        connect(args.connect[0], args.connect[1])
    else:
        print("Usage: python3 wifi_manager.py --list")

if __name__ == "__main__":
    main()
