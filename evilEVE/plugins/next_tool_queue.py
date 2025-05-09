# plugins/next_tool_queue.py

from collections import Counter

KEYWORD_TOOLS = {
    "ftp": ["hydra", "ftp_vsftpd"],
    "ssh": ["hydra"],
    "mysql": ["hydra", "sqlmap"],
    "http": ["sqlmap", "apache_struts"],
    "smb": ["metasploit", "samba_usermap", "EternalBlue"],
    "telnet": ["hydra"],
    "rdp": ["hydra"],
    "https": ["sqlmap", "nuclei"],
}

def extract_tools_from_services(open_ports: list) -> list:
    """
    Given a list of (port, service) tuples, return tools that match the services.
    """
    suggestions = []
    for _, service in open_ports:
        for keyword, tools in KEYWORD_TOOLS.items():
            if keyword in service.lower():
                suggestions.extend(tools)
    return suggestions

def rank_tool_suggestions(tools: list) -> list:
    """
    Rank suggestions by frequency (or future model-driven scoring).
    """
    if not tools:
        return []
    counts = Counter(tools)
    ranked = sorted(counts.items(), key=lambda x: -x[1])
    return [t[0] for t in ranked]

def queue_next_tools(attacker: dict, open_ports: list) -> list:
    """
    Full helper to generate and attach next_tool priority list.
    """
    raw_suggestions = extract_tools_from_services(open_ports)
    ranked = rank_tool_suggestions(raw_suggestions)
    attacker.setdefault("next_tools", []).extend(ranked)
    attacker["next_tools"] = list(dict.fromkeys(attacker["next_tools"]))  # deduplicate, keep order
    return ranked
