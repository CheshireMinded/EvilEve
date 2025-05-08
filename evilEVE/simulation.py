"""
EvilEVE: Human-like AI Attacker Simulation Framework
Main CLI Entry Point (modular version)
"""

import argparse
import time
from core import profile_manager, mitre_engine, logger, psychology
from core.tool_executor import execute_tool
from core.monitor_tools import monitor_active_tools
from core.logger import log_phase_result_jsonl, log_tool_event_jsonl 

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

    active_tools = []

    for phase in MITRE_PHASES[:args.phases]:
        print(f"\nStarting Phase: {phase}")

        hesitation = attacker.get("current_psychology", {}).get("self_doubt", 0) * 0.2
        if hesitation:
            print(f"Hesitating... (delay: {hesitation:.1f}s due to self-doubt)")
            time.sleep(hesitation)

        tool = "hydra"
        args_list = ["-l", "root", "-P", "rockyou.txt", args.ip, "ssh"]
        result = execute_tool(tool, args_list)
        result["phase"] = phase
        start_time = time.time()

        if result.get("launched"):
            result["start_time"] = start_time
            active_tools.append(result)

        stdout = result.get("stdout", "").lower()
        stderr = result.get("stderr", "").lower()
        deception_keywords = ["decoy", "honeypot", "fake", "bait", "trap"]
        result["deception_triggered"] = any(kw in stdout or kw in stderr for kw in deception_keywords)

        monitored = monitor_active_tools(active_tools, timeout=60)

        for m in monitored:
            if m["pid"] == result.get("pid"):
                result["monitored_status"] = m["status"]
                result["exit_code"] = m["exit_code"]

                # Tool-level log
                log_tool_event_jsonl({
                    "attacker": attacker["name"],
                    "phase": phase,
                    "tool": m["tool"],
                    "args": m.get("args", []),
                    "pid": m["pid"],
                    "status": m["status"],
                    "exit_code": m["exit_code"],
                    "runtime": round(time.time() - m["start_time"], 2),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })

        mitre_result = mitre_engine.simulate_phase(attacker, phase, args.ip)
        result.update(mitre_result or {})

        psychology.apply_correlations(attacker)
        psychology.update_suspicion_and_utility(attacker)
        psychology.export_cognitive_state(attacker, attacker_name=args.name)
        psychology.append_ctq_csv(attacker, attacker_name=args.name, phase=phase)

        traits = attacker.get("current_psychology", {})
        psych_snapshot = {
            "confidence": traits.get("confidence"),
            "self_doubt": traits.get("self_doubt"),
            "confusion": traits.get("confusion"),
            "frustration": traits.get("frustration"),
            "surprise": traits.get("surprise"),
            "suspicion": attacker.get("suspicion"),
            "utility": attacker.get("utility"),
        }

        phase_result = {
            "attacker": attacker["name"],
            "phase": phase,
            "tool": result.get("tool"),
            "args": result.get("args"),
            "pid": result.get("pid"),
            "elapsed": result.get("elapsed"),
            "success": result.get("success"),
            "exit_code": result.get("exit_code"),
            "bias": result.get("bias"),
            "tool_reason": result.get("tool_reason"), 
            "deception_triggered": result.get("deception_triggered"),
            "monitored_status": result.get("monitored_status"),
            "psych_state": psych_snapshot
}

        log_phase_result_jsonl(attacker["name"], phase_result)

        print(f"Psych - Confidence: {traits.get('confidence')} | Frustration: {traits.get('frustration')} | Self-doubt: {traits.get('self_doubt')} | Surprise: {traits.get('surprise')}")
        print(f"Suspicion: {attacker.get('suspicion')} | Utility: {attacker.get('utility')}")

    profile_manager.save_profile(attacker, preserve_baseline=True, adjust_skill=True)
    logger.finalize_summary(attacker, args.phases)
    logger.export_summary_report(attacker, args.phases)
    print("\nSimulation complete. Logs and profile updated.")

if __name__ == "__main__":
    main()


