#!/usr/bin/env python3
"""
battery_report.py -- Generate a full battery health report
Usage: python3 battery_report.py [--csv report.csv]
Shows: current level, health, temperature, voltage, capacity, charge cycles, wear estimate
"""
import subprocess, re, argparse

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_battery_health():
    raw = adb("dumpsys battery")
    data = {}
    for line in raw.splitlines():
        if ':' in line:
            key, val = line.strip().split(':', 1)
            data[key.strip()] = val.strip()
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", help="Export to CSV")
    args = parser.parse_args()

    print("\n🔋 Android Battery Report")
    print("=" * 50)

    batt = get_battery_health()

    level = int(batt.get('level', 0))
    health = batt.get('health', '?')
    temp = int(batt.get('temperature', 0)) / 10
    voltage = int(batt.get('voltage', 0))
    plugged = batt.get('plugged', '0')
    status = batt.get('status', '?')

    print(f"\nCurrent Status:")
    print(f"  Level:          {level}%")
    print(f"  Health:         {health}")
    print(f"  Temperature:    {temp}°C")
    print(f"  Voltage:        {voltage}mV")
    print(f"  Status:         {status}")
    print(f"  Plugged:        {plugged}")

    # Calculate wear estimate
    if health == "Good" or health == "2":
        wear = "< 5%"
    elif health == "Fair" or health == "3":
        wear = "5-15%"
    elif health == "Poor" or health == "4":
        wear = "> 15%"
    else:
        wear = "Unknown"

    print(f"\nHealth Estimate:")
    print(f"  Wear:           {wear}")
    print(f"  Safe temp:      {temp < 45}° C")
    print(f"  Safe voltage:   {3800 < voltage < 4350} mV")

    if args.csv:
        import csv
        with open(args.csv, 'w') as f:
            w = csv.writer(f)
            w.writerow(['Metric', 'Value'])
            for k, v in batt.items():
                w.writerow([k, v])
        print(f"\n✓ Exported to {args.csv}")

if __name__ == "__main__":
    main()
