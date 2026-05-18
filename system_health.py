#!/usr/bin/env python3
"""
system_health.py -- Quick system health check for Android device
CPU throttling, thermal status, storage health, battery condition
Usage: python3 system_health.py
"""
import subprocess, re

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

def check():
    print("\n🏥 Android System Health Check\n")
    
    # CPU
    print("[CPU]")
    freq = adb("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null || echo '0'")
    max_freq = adb("cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq")
    freq_mhz = int(freq) // 1000 if freq != '0' else 0
    max_mhz = int(max_freq) // 1000
    print(f"  Current: {freq_mhz} MHz / {max_mhz} MHz", end="")
    if freq_mhz < max_mhz * 0.5:
        print(" ⚠️  THROTTLED")
    else:
        print(" ✓")
    
    # Thermal
    print("[Thermal]")
    thermal = adb("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo '0'")
    temp_c = int(thermal) / 1000 if thermal != '0' else 0
    print(f"  Zone 0: {temp_c:.1f}°C", end="")
    if temp_c > 45: print(" 🔥 HOT")
    elif temp_c > 40: print(" ⚠️  WARM")
    else: print(" ✓")
    
    # Storage
    print("[Storage]")
    df = adb("df -h /data | tail -1")
    parts = df.split()
    if len(parts) >= 5:
        used = parts[2]
        avail = parts[3]
        percent = int(parts[4].rstrip('%'))
        icon = "✓" if percent < 80 else "⚠️ " if percent < 90 else "🔴"
        print(f"  /data: {used} used, {avail} free ({percent}%) {icon}")
    
    # Battery
    print("[Battery]")
    level = adb("dumpsys battery | grep level")
    temp = adb("dumpsys battery | grep temperature")
    print(f"  {level}")
    print(f"  {temp}")

if __name__ == "__main__":
    check()
