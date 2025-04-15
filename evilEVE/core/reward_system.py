# core/reward_system.py
from core.psychology import update_suspicion_and_utility

def update_profile_feedback(profile, result, tool):
    psych = profile["current_psychology"]

    if result["success"]:
        psych["confidence"] = min(5, psych.get("confidence", 2) + 1)
        profile["tools_used"].append(tool)
    else:
        psych["frustration"] = min(5, psych.get("frustration", 2) + 1)
        psych["self_doubt"] = min(5, psych.get("self_doubt", 2) + 1)
        profile["failed_attempts"].setdefault(tool, 0)
        profile["failed_attempts"][tool] += 1

    update_suspicion_and_utility(profile)

