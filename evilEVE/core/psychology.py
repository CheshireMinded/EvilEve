# core/psychology.py
# Handles suspicion, stress, utility calculations

def update_suspicion_and_utility(profile):
    traits = profile.get("current_psychology", {})

    profile["suspicion"] = round((
        traits.get("frustration", 2.5) * 0.25 +
        traits.get("confusion", 2.5) * 0.25 +
        traits.get("self_doubt", 2.5) * 0.25 +
        (5 - traits.get("confidence", 2.5)) * 0.25
    ) / 5, 2)

    profile["utility"] = round(
        traits.get("confidence", 2.5) - profile.get("perceived_risk", 2.5), 2
    )



