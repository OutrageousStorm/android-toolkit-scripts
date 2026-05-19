#!/usr/bin/env python3
"""
service_monitor.py -- Monitor running Android services and track their CPU/memory usage
Usage: python3 service_monitor.py [--filter keyword] [--interval 2]
"""
import subprocess, re, time, argparse

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_services():
    out = adb("service list")
    services = {}
    for line in out.splitlines():
        m = re.match(r'\s+(\S+):\s+\[(.*?)\]', line)
        if m:
            services[m.group(1)] = m.group(2)
    return services

def get_memory_stats():
    out = adb("dumpsys meminfo --unreachable")
    stats = {}
    for line in out.splitlines():
        if "TOTAL" in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if p == "TOTAL":
                    total_kb = int(parts[i+1]) if i+1 < len(parts) else 0
                    stats['total'] = total_kb
    return stats

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", help="Filter services by keyword")
    parser.add_argument("--interval", type=int, default=3)
    args = parser.parse_args()

    print("\n🔧 Android Service Monitor\n")
    try:
        while True:
            services = get_services()
            if args.filter:
                services = {k:v for k,v in services.items() if args.filter.lower() in k.lower()}

            print(f"{'Service':<40} {'Status'}")
            print("─" * 60)
            for name, status in sorted(services.items())[:20]:
                icon = "✅" if status == "running" else "⏸️ "
                print(f"  {icon} {name:<37} {status}")

            print(f"\nShowing {len(services)} services | refresh every {args.interval}s\n")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
