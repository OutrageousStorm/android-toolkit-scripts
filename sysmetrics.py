#!/usr/bin/env python3
"""
sysmetrics.py -- Real-time Android system metrics
CPU, RAM, temp, battery, network bandwidth — live updating.
Usage: python3 sysmetrics.py [--interval 1] [--csv metrics.csv]
"""
import subprocess, time, argparse, csv
from datetime import datetime

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_cpu_usage():
    try:
        out = adb("cat /proc/stat | head -1")
        return out.split()[1:5]  # user, nice, system, idle
    except:
        return [0, 0, 0, 0]

def get_ram():
    out = adb("cat /proc/meminfo | head -2")
    lines = out.splitlines()
    total = int(lines[0].split()[1]) if lines else 0
    free = int(lines[1].split()[1]) if len(lines) > 1 else 0
    used = total - free
    return used, total

def get_temp():
    """Try to read thermal zone temp"""
    try:
        out = adb("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null")
        temp_mC = int(out.strip())
        return temp_mC / 1000
    except:
        return None

def get_battery():
    out = adb("dumpsys battery | grep -E 'level|temp' | head -2")
    lines = out.splitlines()
    level = int(lines[0].split()[-1]) if lines else 0
    temp = int(lines[1].split()[-1]) // 10 if len(lines) > 1 else 0
    return level, temp

def get_network():
    """Total bytes sent/received"""
    try:
        out = adb("cat /proc/net/dev | tail -n +3 | awk '{s+=$2; r+=$10} END {print s, r}'")
        sent, recv = map(int, out.split())
        return sent, recv
    except:
        return 0, 0

def bytes_to_human(b):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if b < 1024:
            return f"{b:.1f}{unit}"
        b /= 1024
    return f"{b:.1f}TB"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--csv", help="Log to CSV file")
    args = parser.parse_args()

    print("
📊 Android System Metrics")
    print("=" * 60)
    print(f"{'Time':<12} {'CPU%':<8} {'RAM':<12} {'Temp':<8} {'Batt':<8} {'Net Send'}")
    print("-" * 60)

    csv_writer = None
    if args.csv:
        csv_file = open(args.csv, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['timestamp', 'cpu_pct', 'ram_mb', 'temp_c', 'battery_pct', 'net_sent_kb'])

    last_net = None
    try:
        while True:
            ts = datetime.now().strftime("%H:%M:%S")
            
            # CPU: rough estimate
            cpu_raw = get_cpu_usage()
            total = sum(int(x) for x in cpu_raw)
            idle = int(cpu_raw[3]) if len(cpu_raw) > 3 else 0
            cpu_pct = max(0, (100 * (total - idle) // total)) if total > 0 else 0

            # RAM
            used_kb, total_kb = get_ram()
            ram_pct = (100 * used_kb) // total_kb if total_kb > 0 else 0

            # Temp
            temp = get_temp()
            temp_str = f"{temp:.0f}°C" if temp else "—"

            # Battery
            batt_pct, batt_temp = get_battery()

            # Network (delta)
            sent, recv = get_network()
            if last_net:
                delta_sent = (sent - last_net[0]) // 1024
                delta_str = f"{delta_sent}KB/s"
            else:
                delta_str = "—"
            last_net = (sent, recv)

            line = f"{ts:<12} {cpu_pct:>5}% {ram_pct:>5}% {temp_str:<8} {batt_pct:>3}% {delta_str}"
            print(line)

            if csv_writer:
                csv_writer.writerow([ts, cpu_pct, used_kb // 1024, temp or 0, batt_pct, delta_sent if last_net else 0])
                csv_file.flush()

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("
Stopped.")
    finally:
        if csv_writer:
            csv_file.close()
            print(f"✅ Logged to {args.csv}")

if __name__ == "__main__":
    main()
