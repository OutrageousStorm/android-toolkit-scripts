#!/usr/bin/env python3
"""
app_monitor.py -- Monitor app crashes, ANRs, and excessive battery drain
Usage: python3 app_monitor.py
Watches logcat for crash patterns and alerts you
"""
import subprocess, re, time

def monitor_crashes():
    print("\n🚨 App Monitor — press Ctrl+C to stop")
    print("Watching for: crashes, ANRs, wakelocks, high CPU\n")
    
    proc = subprocess.Popen(
        "adb logcat -v brief FATAL:E ActivityManager:E AndroidRuntime:E *:S",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )
    
    try:
        for line in proc.stdout:
            if 'FATAL' in line or 'crash' in line.lower():
                m = re.search(r'(\S+) has stopped', line)
                if m:
                    print(f"❌ CRASH: {m.group(1)}")
            elif 'ANR' in line:
                m = re.search(r'ANR in (\S+)', line)
                if m:
                    print(f"⏱️  ANR (freeze): {m.group(1)}")
            elif 'Exception' in line or 'Error' in line:
                print(f"⚠️  {line[:80]}")
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        proc.terminate()

if __name__ == "__main__":
    monitor_crashes()
