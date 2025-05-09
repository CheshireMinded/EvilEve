# plugins/sqlmap_plugin.py

"""
SQLMap Plugin for EvilEVE Attacker Framework

Launches SQLMap in background against a given target URL.
Logs output and returns metadata for later analysis.
"""

import os
import time
import subprocess
from pathlib import Path


def run_sqlmap_attack(target_url, output_dir="logs/sqlmap", level=1):
    """
    Launches a SQLMap scan in background using nohup.

    Args:
        target_url (str): The target URL to scan (e.g., http://example.com/index.php?id=1).
        output_dir (str): Directory where logs will be stored.
        level (int): Intensity level (1–5) for SQLMap scan.

    Returns:
        dict: Metadata about the launched scan, including log file and timestamp.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    log_path = os.path.join(output_dir, f"sqlmap_{timestamp}.log")

    cmd = [
        "nohup", "sqlmap",
        "-u", target_url,
        "--batch",
        "--level", str(level),
        "--risk", "1",
        "--random-agent",
        "--output-dir", output_dir
    ]

    result = {
        "tool": "sqlmap",
        "target": target_url,
        "log": log_path,
        "timestamp": timestamp,
        "launched": False,
        "error": None
    }

    try:
        with open(log_path, "w") as logfile:
            subprocess.Popen(
                cmd,
                stdout=logfile,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setpgrp
            )
        result["launched"] = True
        print(f"[sqlmap_plugin] SQLMap launched for: {target_url}")
    except Exception as e:
        result["error"] = str(e)
        print(f"[sqlmap_plugin] Launch failed: {e}")

    return result


# Optional CLI test runner
if __name__ == "__main__":
    test_url = "http://testphp.vulnweb.com/artists.php?artist=1"
    print(run_sqlmap_attack(test_url))
