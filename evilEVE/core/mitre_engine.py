
# core/mitre_engine.py

import os
import time
import random
import json
from core.tool_executor import execute_tool
from core.reward_system import update_profile_feedback
from core.logger import log_attack
from core.memory_graph import update_memory_graph
from core.monitor_tools import monitor_active_tools
from core.plugin_errors import summarize_plugin_errors
from plugins.metasploit_plugin import run_msf_attack, parse_msf_log
from plugins.ghidra_plugin import GhidraHeadlessPlugin
from plugins.hydra_plugin import run_hydra_attack
from plugins.nmap_plugin import run_nmap_scan
from plugins.nmap_interpreter import interpret_nmap_json
from plugins.sqlmap_plugin import run_sqlmap_attack, parse_sqlmap_log
from plugins.curl_plugin import run_curl_check
from plugins.wget_plugin import run_wget_probe
from plugins.httpie_plugin import run_httpie_probe
from plugins import next_tool_queue

TOOLS_BY_SKILL = {
    0: [],
    1: ["curl", "wget"],
    2: ["httpie"],
    3: ["nmap", "sqlmap"],
    4: ["hydra"],
    5: ["metasploit", "ghidra"]
}

BIAS_TOOL_WEIGHTS = {
    "anchoring": {"nmap": 2.0, "sqlmap": 2.0, "hydra": 0.5, "ghidra": 1.0},
    "confirmation": {"hydra": 2.0, "sqlmap": 2.0, "nmap": 0.5},
    "overconfidence": {"metasploit": 3.0, "ghidra": 2.0, "httpie": 0.5}
}

BIAS_EXPLOITS = {
    "anchoring": ["ftp_vsftpd"],
    "confirmation": ["apache_struts"],
    "overconfidence": ["samba_usermap", "apache_struts"]
}

FOLLOWUP_LOG_PATH = os.path.expanduser("~/.evilEVE/logs/followups.jsonl")

def log_followup_suggestions(attacker_name, suggestions):
    if not suggestions:
        return
    os.makedirs(os.path.dirname(FOLLOWUP_LOG_PATH), exist_ok=True)
    entry = {
        "attacker": attacker_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "suggestions": suggestions
    }
    with open(FOLLOWUP_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def get_bias_activation_probs(deception_present: bool, informed: bool) -> dict:
    return {
        "anchoring": 0.85 if deception_present and not informed else 0.5,
        "confirmation": 0.75 if informed else 0.4,
        "overconfidence": 0.65 if informed and not deception_present else 0.3
    }

def weighted_random_choice(weight_dict):
    total = sum(weight_dict.values())
    r = random.uniform(0, total)
    upto = 0
    for k, w in weight_dict.items():
        if upto + w >= r:
            return k
        upto += w
    return random.choice(list(weight_dict.keys()))

def weighted_tool_choice(tools, bias):
    weights = []
    bias_weights = BIAS_TOOL_WEIGHTS.get(bias, {})
    for tool in tools:
        weights.append(bias_weights.get(tool, 1.0))
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for tool, weight in zip(tools, weights):
        if upto + weight >= r:
            return tool
        upto += weight
    return random.choice(tools)

def simulate_phase(attacker, phase, target_ip, queued_tool=None, dry_run=False):
    print(f"\n Phase: {phase}")

    tools = [t for lvl in range(attacker["skill"] + 1) for t in TOOLS_BY_SKILL[lvl]]
    if not tools:
        print("[!] No tools available due to low skill level.")
        return

    deception_present = attacker.get("deception_present", False)
    informed = attacker.get("informed_of_deception", False)
    bias_probs = get_bias_activation_probs(deception_present, informed)
    selected_bias = weighted_random_choice(bias_probs)
    attacker["last_selected_bias"] = selected_bias
    print(f" Cognitive Bias Activated: {selected_bias}")

    queued = attacker.get("next_tools", [])
    if queued:
        print(f"[next_tool_queue] Prioritized tool from queue: {queued[0]}")
    tool = queued.pop(0) if queued else queued_tool or weighted_tool_choice(tools, selected_bias)
    attacker["next_tools"] = queued

    args = [target_ip] if tool in ["nmap", "curl", "wget", "httpie"] else []
    bias_tool_reason = f"Tool selected using bias '{selected_bias}' weighted preference"
    print(f" Using tool: {tool} on {target_ip} → Reason: {bias_tool_reason}")

    active_tools = []
    start = time.time()
    result = {
        "tool": tool,
        "args": args,
        "bias": selected_bias,
        "tool_reason": bias_tool_reason,
        "start_time": start
    }

    if dry_run:
        result.update({"dry_run": True, "elapsed": 0.0})
        return result

    try:
        if tool == "curl":
            plugin_result = run_curl_check(target_ip)
        elif tool == "wget":
            plugin_result = run_wget_probe(target_ip)
        elif tool == "httpie":
            plugin_result = run_httpie_probe(target_ip)
        else:
            plugin_result = None

        if plugin_result:
            result.update(plugin_result)
            if "apache" in plugin_result.get("stdout", "").lower():
                attacker.setdefault("next_tools", []).append("sqlmap")
                result["log_warning"] = "Found HTTP server, enqueued sqlmap"

    except Exception as e:
        result.update({
            "launched": False, "stdout_snippet": "", "stderr_snippet": "",
            "deception_triggered": False, "monitored_status": "plugin",
            "exit_code": None, "log_warning": f"{tool} plugin failed: {e}",
            "plugin_errors": [str(e)]
        })

    update_profile_feedback(attacker, result, tool)
    update_memory_graph(attacker, phase, tool, result.get("success", False))
    log_attack(attacker, tool, target_ip, phase, result)

    result["elapsed"] = round(time.time() - start, 2)
    return result
