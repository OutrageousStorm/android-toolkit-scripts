#!/bin/bash
# Quick device stats one-liner
adb shell "echo 'Memory:'; free -h; echo; echo 'Storage:'; df -h /data; echo; echo 'Top CPU:'; top -n 1 | head -8"
