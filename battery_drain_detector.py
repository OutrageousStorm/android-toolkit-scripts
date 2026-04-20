#!/usr/bin/env python3
"""
battery_drain_detector.py -- Real-time battery drain monitor
Shows which apps are draining battery in real time by watching dumpsys battery output.
Usage: python3 battery_drain_detector.py [--threshold 5]  (alert if drain > 5%/min)
"""
import subprocess, time, re
from datetime import datetime

def get_battery():
    r = subprocess.run("adb shell dumpsys battery", shell=True, capture_output=True, text=True)
    battery = {}
    for line in r.stdout.splitlines():
        line = line.strip()
        m = re.match(r'(\w+):\s*(.+)', line)
        if m:
            battery[m.group(1).lower()] = m.group(2)
    return battery

def get_top_drain():
    r = subprocess.run("adb shell dumpsys batterystats | grep 'uid'", shell=True, capture_output=True, text=True)
    lines = r.stdout.splitlines()[:10]
    return "\n".join(f"  {l.strip()}" for l in lines if l.strip())

def main():
    print("\n🔋 Battery Drain Detector")
    print("=" * 45)
    print("Monitoring in real time... (press Ctrl+C to stop)\n")

    last_level = None
    last_time = datetime.now()
    readings = []

    try:
        while True:
            b = get_battery()
            level = int(b.get('level', 0))
            temp = int(b.get('temperature', 0)) / 10
            status = b.get('status', '?')
            health = b.get('health', '?')

            now = datetime.now()
            if last_level is not None:
                delta = last_level - level
                elapsed = (now - last_time).total_seconds()
                if elapsed > 0:
                    drain_per_min = (delta / elapsed) * 60
                    readings.append(drain_per_min)
                    if len(readings) > 10:
                        readings.pop(0)
                    avg_drain = sum(readings) / len(readings) if readings else 0

                    ts = now.strftime("%H:%M:%S")
                    print(f"[{ts}] Battery {level}% | Temp {temp}°C | Drain {delta}% in {elapsed:.0f}s ({drain_per_min:.1f}%/min avg)")

                    if drain_per_min > 5:
                        print(f"  ⚠️  HIGH DRAIN! Top apps:")
                        print(get_top_drain())

            last_level = level
            last_time = now
            time.sleep(30)

    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
