import os
from datetime import datetime
from collections import Counter

LOG_FILE = os.path.expanduser("~/.evilEVE/logs/attack_log.csv")

def log_attack(attacker, tool, target_ip, phase, result):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    traits = attacker.get("current_psychology", {})
    
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()},{attacker['id']},{attacker['name']},{tool},{target_ip},{phase},"
                f"{result['success']},{attacker.get('suspicion', 0)},{traits.get('confidence', 0)},"
                f"{traits.get('frustration', 0)},{traits.get('self_doubt', 0)},{result['exit_code']}\n")


def finalize_summary(attacker, num_phases=0):
    traits = attacker.get("current_psychology", {})
    print("\nSummary of Simulation:")
    print(f"   Phases simulated: {num_phases}")
    print(f"   Tools used: {attacker.get('tools_used', [])}")
    print(f"   Time wasted: {attacker.get('metrics', {}).get('time_wasted', 0)} seconds")
    print(f"   Failed attempts: {sum(attacker.get('failed_attempts', {}).values())}")
    print(f"   Confidence: {traits.get('confidence', 'N/A')}")
    print(f"   Frustration: {traits.get('frustration', 'N/A')}")
    print(f"   Self-doubt: {traits.get('self_doubt', 'N/A')}")
    print(f"   Suspicion: {attacker.get('suspicion', 'N/A')}")


def export_summary_report(attacker, num_phases):
    name = attacker["name"]
    report_dir = os.path.expanduser("~/.evilEVE/reports")
    os.makedirs(report_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_summary_{timestamp}.md"
    filepath = os.path.join(report_dir, filename)

    traits = attacker.get("current_psychology", {})
    metrics = attacker.get("metrics", {})
    tools_used = attacker.get("tools_used", [])
    tool_counts = Counter(tools_used)
    skill = attacker.get("skill", "?")

    with open(filepath, "w") as f:
        f.write(f"# EvilEVE Summary Report: {name}\n")
        f.write(f"**Date:** {timestamp}\n")
        f.write(f"**MITRE Phases Simulated:** {num_phases}\n\n")
        
        f.write("## Final Psychological Profile\n")
        for trait, value in traits.items():
            f.write(f"- **{trait.capitalize()}**: {value}\n")
        f.write(f"- **Suspicion**: {attacker.get('suspicion', '?')}\n")
        f.write(f"- **Skill Level**: {skill}\n\n")

        f.write("## Performance Summary\n")
        f.write(f"- **Total Tools Used**: {len(tools_used)}\n")
        f.write(f"- **Time Wasted**: {metrics.get('time_wasted', 0)} seconds\n")
        f.write(f"- **Failed Attempts**: {metrics.get('false_actions', 0)}\n\n")

        f.write("## Tool Usage Frequency\n")
        if tool_counts:
            for tool, count in tool_counts.most_common():
                f.write(f"- {tool}: {count} use(s)\n")
        else:
            f.write("No tools used.\n")

    print(f"📄 Summary report written to: {filepath}")

