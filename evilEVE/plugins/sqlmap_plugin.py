# plugins/sqlmap_plugin.py

import os
import time
import subprocess
from pathlib import Path

def run_sqlmap_attack(target_url, output_dir="logs/sqlmap", level=1):
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

    with open(log_path, "w") as logfile:
        subprocess.Popen(
            cmd,
            stdout=logfile,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setpgrp
        )

    return {
        "tool": "sqlmap",
        "target": target_url,
        "log": log_path,
        "timestamp": timestamp
    }
