# core/reward_system.py

from core.psychology import update_suspicion_and_utility

def update_profile_feedback(profile, result, tool):
    psych = profile["current_psychology"]

    # Initialize default values
    for k in ["confidence", "frustration", "self_doubt", "confusion", "surprise"]:
        psych[k] = psych.get(k, 2.5)

    success = result.get("success", False)
    deception = result.get("deception_triggered", False)

    if success:
        # Reward success with positive reinforcement
        psych["confidence"] = min(5.0, psych["confidence"] + 0.5)
        psych["frustration"] = max(0.0, psych["frustration"] - 0.3)
        psych["self_doubt"] = max(0.0, psych["self_doubt"] - 0.2)
        psych["surprise"] = max(0.0, psych["surprise"] - 0.2)
        profile["tools_used"].append(tool)

    else:
        # Penalize failure
        psych["confidence"] = max(0.0, psych["confidence"] - 0.4)
        psych["frustration"] = min(5.0, psych["frustration"] + 0.6)
        psych["self_doubt"] = min(5.0, psych["self_doubt"] + 0.4)
        psych["surprise"] = min(5.0, psych["surprise"] + 0.3)

        # Track failed attempts
        profile["failed_attempts"].setdefault(tool, 0)
        profile["failed_attempts"][tool] += 1

        if deception:
            psych["confusion"] = min(5.0, psych["confusion"] + 0.5)
            psych["surprise"] = min(5.0, psych["surprise"] + 0.6)

    # Optional: amplify frustration if cumulative time wasted is high
    wasted = profile.get("metrics", {}).get("time_wasted", 0)
    if wasted > 30:  # total wasted seconds
        psych["frustration"] = min(5.0, psych["frustration"] + 0.2)
        psych["confidence"] = max(0.0, psych["confidence"] - 0.1)

    # Recalculate suspicion and utility using updated state
    update_suspicion_and_utility(profile)
