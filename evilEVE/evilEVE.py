"""
EvilEVE: Human-like AI Attacker Simulation Framework
Main CLI Entry Point (modular version)
"""

import argparse
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

    attacker = profile_manager.load_or_create_profile(args.name, args.seed)
    print(f"\n Loaded Attacker Profile for {attacker['name']} (Skill Level {attacker['skill']})")

    for phase in MITRE_PHASES[:args.phases]:
        mitre_engine.simulate_phase(attacker, phase, args.ip)

    profile_manager.save_profile(attacker)
    logger.finalize_summary(attacker, args.phases)
    print("\n Simulation complete. Logs and profile updated.")

if __name__ == "__main__":
    main()

