#!/usr/bin/env python3
"""
device_info.py — Full Android device report via ADB
Usage: python3 device_info.py
"""
import subprocess, sys, json
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    console = Console()
    RICH = True
except ImportError:
    RICH = False
    class Console:
        def print(self, *a, **k): print(*a)
    console = Console()

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def adb_raw(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def check_device():
    devices = adb_raw("adb devices").splitlines()
    connected = [l for l in devices[1:] if "device" in l and "offline" not in l]
    if not connected:
        console.print("[red]No device connected. Enable USB debugging and try again.[/red]")
        sys.exit(1)
    return connected[0].split()[0]

def prop(key):
    return adb(f"getprop {key}")

def main():
    serial = check_device()
    console.print(f"\n[bold cyan]Android Device Report[/bold cyan] — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    console.print(f"Serial: [dim]{serial}[/dim]\n")

    sections = {
        "Device": [
            ("Model",           prop("ro.product.model")),
            ("Brand",           prop("ro.product.brand")),
            ("Manufacturer",    prop("ro.product.manufacturer")),
            ("Codename",        prop("ro.product.device")),
            ("Hardware",        prop("ro.hardware")),
            ("Board",           prop("ro.product.board")),
        ],
        "Software": [
            ("Android version", prop("ro.build.version.release")),
            ("API level",       prop("ro.build.version.sdk")),
            ("Security patch",  prop("ro.build.version.security_patch")),
            ("Build fingerprint", prop("ro.build.fingerprint")),
            ("Build type",      prop("ro.build.type")),
            ("Build tags",      prop("ro.build.tags")),
        ],
        "CPU": [
            ("Architecture",    prop("ro.product.cpu.abi")),
            ("CPU variant",     prop("ro.product.cpu.abilist")),
            ("CPU info",        adb("cat /proc/cpuinfo | grep 'Hardware' | head -1")),
            ("Cores",           adb("nproc")),
            ("Current freq",    adb("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null || echo N/A")),
            ("Max freq",        adb("cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq 2>/dev/null || echo N/A")),
        ],
        "Memory": [
            ("Total RAM",       adb("cat /proc/meminfo | grep MemTotal")),
            ("Free RAM",        adb("cat /proc/meminfo | grep MemFree")),
            ("Available RAM",   adb("cat /proc/meminfo | grep MemAvailable")),
        ],
        "Storage": [
            ("Internal",        adb("df -h /data | tail -1")),
            ("SD Card",         adb("df -h /sdcard 2>/dev/null | tail -1 || echo N/A")),
        ],
        "Battery": [
            ("Level",           adb("dumpsys battery | grep level")),
            ("Status",          adb("dumpsys battery | grep status")),
            ("Health",          adb("dumpsys battery | grep health")),
            ("Temperature",     adb("dumpsys battery | grep temperature")),
            ("Voltage",         adb("dumpsys battery | grep voltage")),
            ("Plugged",         adb("dumpsys battery | grep plugged")),
        ],
        "Network": [
            ("Wi-Fi SSID",      adb("dumpsys wifi | grep 'mWifiInfo' | grep -oP 'SSID: \K[^,]+'  2>/dev/null || echo N/A")),
            ("IP address",      adb("ip route | grep src | awk '{print $NF}' | head -1")),
            ("MAC address",     adb("ip link show wlan0 | grep link/ether | awk '{print $2}' 2>/dev/null || echo N/A")),
        ],
        "Security": [
            ("Bootloader",      prop("ro.boot.verifiedbootstate")),
            ("Encryption",      adb("getprop ro.crypto.state")),
            ("SELinux",         adb("getenforce 2>/dev/null || echo N/A")),
            ("ADB enabled",     adb("settings get global adb_enabled")),
            ("Root detected",   "Yes" if adb("which su 2>/dev/null") else "No"),
        ],
    }

    for section, items in sections.items():
        if RICH:
            t = Table(box=box.SIMPLE, show_header=False, padding=(0,1))
            t.add_column("Key", style="dim", width=22)
            t.add_column("Value", style="white")
            for k, v in items:
                t.add_row(k, v or "—")
            console.print(Panel(t, title=f"[bold]{section}[/bold]", border_style="blue"))
        else:
            print(f"\n=== {section} ===")
            for k, v in items:
                print(f"  {k:<22} {v or '—'}")

if __name__ == "__main__":
    main()
