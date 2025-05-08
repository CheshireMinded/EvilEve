# core/reward_system.py

from core.psychology import update_suspicion_and_utility

def update_profile_feedback(profile, result, tool):
    psych = profile["current_psychology"]

    # Initialize defaults
    for k in ["confidence", "frustration", "self_doubt", "confusion", "surprise"]:
        psych[k] = psych.get(k, 2.5)

    # Determine if this was a decoy hit (if result is empty or deception-related)
    is_deception = result.get("deception_triggered", False) or "decoy" in result.get("stdout", "").lower()

    if result["success"]:
        psych["confidence"] = min(5.0, psych["confidence"] + 0.5)
        psych["frustration"] = max(0.0, psych["frustration"] - 0.3)
        psych["self_doubt"] = max(0.0, psych["self_doubt"] - 0.2)
        profile["tools_used"].append(tool)

    else:
        psych["frustration"] = min(5.0, psych["frustration"] + 0.6)
        psych["self_doubt"] = min(5.0, psych["self_doubt"] + 0.4)
        psych["confidence"] = max(0.0, psych["confidence"] - 0.3)

        # Track tool-specific failures
        profile["failed_attempts"].setdefault(tool, 0)
        profile["failed_attempts"][tool] += 1

        if is_deception:
            psych["confusion"] = min(5.0, psych["confusion"] + 0.5)
            psych["surprise"] = min(5.0, psych["surprise"] + 0.6)
        else:
            psych["surprise"] = min(5.0, psych["surprise"] + 0.3)

    # Update suspicion and utility based on adjusted traits
    update_suspicion_and_utility(profile)


