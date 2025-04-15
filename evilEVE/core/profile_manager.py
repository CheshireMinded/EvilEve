import os
import json
import uuid
import random
from core.psychology import update_suspicion_and_utility

PROFILE_DIR = os.path.expanduser("~/.evilEVE/attackers")


def generate_attacker_profile(name, seed=None):
    if seed is not None:
        random.seed(seed)

    attacker_id = str(uuid.uuid4())

    initial = {
        "confidence": random.randint(0, 5),
        "frustration": random.randint(0, 5),
        "self_doubt": random.randint(0, 5),
        "confusion": random.randint(0, 5)
    }

    profile = {
        "id": attacker_id,
        "name": name,
        "initial_psychology": initial,
        "current_psychology": initial.copy(),
        "skill": random.randint(0, 5),
        "memory_graph": {},
        "tools_used": [],
        "failed_attempts": {},
        "metrics": {},
        "seed": seed
    }

    update_suspicion_and_utility(profile)
    return profile


def load_or_create_profile(name, seed=None, preserve_psych_baseline=True, initialize_skill=True):
    os.makedirs(PROFILE_DIR, exist_ok=True)
    path = os.path.join(PROFILE_DIR, f"{name}.json")

    if os.path.exists(path):
        with open(path) as f:
            profile = json.load(f)

        if preserve_psych_baseline:
            if "initial_psychology" in profile:
                profile["current_psychology"] = profile.get("current_psychology", profile["initial_psychology"].copy())

        if initialize_skill and "skill" not in profile:
            profile["skill"] = random.randint(0, 5)

        update_suspicion_and_utility(profile)
        return profile

    profile = generate_attacker_profile(name, seed)
    save_profile(profile, preserve_baseline=True)
    return profile


def save_profile(profile, preserve_baseline=True, adjust_skill=True):
    if adjust_skill:
        false_actions = profile.get("metrics", {}).get("false_actions", 0)
        time_wasted = profile.get("metrics", {}).get("time_wasted", 0)
        successes = len(profile.get("tools_used", []))

        total_uses = false_actions + (time_wasted // 2) + successes
        if total_uses > 0:
            success_ratio = successes / total_uses

            # Increase or decrease skill based on performance
            if success_ratio > 0.6 and profile["skill"] < 5:
                profile["skill"] += 1
            elif success_ratio < 0.2 and profile["skill"] > 0:
                profile["skill"] -= 1

    if preserve_baseline:
        if "initial_psychology" in profile and "current_psychology" in profile:
            for trait in profile["initial_psychology"]:
                # Just ensuring key consistency, not resetting it
                profile["initial_psychology"][trait] = profile["initial_psychology"][trait]

    path = os.path.join(PROFILE_DIR, f"{profile['name']}.json")
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)


