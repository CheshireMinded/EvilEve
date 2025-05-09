# plugins/curl_plugin.py

"""
Plugin to run curl requests and parse output for useful indicators
of web services, deception, and follow-up tool suggestions.
"""

import os
import time
import subprocess
from pathlib import Path

def run_curl_probe(target_url, output_dir="logs/curl"):
    """
    Executes a curl HEAD request and parses headers.

    Args:
        target_url (str): Full target URL (e.g., http://192.168.1.100)
        output_dir (str): Directory to store curl logs

    Returns:
        dict: Metadata and parsed header info
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    log_path = os.path.join(output_dir, f"curl_{timestamp}.log")

    cmd = ["curl", "-I", "--max-time", "5", target_url]

    result = {
        "tool": "curl",
        "target": target_url,
        "log": log_path,
        "timestamp": timestamp,
        "headers": {},
        "suggestions": [],
        "deception_flags": [],
        "launched": False,
        "error": None
    }

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
        result["launched"] = True

        # Save to log file
        with open(log_path, "w") as f:
            f.write(proc.stdout)
            f.write(proc.stderr)

        for line in proc.stdout.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                result["headers"][k.strip().lower()] = v.strip()

        # Basic deception heuristics
        banner = result["headers"].get("server", "").lower()
        if any(x in banner for x in ["honeypot", "decoy", "snare"]):
            result["deception_flags"].append("server-banner-deception")

        # Suggest follow-ups
        if "apache" in banner or "nginx" in banner:
            result["suggestions"].append("sqlmap")
        if "iis" in banner:
            result["suggestions"].append("hydra")

    except Exception as e:
        result["error"] = str(e)

    return result


# Test Hook
if __name__ == "__main__":
    test = run_curl_probe("http://testphp.vulnweb.com")
    print(test)
