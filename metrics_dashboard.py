#!/usr/bin/env python3
"""
metrics_dashboard.py -- Real-time Android system metrics dashboard
Usage: python3 metrics_dashboard.py [--interval 1]
Shows: CPU, RAM, battery, temperature, network in a live updating view.
"""
import subprocess, time, sys, argparse, os
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich import box
    console = Console()
except ImportError:
    print("Install: pip install rich")
    sys.exit(1)

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_cpu_usage():
    out = adb("top -n 1 -b | grep '^CPU'")
    return out.replace("CPU:", "").strip()

def get_memory():
    out = adb("cat /proc/meminfo | grep -E '^MemTotal|^MemAvailable'")
    lines = out.splitlines()
    total = int(lines[0].split()[1]) // 1024 if lines else 0
    avail = int(lines[1].split()[1]) // 1024 if len(lines) > 1 else 0
    used = total - avail
    return total, used, avail

def get_battery():
    out = adb("dumpsys battery")
    info = {}
    for line in out.splitlines():
        if ": " in line:
            k, v = line.strip().split(": ", 1)
            info[k.strip()] = v.strip()
    return info.get("level", "?"), info.get("temperature", "?"), info.get("status", "?")

def get_network():
    out = adb("dumpsys telephony.registry | grep -i 'mDataActivity'")
    return out[:50] if out else "N/A"

def get_thermal():
    temps = []
    for i in range(5):
        t = adb(f"cat /sys/class/thermal/thermal_zone{i}/temp 2>/dev/null")
        if t and t.isdigit():
            temps.append(int(t) // 1000)
    return temps[0] if temps else "?", max(temps) if temps else "?"

def build_dashboard(cpu, mem, bat, net, temp):
    t, u, a = mem
    table = Table(box=box.ROUNDED, title="📊 Android Metrics Dashboard")
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Value", style="white", width=30)

    table.add_row("CPU Usage", cpu)
    table.add_row("RAM", f"{u}MB / {t}MB ({100*u//t if t else 0}%)")
    table.add_row("Available RAM", f"{a}MB")
    
    level, temp_c, status = bat
    table.add_row("Battery Level", f"{level}% ({status})")
    table.add_row("Battery Temp", f"{temp_c}°C")
    
    current, peak = temp
    table.add_row("CPU Temp", f"{current}°C (peak: {peak}°C)")
    
    table.add_row("Network", net)
    table.add_row("Updated", datetime.now().strftime("%H:%M:%S"))

    return table

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()

    print("📊 Android Metrics Dashboard — press Ctrl+C to stop\n")

    try:
        while True:
            cpu = get_cpu_usage() or "—"
            mem = get_memory()
            bat = get_battery()
            net = get_network()
            temp = get_thermal()

            dashboard = build_dashboard(cpu, mem, bat, net, temp)
            os.system("clear" if os.name != "nt" else "cls")
            console.print(dashboard)
            print(f"Refreshing every {args.interval}s...\n")

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
