import json
from pathlib import Path

PORT_CVE_MAP = {
    21: "FTP service — suggest brute force or vsftpd exploit",
    22: "SSH detected — suggest Hydra with SSH or banner fingerprinting",
    80: "HTTP open — run sqlmap or look for default web pages",
    139: "NetBIOS/SMB — suggest EternalBlue or Samba exploits",
    445: "SMB — suggest MS17-010 (EternalBlue)",
    3306: "MySQL open — consider sqlmap or password spraying",
    8080: "Alternate HTTP — check for Apache Struts CVE"
}

def interpret_nmap_json(nmap_json_path):
    if not Path(nmap_json_path).exists():
        return {"error": "Nmap scan output not found."}

    try:
        with open(nmap_json_path) as f:
            data = json.load(f)
    except Exception as e:
        return {"error": f"Failed to parse Nmap JSON: {e}"}

    results = {
        "total_ports": 0,
        "suggestions": [],
        "deception_flags": []
    }

    open_ports = data.get("ports", [])
    results["total_ports"] = len(open_ports)

    if len(open_ports) <= 2:
        results["deception_flags"].append("Unusually low number of open ports — possible honeypot")

    for port_entry in open_ports:
        port = port_entry.get("portid")
        service = port_entry.get("service", {}).get("name", "unknown")

        try:
            port = int(port)
        except:
            continue

        suggestion = PORT_CVE_MAP.get(port)
        if suggestion:
            results["suggestions"].append(f"Port {port}/{service}: {suggestion}")

    return results

# Optional test
if __name__ == "__main__":
    path = "logs/nmap_results/nmap_10.0.0.81.json"
    outcome = interpret_nmap_json(path)
    print(json.dumps(outcome, indent=2))
