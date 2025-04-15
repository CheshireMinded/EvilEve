# core/mitre_engine.py
# Simulates MITRE ATT&CK phases with tool use

import random
import time
from core.tool_executor import execute_tool
from core.reward_system import update_profile_feedback
from core.logger import log_attack
from core.memory_graph import update_memory_graph

TOOLS_BY_SKILL = {
    0: [],
    1: ["curl", "wget"],
    2: ["httpie"],
    3: ["nmap", "sqlmap"],
    4: ["hydra"],
    5: ["metasploit", "ghidra"]
}

def simulate_phase(attacker, phase, target_ip):
    print(f"\n Phase: {phase}")
    tools = [t for lvl in range(attacker["skill"] + 1) for t in TOOLS_BY_SKILL[lvl]]
    if not tools:
        print("[!] No tools available due to low skill level.")
        return

    tool = random.choice(tools)
    print(f" Using tool: {tool} on {target_ip}")

    args = [target_ip] if tool in ["nmap", "curl", "wget", "httpie"] else []
    start = time.time()
    result = execute_tool(tool, args)
    elapsed = round(time.time() - start, 2)

    if random.random() < attacker["suspicion"]:
        attacker["metrics"]["time_wasted"] = attacker["metrics"].get("time_wasted", 0) + elapsed

    update_profile_feedback(attacker, result, tool)
    update_memory_graph(attacker, phase, tool, result["success"])
    log_attack(attacker, tool, target_ip, phase, result)

