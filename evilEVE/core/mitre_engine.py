# core/mitre_engine.py

import os
import time
import random
from core.tool_executor import execute_tool
from core.reward_system import update_profile_feedback
from core.logger import log_attack
from core.memory_graph import update_memory_graph
from core.monitor_tools import monitor_active_tools
from plugins.metasploit_plugin import run_msf_attack, parse_msf_log
from plugins.ghidra_plugin import GhidraHeadlessPlugin
from plugins.hydra_plugin import run_hydra_attack
from plugins.nmap_plugin import run_nmap_scan  # ← NEW

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

def simulate_phase(attacker, phase, target_ip):
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

    tool = weighted_tool_choice(tools, selected_bias)
    args = [target_ip] if tool in ["nmap", "curl", "wget", "httpie"] else []
    bias_tool_reason = f"Tool selected using bias '{selected_bias}' weighted preference"
    print(f" Using tool: {tool} on {target_ip} → Reason: {bias_tool_reason}")

    active_tools = []
    start = time.time()
    result = {}

    if tool == "metasploit":
        exploit_name = random.choice(BIAS_EXPLOITS.get(selected_bias, ["ftp_vsftpd"]))
        plugin_result = run_msf_attack(target_ip=target_ip, exploit_name=exploit_name)
        time.sleep(3)
        outcome = parse_msf_log(plugin_result["log"])
        result.update({
            "tool": tool, "args": [target_ip], "pid": None, "launched": False,
            "elapsed": 0.0, "stdout_snippet": "", "stderr_snippet": "",
            "deception_triggered": False, "monitored_status": "plugin", "exit_code": None,
            "bias": selected_bias, "tool_reason": bias_tool_reason,
            "log_warning": f"Metasploit launched (rc: {plugin_result['script']})",
            "exploit_success": outcome["session_opened"], "plugin_errors": outcome["errors"]
        })

    elif tool == "ghidra":
        ghidra_path = "/home/student/tools/ghidra_11.3.2_PUBLIC"
        binary_path = "/home/student/binaries/malware.exe"
        project_path = f"/home/student/ghidra-projects/{attacker['name']}"
        log_path = f"/home/student/logs/ghidra_{attacker['name']}.log"

        plugin = GhidraHeadlessPlugin(
            ghidra_path=ghidra_path,
            binary_path=binary_path,
            project_path=project_path,
            log_path=log_path
        )
        plugin.run()
        result.update({
            "tool": tool, "args": [binary_path], "pid": None, "launched": False,
            "elapsed": 0.0, "stdout_snippet": "", "stderr_snippet": "",
            "deception_triggered": False, "monitored_status": "plugin", "exit_code": None,
            "bias": selected_bias, "tool_reason": bias_tool_reason,
            "log_warning": f"Ghidra launched in background (project: {project_path})"
        })

    elif tool == "hydra":
        plugin_result = run_hydra_attack(target_ip, service="ssh")
        result.update({
            "tool": tool, "args": [target_ip], "pid": None, "launched": False,
            "elapsed": 0.0, "stdout_snippet": "", "stderr_snippet": "",
            "deception_triggered": False, "monitored_status": "plugin", "exit_code": None,
            "bias": selected_bias, "tool_reason": bias_tool_reason,
            "log_warning": f"Hydra launched against {target_ip} (log: {plugin_result['log']})"
        })

    elif tool == "nmap":
        plugin_result = run_nmap_scan(target_ip, log_dir=f"logs/nmap/{attacker['name']}")
        result.update({
            "tool": tool, "args": [target_ip], "pid": None, "launched": False,
            "elapsed": 0.0, "stdout_snippet": "", "stderr_snippet": "",
            "deception_triggered": plugin_result.get("deception_detected", False),
            "monitored_status": "plugin", "exit_code": None,
            "bias": selected_bias, "tool_reason": bias_tool_reason,
            "log_warning": f"Nmap scan completed. Deception: {plugin_result.get('deception_detected')}",
            "open_ports": plugin_result.get("open_ports", []),
            "traits": plugin_result.get("traits", {})
        })

    else:
        try:
            result = execute_tool(tool, args)
        except Exception as e:
            result = {
                "success": False, "stdout": "", "stderr": str(e), "exit_code": -1,
                "log_warning": f"Exception while executing tool '{tool}': {e}"
            }

        result.update({
            "phase": phase, "tool": tool, "args": args, "bias": selected_bias,
            "tool_reason": bias_tool_reason
        })

        if result.get("launched"):
            result["start_time"] = start
            active_tools.append(result)

        try:
            stdout = result.get("stdout", "").lower()
            stderr = result.get("stderr", "").lower()
            result["stdout_snippet"] = stdout[:1000]
            result["stderr_snippet"] = stderr[:1000]
            result["deception_triggered"] = any(
                kw in stdout or kw in stderr for kw in ["decoy", "honeypot", "fake", "bait", "trap"]
            )
        except Exception as e:
            result["deception_triggered"] = False
            result["stdout_snippet"] = ""
            result["stderr_snippet"] = ""
            result["log_warning"] = f"Error parsing output: {str(e)}"

        if result.get("deception_triggered"):
            print(" [!] Deception suspected from output.")

        monitored = monitor_active_tools(active_tools, timeout=60)
        for m in monitored:
            if m["pid"] == result.get("pid"):
                result["monitored_status"] = m["status"]
                result["exit_code"] = m["exit_code"]

    update_profile_feedback(attacker, result, tool)
    update_memory_graph(attacker, phase, tool, result.get("success", False))
    log_attack(attacker, tool, target_ip, phase, result)

    result["elapsed"] = round(time.time() - start, 2)
    return result



