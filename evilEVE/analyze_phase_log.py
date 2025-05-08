# /analyze_phase_log.py

#!/usr/bin/env python3
"""
Analyze EvilEVE simulation results from a .jsonl phase log file.

Usage Examples:
  python3 analyze_phase_log.py --log logs/phase_runs/Eve_phases.jsonl
  python3 analyze_phase_log.py --log logs/phase_runs/Eve_phases.jsonl --export_csv summary.csv

This script prints phase summaries, tool usage, bias activations, and deception triggers.
"""

import argparse
import json
from collections import Counter
from pathlib import Path

def load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]

def summarize(log_data):
    phases = len(log_data)
    tools = [entry["tool"] for entry in log_data if entry.get("tool")]
    biases = [entry["bias"] for entry in log_data if entry.get("bias")]
    exit_codes = [entry["exit_code"] for entry in log_data if entry.get("exit_code") is not None]
    success_count = sum(1 for entry in log_data if entry.get("success") is True)
    failure_count = sum(1 for entry in log_data if entry.get("success") is False)
    deception_hits = sum(1 for entry in log_data if entry.get("deception_triggered"))
    monitored_status = Counter(entry.get("monitored_status", "unknown") for entry in log_data)

    print("\n📊 Phase Log Summary")
    print(f"- Total Phases Simulated: {phases}")
    print(f"- Successful Tools: {success_count}")
    print(f"- Failed Tools: {failure_count}")
    print(f"- Deception Triggers: {deception_hits}")
    print(f"- Unique Tools Used: {len(set(tools))}")
    print(f"- Biases Activated: {Counter(biases)}")
    print(f"- Tool Frequency: {Counter(tools)}")
    print(f"- Exit Code Distribution: {Counter(exit_codes)}")
    print(f"- Monitor Status: {dict(monitored_status)}")

def save_csv(log_data, out_path):
    import csv
    keys = [
        "attacker", "phase", "tool", "args", "pid", "elapsed", "success",
        "exit_code", "bias", "deception_triggered", "monitored_status"
    ]
    with open(out_path, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in log_data:
            writer.writerow({k: row.get(k, "") for k in keys})
    print(f"\n✅ CSV exported to: {out_path}")

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--log", required=True, help="Path to attacker phase .jsonl log file.")
    parser.add_argument("--export_csv", help="Optional path to export summary as a CSV file.")

    args = parser.parse_args()

    path = Path(args.log)
    if not path.exists():
        print(f"[!] Log file not found: {path}")
        return

    log_data = load_jsonl(path)
    if not log_data:
        print("[!] Log is empty.")
        return

    summarize(log_data)

    if args.export_csv:
        save_csv(log_data, args.export_csv)

if __name__ == "__main__":
    main()
