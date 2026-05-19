#!/usr/bin/env python3
import subprocess
def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()
print("\n[System Profile]\n")
freq = adb("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null || echo 0")
print(f"CPU: {int(freq)//1000} MHz")
for i in range(2):
    temp_mc = adb(f"cat /sys/class/thermal/thermal_zone{i}/temp 2>/dev/null || echo 0")
    print(f"Thermal Zone {i}: {int(temp_mc)//1000}C")
print()
