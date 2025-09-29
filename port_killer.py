"""
Simple Windows CLI tool to list processes using a given port and optionally kill them.
No external Python packages required — uses netstat and tasklist/taskkill built-ins.

Usage: python port_killer.py

Author: generated
"""
import re
import subprocess
import sys
import shlex
import os

NETSTAT_CMD = ["netstat", "-ano"]

RE_LINE = re.compile(r"^\s*(TCP|UDP)\s+(\S+)\s+(\S+)\s+(?:(\S+)\s+)?(\d+)\s*$")


def run_netstat():
    try:
        p = subprocess.run(NETSTAT_CMD, capture_output=True, text=True, check=True)
        return p.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print("Failed to run netstat:", e)
        return []


def parse_netstat_lines(lines, port):
    entries = []
    port_str = str(port)
    for ln in lines:
        m = RE_LINE.match(ln)
        if not m:
            continue
        proto, local, foreign, state, pid = m.groups()
        # local might be like 0.0.0.0:3306 or [::]:3306
        if local.endswith(':' + port_str) or local.lower().endswith(':' + port_str.lower()):
            entries.append({
                'proto': proto,
                'local': local,
                'foreign': foreign,
                'state': state or '',
                'pid': int(pid)
            })
    # Deduplicate by pid and preserve order
    seen = set()
    uniq = []
    for e in entries:
        if e['pid'] not in seen:
            seen.add(e['pid'])
            uniq.append(e)
    return uniq


def pid_to_name(pid):
    try:
        # Use tasklist to get image name for PID
        cmd = ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"]
        p = subprocess.run(cmd, capture_output=True, text=True, check=True)
        out = p.stdout.strip()
        if not out:
            return "<unknown>"
        # CSV: "Image Name","PID","Session Name","Session#","Mem Usage"
        # simple split by comma, remove surrounding quotes
        # But image name may have spaces, it's enclosed in quotes; parse by CSV rules minimally
        parts = [s.strip().strip('"') for s in out.split('","')]
        name = parts[0].strip('"') if parts else out
        return name
    except subprocess.CalledProcessError:
        return "<unknown>"


def kill_pid(pid):
    try:
        cmd = ["taskkill", "/PID", str(pid), "/F"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        success = p.returncode == 0
        return success, p.stdout + p.stderr
    except Exception as e:
        return False, str(e)


def clear_console():
    """Clear the terminal/console in a cross-platform way."""
    try:
        if sys.platform.startswith('win'):
            os.system('cls')
        else:
            os.system('clear')
    except Exception:
        # best-effort; ignore errors
        pass


def prompt_port():
    while True:
        val = input("Enter port number (or 'q' to quit): ").strip()
        if val.lower() in ('q', 'quit', 'exit'):
            return None
        if not val.isdigit():
            print("Please enter a numeric port (1-65535).")
            continue
        port = int(val)
        if 1 <= port <= 65535:
            return port
        print("Port out of range. Choose 1-65535.")


def display_entries(entries):
    if not entries:
        print("No processes found using that port.")
        return
    print("Processes using port:")
    print("Idx  PID     Image Name                 Proto  Local -> Foreign                 State")
    print("---  -----   -------------------------  -----  ----------------------------  -----")
    for i, e in enumerate(entries, 1):
        name = pid_to_name(e['pid'])
        print(f"{i:>3}  {e['pid']:<6}  {name:<25.25}  {e['proto']:<5}  {e['local']:<28}  {e['state']}")


def main_loop():
    print("Port inspector + killer (Windows). No external deps.")
    while True:
        port = prompt_port()
        if port is None:
            print("Bye.")
            break
        lines = run_netstat()
        entries = parse_netstat_lines(lines, port)
        if not entries:
            print(f"No process is listening on port {port}.")
            continue
        display_entries(entries)
        while True:
            choice = input("Enter index to kill, 'a' to kill all, 'r' to refresh, 'b' to go back: ").strip().lower()
            if choice == 'b':
                break
            if choice == 'r':
                lines = run_netstat()
                entries = parse_netstat_lines(lines, port)
                clear_console()
                display_entries(entries)
                continue
            if choice == 'a':
                for e in entries:
                    pid = e['pid']
                    confirm = input(f"Kill PID {pid} ({pid_to_name(pid)})? [y/N]: ").strip().lower()
                    if confirm == 'y':
                        ok, out = kill_pid(pid)
                        print(out)
                        if ok:
                            print(f"Killed PID {pid}")
                        else:
                            print(f"Failed to kill PID {pid}")
                # after attempting kills, refresh list
                lines = run_netstat()
                entries = parse_netstat_lines(lines, port)
                display_entries(entries)
                continue
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(entries):
                    pid = entries[idx-1]['pid']
                    name = pid_to_name(pid)
                    confirm = input(f"Kill PID {pid} ({name})? [y/N]: ").strip().lower()
                    if confirm == 'y':
                        ok, out = kill_pid(pid)
                        print(out)
                        if ok:
                            print(f"Killed PID {pid}")
                        else:
                            print(f"Failed to kill PID {pid}")
                        # refresh list
                        lines = run_netstat()
                        entries = parse_netstat_lines(lines, port)
                        display_entries(entries)
                    else:
                        print("Cancelled.")
                else:
                    print("Index out of range.")
                continue
            print("Unknown command.")


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nInterrupted. Bye.")
        sys.exit(0)
