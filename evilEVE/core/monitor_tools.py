# core/monitor_tools.py

# core/monitor_tools.py

import os
import signal
import time

def is_running(pid):
    """Check if process is alive."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def poll_process(pid):
    """Get exit status if process has finished (non-blocking)."""
    try:
        _, status = os.waitpid(pid, os.WNOHANG)
        if status == 0:
            return None  # still running
        return os.WEXITSTATUS(status)
    except ChildProcessError:
        return None

def kill_process_group(pid):
    """Terminate entire process group."""
    try:
        os.killpg(pid, signal.SIGTERM)
        return True
    except Exception as e:
        print(f"[monitor] Failed to kill PID group {pid}: {e}")
        return False

def monitor_active_tools(active_tools, timeout=60):
    """
    Monitor running tools and update their state.
    Each entry must have: {pid, tool, start_time, ...}
    """
    now = time.time()
    completed = []

    for entry in list(active_tools):  # safe iteration
        pid = entry["pid"]
        tool = entry["tool"]
        start = entry.get("start_time", now)
        elapsed = now - start

        if not is_running(pid):
            exit_code = poll_process(pid)
            print(f"[monitor] {tool} (pid={pid}) finished. Exit code: {exit_code}")
            completed.append({**entry, "status": "finished", "exit_code": exit_code})
            active_tools.remove(entry)

        elif elapsed > timeout:
            print(f"[monitor] Killing {tool} (pid={pid}) after {elapsed:.1f}s")
            kill_process_group(pid)
            completed.append({**entry, "status": "killed", "exit_code": None})
            active_tools.remove(entry)

        else:
            print(f"[monitor] {tool} (pid={pid}) still running...")

    return completed

