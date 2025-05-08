"""
EvilEVE: Human-like AI Attacker Simulation Framework
Main CLI Entry Point (modular version)
"""

import argparse
import time
from core import profile_manager, mitre_engine, logger, psychology
from core.tool_executor import execute_tool
from core.monitor_tools import monitor_active_tools

MITRE_PHASES = [
    "Reconnaissance", "Initial Access", "Execution",
    "Persistence", "Privilege Escalation", "Lateral Movement",
    "Collection", "Exfiltration", "Impact"
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Attacker name")
    parser.add_argument("--ip", required=True, help="Target IP address")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--phases", type=int, default=5, help="Number of MITRE phases to simulate")
    args = parser.parse_args()

    attacker = profile_manager.load_or_create_profile(
        args.name,
        args.seed,
        preserve_psych_baseline=True,
        initialize_skill=True
    )
    print(f"\nLoaded Attacker Profile for {attacker['name']} (Skill Level {attacker['skill']})")

    # Initialize tool tracking list
    active_tools = []

    for phase in MITRE_PHASES[:args.phases]:
        print(f"\nStarting Phase: {phase}")

        # Simulate hesitation based on self-doubt
        hesitation = attacker.get("current_psychology", {}).get("self_doubt", 0) * 0.2
        if hesitation:
            print(f"Hesitating... (delay: {hesitation:.1f}s due to self-doubt)")
            time.sleep(hesitation)

        # Execute tool in background
        tool = "hydra"  # Replace with your phase-to-tool mapping if needed
        args_list = ["-l", "root", "-P", "rockyou.txt", args.ip, "ssh"]
        result = execute_tool(tool, args_list)
        result["phase"] = phase

        if result.get("launched"):
            result["start_time"] = time.time()
            active_tools.append(result)

        # Optional: Check deception indicators in output
        stdout = result.get("stdout", "").lower()
        stderr = result.get("stderr", "").lower()
        deception_keywords = ["decoy", "honeypot", "fake", "bait", "trap"]
        result["deception_triggered"] = any(kw in stdout or kw in stderr for kw in deception_keywords)

        # Monitor background tools for status and update result
        monitored = monitor_active_tools(active_tools, timeout=60)
        for m in monitored:
            if m["pid"] == result.get("pid"):
                result["monitored_status"] = m["status"]
                result["exit_code"] = m["exit_code"]

        # Simulate MITRE phase (triggers reward system + memory update)
        mitre_result = mitre_engine.simulate_phase(attacker, phase, args.ip)
        result.update(mitre_result or {})

        # Apply cognitive drift and recalculate suspicion/utility
        psychology.apply_correlations(attacker)
        psychology.update_suspicion_and_utility(attacker)

        # Save psychological snapshot and CTQ row
        psychology.export_cognitive_state(attacker, attacker_name=args.name)
        psychology.append_ctq_csv(attacker, attacker_name=args.name, phase=phase)

        # Print phase summary
        traits = attacker.get("current_psychology", {})
        print(f"Psych - Confidence: {traits.get('confidence')} | Frustration: {traits.get('frustration')} | Self-doubt: {traits.get('self_doubt')} | Surprise: {traits.get('surprise')}")
        print(f"Suspicion: {attacker.get('suspicion')} | Utility: {attacker.get('utility')}")

    # Save final attacker profile
    profile_manager.save_profile(attacker, preserve_baseline=True, adjust_skill=True)

    # Export simulation summary logs
    logger.finalize_summary(attacker, args.phases)
    logger.export_summary_report(attacker, args.phases)

    print("\nSimulation complete. Logs and profile updated.")

if __name__ == "__main__":
    main()

