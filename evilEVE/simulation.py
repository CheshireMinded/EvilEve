"""
EvilEVE: Human-like AI Attacker Simulation Framework
Main CLI Entry Point (modular version)
"""

import argparse
import time
from core import profile_manager, mitre_engine, logger

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

    # Load or create attacker profile while ensuring psychological traits and skill level are generated only once
    attacker = profile_manager.load_or_create_profile(
        args.name,
        args.seed,
        preserve_psych_baseline=True,
        initialize_skill=True
    )
    print(f"\nLoaded Attacker Profile for {attacker['name']} (Skill Level {attacker['skill']})")

    for phase in MITRE_PHASES[:args.phases]:
        print(f"\nStarting Phase: {phase}")

        # Hesitation simulation based on psychological state
        hesitation = attacker.get("current_psychology", {}).get("self_doubt", 0) * 0.2
        if hesitation:
            print(f"Hesitating... (delay: {hesitation:.1f}s due to self-doubt)")
            time.sleep(hesitation)

        # Simulate the phase and get tool result
        result = mitre_engine.simulate_phase(attacker, phase, args.ip)

        # Show tool output if available
        if result:
            print("---- STDOUT ----")
            print(result['stdout'][:300] or "[empty]")
            print("---- STDERR ----")
            print(result['stderr'][:300] or "[empty]")
            print(f"Elapsed: {result.get('elapsed', '?')}s | Success: {result['success']}")

        # Print updated psychology
        traits = attacker.get("current_psychology", {})
        print(f"Psych - Confidence: {traits.get('confidence')} | Frustration: {traits.get('frustration')} | Self-doubt: {traits.get('self_doubt')}")
        print(f"Suspicion: {attacker.get('suspicion')}")

    # Save current psychological state and skill level, adjusting skill based on performance if applicable
    profile_manager.save_profile(attacker, preserve_baseline=True, adjust_skill=True)

    # Generate both console and external summary output (e.g., .csv/.md reports)
    logger.finalize_summary(attacker, args.phases)
    logger.export_summary_report(attacker, args.phases)

    print("\nSimulation complete. Logs and profile updated.")

if __name__ == "__main__":
    main()

