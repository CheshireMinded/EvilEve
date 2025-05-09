# plugins/sqlmap_plugin.py

import os
import subprocess
import time
from pathlib import Path

def run_sqlmap_attack(target_url, output_dir="logs/sqlmap", dry_run=False):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    log_file = os.path.join(output_dir, f"sqlmap_{timestamp}.log")

    cmd = [
        "nohup", "sqlmap", "-u", target_url,
        "--batch", "--random-agent", "--threads=3", "--dbs"
    ]

    if dry_run:
        print(f"[sqlmap_plugin] [dry-run] Would run: {' '.join(cmd)}")
        return {"dry_run": True, "cmd": cmd}

    print(f"[sqlmap_plugin] Running sqlmap on {target_url}")
    subprocess.Popen(
        cmd,
        stdout=open(log_file, "w"),
        stderr=subprocess.STDOUT,
        preexec_fn=os.setpgrp
    )

    return {
        "tool": "sqlmap",
        "target_url": target_url,
        "log_path": log_file,
        "timestamp": timestamp
    }
