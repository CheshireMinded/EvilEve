# core/monitor_tools.py

import os
import signal
import time

def is_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def poll_process(pid):
    try:
        _, status = os.waitpid(pid, os.WNOHANG)
        if status == 0:
            return None  # still running
        return os.WEXITSTATUS(status)
    except ChildProcessError:
        return None  # already finished or invalid PID

def kill_process_group(pid):
    try:
        os.killpg(pid, signal.SIGTERM)
        return True
    except Exception as e:
        print(f"[monitor] Failed to kill PID group {pid}: {e}")
        return False

def monitor_active_tools(active_tools, timeout=60):
    now = time.time()
    completed = []

    for entry in active_tools:
        pid = entry["pid"]
        tool = entry["tool"]
        start = entry.get("start_time", now)
        elapsed = now - start

        if not is_running(pid):
            exit_code = poll_process(pid)
            print(f"[monitor] {tool} (pid={pid}) finished. Exit code: {exit_code}")
            completed.append({**entry, "status": "finished", "exit_code": exit_code})
        elif elapsed > timeout:
            print(f"[monitor] Killing {tool} (pid={pid}) after {elapsed:.1f}s")
            kill_process_group(pid)
            completed.append({**entry, "status": "killed", "exit_code": None})
        else:
            print(f"[monitor] {tool} (pid={pid}) still running...")
    return completed
