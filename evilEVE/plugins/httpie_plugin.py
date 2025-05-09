# plugins/httpie_plugin.py

import subprocess
import time
import os
from pathlib import Path

def run_httpie_probe(target_ip, log_dir="logs/httpie"):
    """
    Uses httpie to probe a web service.
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    output_file = os.path.join(log_dir, f"httpie_{target_ip}_{timestamp}.log")
    url = f"http://{target_ip}/"

    cmd = ["nohup", "http", "--timeout=5", url]

    try:
        with open(output_file, "w") as log:
            subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, preexec_fn=os.setpgrp)

        return {
            "tool": "httpie",
            "args": [url],
            "pid": None,
            "launched": True,
            "elapsed": 0.0,
            "stdout_snippet": "",
            "stderr_snippet": "",
            "deception_triggered": False,
            "monitored_status": "plugin",
            "exit_code": None,
            "log_warning": f"httpie launched (output: {output_file})"
        }
    except Exception as e:
        return {
            "tool": "httpie",
            "args": [url],
            "pid": None,
            "launched": False,
            "elapsed": 0.0,
            "stdout_snippet": "",
            "stderr_snippet": "",
            "deception_triggered": False,
            "monitored_status": "plugin",
            "exit_code": None,
            "log_warning": f"httpie plugin failed: {e}",
            "plugin_errors": [str(e)]
        }
