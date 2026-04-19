#!/usr/bin/env python3
"""
process_monitor.py -- Watch Android processes in real time
Shows CPU, memory, threads per process. Like 'top' for Android.
Usage: python3 process_monitor.py [--filter keyword] [--interval 2]
"""
import subprocess, time, re, argparse, os
from collections import defaultdict

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_processes():
    out = adb("ps -A")
    procs = []
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 9:
            procs.append({
                'user': parts[0], 'pid': parts[1], 'ppid': parts[2],
                'vsize': int(parts[4]), 'rss': int(parts[5]),
                'name': parts[-1]
            })
    return procs

def get_top_processes():
    """Get top processes by memory usage"""
    out = adb("top -n 1 | head -20")
    procs = []
    for line in out.splitlines()[7:]:
        parts = line.split()
        if len(parts) >= 9:
            try:
                procs.append({
                    'pid': parts[0], 'cpu': float(parts[1]),
                    'mem': float(parts[2]), 'name': parts[-1]
                })
            except ValueError:
                pass
    return sorted(procs, key=lambda x: x['mem'], reverse=True)

def format_size(bytes_):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_ < 1024:
            return f"{bytes_:.0f}{unit}"
        bytes_ /= 1024
    return f"{bytes_:.1f}TB"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", help="Filter by process name")
    parser.add_argument("--interval", type=float, default=2)
    args = parser.parse_args()

    print("\n📊 Android Process Monitor — Ctrl+C to stop\n")
    print(f"{'PID':<8} {'Name':<40} {'CPU%':<8} {'Memory':<12}")
    print("─" * 70)

    try:
        while True:
            procs = get_top_processes()
            for p in procs[:15]:
                if args.filter and args.filter.lower() not in p['name'].lower():
                    continue
                name = p['name'][-35:] if len(p['name']) > 35 else p['name']
                mem_str = format_size(p['mem'] * 1000) if p['mem'] < 10000 else f"{p['mem']:.0f}MB"
                print(f"{p['pid']:<8} {name:<40} {p['cpu']:>6.1f}%  {mem_str:<12}")
            print()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
