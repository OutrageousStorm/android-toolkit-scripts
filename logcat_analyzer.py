#!/usr/bin/env python3
"""
logcat_analyzer.py -- Parse Android logcat for errors, crashes, ANRs
Usage: python3 logcat_analyzer.py [--file logcat.txt] [--follow]
"""
import subprocess, re, sys, argparse
from collections import defaultdict

def parse_logcat(lines):
    errors = defaultdict(int)
    crashes = []
    for line in lines:
        if 'FATAL' in line or 'CRASH' in line:
            crashes.append(line)
            pkg = re.search(r'(\S+\.\S+)', line)
            if pkg: errors[pkg.group(1)] += 1
        if 'ANR' in line or 'Application Not Responding' in line:
            errors['ANRs'] += 1
        if re.search(r'E\s+/\s+.*Exception', line):
            errors['Exceptions'] += 1
    return errors, crashes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='Read from logcat file instead of device')
    parser.add_argument('--follow', action='store_true', help='Stream live logcat')
    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            lines = f.readlines()
    elif args.follow:
        proc = subprocess.Popen('adb logcat', shell=True, stdout=subprocess.PIPE, text=True)
        print('🔴 Live logcat — looking for crashes/ANRs (Ctrl+C to stop)\n')
        lines = []
        try:
            for line in proc.stdout:
                lines.append(line)
                if 'CRASH' in line or 'ANR' in line or 'Exception' in line:
                    print(f'⚠️  {line.strip()[:80]}')
        except KeyboardInterrupt:
            proc.terminate()
        return
    else:
        # Live from device
        r = subprocess.run('adb logcat -d', shell=True, capture_output=True, text=True)
        lines = r.stdout.splitlines()

    errors, crashes = parse_logcat(lines)
    
    print('\n📊 Logcat Analysis')
    print('=' * 40)
    for error_type, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
        print(f'  {error_type}: {count}')
    if crashes:
        print(f'\n🚨 {len(crashes)} crash(es) found')
        for c in crashes[:5]:
            print(f'  {c.strip()[:70]}')

if __name__ == '__main__':
    main()
