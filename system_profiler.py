#!/usr/bin/env python3
import subprocess, time, argparse, re
from collections import deque

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_cpu():
    raw = adb("cat /proc/stat | head -1")
    parts = raw.split()
    if len(parts) < 8:
        return 0
    user, nice, sys, idle, iowait = map(int, parts[1:6])
    total = user + nice + sys + idle + iowait
    busy = total - idle
    return int((busy / total) * 100) if total > 0 else 0

def get_memory():
    raw = adb("cat /proc/meminfo")
    mem_total = mem_free = 0
    for line in raw.splitlines():
        if line.startswith("MemTotal"):
            mem_total = int(line.split()[1])
        elif line.startswith("MemFree"):
            mem_free = int(line.split()[1])
    if mem_total > 0:
        return int(((mem_total - mem_free) / mem_total) * 100)
    return 0

def get_thermal():
    raw = adb("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo 0")
    try:
        temp = int(raw) // 1000
        return temp
    except:
        return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--duration", type=int, default=30)
    args = parser.parse_args()

    print("\n⚡ Android System Profiler")
    print(f"Sampling every {args.interval}s for {args.duration}s\n")
    print(f"{\'Time\':<10} {\'CPU%\':<8} {\'RAM%\':<8} {\'Temp°C\':<8} {\'Status\'}")
    print("─" * 50)

    samples = 0
    cpus, rams = deque(maxlen=30), deque(maxlen=30)

    try:
        end_time = time.time() + args.duration
        while time.time() < end_time:
            cpu = get_cpu()
            mem = get_memory()
            temp = get_thermal()
            cpus.append(cpu)
            rams.append(mem)

            avg_cpu = sum(cpus) // len(cpus) if cpus else 0
            avg_ram = sum(rams) // len(rams) if rams else 0
            status = "🟢" if cpu < 60 else "🟡" if cpu < 80 else "🔴"
            if temp > 40: status = "🔥"

            ts = time.strftime("%H:%M:%S")
            print(f"{ts:<10} {cpu:>6}% {mem:>6}% {temp:>6}°C {status}")
            samples += 1
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass

    print(f"\n{\'─\'*50}")
    if cpus:
        print(f"Avg CPU: {sum(cpus)//len(cpus)}%  Avg RAM: {sum(rams)//len(rams)}%")
    print(f"Samples: {samples}")

if __name__ == "__main__":
    main()
