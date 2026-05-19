#!/usr/bin/env python3
"""
getevent_parser.py -- Parse Android getevent output to readable touch events
Live logs: tap coordinates, hold duration, swipe trajectory, multi-touch.
Usage: python3 getevent_parser.py [--output log.json]
"""
import subprocess, re, json, sys, argparse
from collections import defaultdict
from datetime import datetime

def stream_getevent(output_file=None):
    print("📱 Touch Event Parser — Ctrl+C to stop\n")
    print("Touch events (taps, swipes, holds):\n")
    
    proc = subprocess.Popen(
        "adb shell getevent",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )
    
    events = []
    current_touch = None
    x, y = 0, 0
    
    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            
            # Parse: /dev/input/event0: 0001 014a 00000001
            m = re.match(r'/dev/input/event\d+:\s+(\w+)\s+(\w+)\s+(\w+)', line)
            if not m:
                continue
            
            type_hex = m.group(1)
            code_hex = m.group(2)
            val_hex = m.group(3)
            
            # 0001 = EV_KEY (BTN_TOUCH)
            if type_hex == "0001" and code_hex == "014a":
                if val_hex == "00000001":
                    # Touch down
                    current_touch = {"x": x, "y": y, "start": datetime.now()}
                    print(f"  DOWN: ({x}, {y})")
                elif val_hex == "00000000":
                    # Touch up
                    if current_touch:
                        duration = (datetime.now() - current_touch["start"]).total_seconds()
                        dx = abs(x - current_touch["x"])
                        dy = abs(y - current_touch["y"])
                        touch_event = {
                            "type": "tap" if (dx < 50 and dy < 50) else "swipe",
                            "start": current_touch,
                            "end": {"x": x, "y": y},
                            "duration_ms": int(duration * 1000),
                            "distance": (dx**2 + dy**2)**0.5
                        }
                        events.append(touch_event)
                        print(f"  UP:   ({x}, {y}) | {touch_event['type'].upper()} {int(duration*1000)}ms")
                        current_touch = None
            
            # 0003 = EV_ABS (absolute position)
            elif type_hex == "0003":
                if code_hex == "0035":  # ABS_X
                    x = int(val_hex, 16)
                elif code_hex == "0036":  # ABS_Y
                    y = int(val_hex, 16)
    
    except KeyboardInterrupt:
        print("\n\nStopped.")
    finally:
        proc.terminate()
    
    if output_file and events:
        with open(output_file, 'w') as f:
            json.dump(events, f, indent=2, default=str)
        print(f"\n✅ Saved {len(events)} events to {output_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Save events to JSON")
    args = parser.parse_args()
    stream_getevent(args.output)

if __name__ == "__main__":
    main()
