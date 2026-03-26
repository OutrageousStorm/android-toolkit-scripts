#!/usr/bin/env python3
"""
network_monitor.py — Real-time network connection monitor for Android
Usage: python3 network_monitor.py [--interval 2] [--filter keyword]
Shows all active connections from the device, refreshing every N seconds.
"""
import subprocess, sys, time, argparse, os
from datetime import datetime

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_connections():
    raw = adb("cat /proc/net/tcp6 /proc/net/tcp 2>/dev/null")
    connections = []
    for line in raw.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        try:
            local_hex = parts[1]
            remote_hex = parts[2]
            state_hex = parts[3]
            uid = int(parts[7]) if len(parts) > 7 else -1

            def parse_addr(hex_addr):
                if ":" not in hex_addr:
                    return "?", 0
                addr_part, port_part = hex_addr.rsplit(":", 1)
                port = int(port_part, 16)
                # IPv4
                if len(addr_part) == 8:
                    b = bytes.fromhex(addr_part)
                    ip = f"{b[3]}.{b[2]}.{b[1]}.{b[0]}"
                else:
                    ip = "IPv6"
                return ip, port

            local_ip, local_port = parse_addr(local_hex)
            remote_ip, remote_port = parse_addr(remote_hex)

            states = {"01":"ESTABLISHED","02":"SYN_SENT","06":"TIME_WAIT","0A":"LISTEN","0B":"CLOSING"}
            state = states.get(state_hex.upper(), state_hex)

            if remote_ip not in ("0.0.0.0", "IPv6", "?") and remote_port != 0:
                connections.append({
                    "local": f"{local_ip}:{local_port}",
                    "remote": f"{remote_ip}:{remote_port}",
                    "state": state,
                    "uid": uid,
                })
        except Exception:
            continue
    return connections

def get_uid_map():
    """Map UIDs to package names"""
    raw = adb("pm list packages -U 2>/dev/null || dumpsys package | grep 'userId='")
    uid_map = {}
    for line in raw.splitlines():
        if "uid=" in line:
            parts = line.strip().split()
            pkg = parts[0].replace("package:", "") if parts else ""
            for p in parts:
                if p.startswith("uid="):
                    try:
                        uid_map[int(p[4:])] = pkg
                    except ValueError:
                        pass
    return uid_map

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=2.0, help="Refresh interval in seconds")
    parser.add_argument("--filter", help="Filter by IP or package keyword")
    args = parser.parse_args()

    print("\n📡 Android Network Monitor")
    print("Press Ctrl+C to stop\n")

    uid_map = get_uid_map()

    try:
        while True:
            os.system("clear" if os.name != "nt" else "cls")
            conns = get_connections()
            print(f"📡 Android Network Monitor — {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'Remote':<25} {'State':<14} {'Local':<22} {'App'}")
            print("─" * 80)
            shown = 0
            for c in conns:
                pkg = uid_map.get(c["uid"], f"uid:{c['uid']}")
                if args.filter and args.filter.lower() not in c["remote"].lower() and args.filter.lower() not in pkg.lower():
                    continue
                print(f"{c['remote']:<25} {c['state']:<14} {c['local']:<22} {pkg}")
                shown += 1
            if shown == 0:
                print("  (no active connections)")
            print(f"\n{shown} connections | refresh every {args.interval}s | Ctrl+C to stop")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
