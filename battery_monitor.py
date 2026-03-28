#!/usr/bin/env python3
"""
battery_monitor.py -- Real-time battery stats monitor
Shows: current %, temperature, voltage, health, current draw (mA).
Usage: python3 battery_monitor.py [--interval 2] [--alert 20]
"""
import subprocess, sys, time, argparse, re

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

def parse_battery():
    out = adb("dumpsys battery")
    data = {}
    for line in out.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            data[k.strip()] = v.strip()
    return data

def format_temp(c):
    f = c * 9/5 + 32
    return f"{c}°C ({f:.0f}°F)"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=float, default=2.0)
    parser.add_argument('--alert', type=int, default=15, help='Alert at % battery')
    args = parser.parse_args()

    print("🔋 Battery Monitor (Ctrl+C to stop)\n")

    try:
        while True:
            data = parse_battery()
            level = int(data.get('level', 0))
            temp = int(data.get('temperature', 0)) / 10
            voltage = data.get('voltage', 'N/A')
            status = data.get('status', 'unknown')
            health = data.get('health', 'unknown')
            current = data.get('current now', 'N/A')

            # Status icon
            icon = "🔴" if level <= args.alert else "🟢" if level > 50 else "🟡"

            print(f"\r{icon} {level:3d}%  |  {format_temp(temp):<13}  |  {voltage} mV  |  {status:<10}  |  {current:>8}", end='', flush=True)

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n\nStopped.")

if __name__ == "__main__":
    main()
