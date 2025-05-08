# core/mitre_engine.py
# Simulates MITRE ATT&CK phases with tool use and bias-based plugin selection

import random
import time
from core.tool_executor import execute_tool
from core.reward_system import update_profile_feedback
from core.logger import log_attack
from core.memory_graph import update_memory_graph

# Optional: import plugin_manager if you have a modular plugin system
# from core.plugin_manager import select_plugin

TOOLS_BY_SKILL = {
    0: [],
    1: ["curl", "wget"],
    2: ["httpie"],
    3: ["nmap", "sqlmap"],
    4: ["hydra"],
    5: ["metasploit", "ghidra"]
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
    return random.choice(list(weight_dict.keys()))  # fallback

def simulate_phase(attacker, phase, target_ip):
    print(f"\n Phase: {phase}")
    tools = [t for lvl in range(attacker["skill"] + 1) for t in TOOLS_BY_SKILL[lvl]]
    if not tools:
        print("[!] No tools available due to low skill level.")
        return

    # Select tool randomly from available pool
    tool = random.choice(tools)
    print(f" Using tool: {tool} on {target_ip}")

    args = [target_ip] if tool in ["nmap", "curl", "wget", "httpie"] else []
    start = time.time()
    result = execute_tool(tool, args)
    elapsed = round(time.time() - start, 2)

    # Track time wasted if suspicion is high
    if random.random() < attacker["suspicion"]:
        attacker["metrics"]["time_wasted"] = attacker["metrics"].get("time_wasted", 0) + elapsed

    # === NEW: Bias Activation Probability ===
    deception_present = attacker.get("deception_present", False)
    informed = attacker.get("informed_of_deception", False)

    bias_probs = get_bias_activation_probs(deception_present, informed)
    selected_bias = weighted_random_choice(bias_probs)
    attacker["last_selected_bias"] = selected_bias  # For analysis/logging

    print(f" Cognitive Bias Activated: {selected_bias}")

    # === Placeholder: Call plugin logic for selected bias ===
    # plugin = select_plugin(bias=selected_bias)
    # plugin.run(attacker=attacker, target_ip=target_ip)

    # Update state tracking
    update_profile_feedback(attacker, result, tool)
    update_memory_graph(attacker, phase, tool, result["success"])
    log_attack(attacker, tool, target_ip, phase, result)

    return {
        "tool": tool,
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "success": result.get("success", False),
        "elapsed": elapsed,
        "bias": selected_bias
    }
