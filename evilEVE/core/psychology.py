# core/psychology.py

import json
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class CognitiveState:
    confidence: float
    self_doubt: float
    confusion: float
    frustration: float
    suspicion: float
    utility: float

def update_suspicion_and_utility(profile):
    traits = profile.get("current_psychology", {})

    # Default values are mid-scale (1–5 Likert)
    frustration = traits.get("frustration", 2.5)
    confusion = traits.get("confusion", 2.5)
    self_doubt = traits.get("self_doubt", 2.5)
    confidence = traits.get("confidence", 2.5)

    # Tularosa-style weighted suspicion model
    suspicion = round((
        0.3 * frustration +
        0.3 * confusion +
        0.2 * self_doubt +
        0.2 * (5 - confidence)  # inverse confidence
    ), 2)

    # Utility = confidence minus perceived risk
    perceived_risk = profile.get("perceived_risk", 2.5)
    utility = round(confidence - perceived_risk, 2)

    # Store in profile
    profile["suspicion"] = suspicion
    profile["utility"] = utility

    # Update internal state object for optional export
    profile["current_state_obj"] = CognitiveState(
        confidence=confidence,
        self_doubt=self_doubt,
        confusion=confusion,
        frustration=frustration,
        suspicion=suspicion,
        utility=utility,
    )

def export_cognitive_state(profile, attacker_name="attacker", out_dir="logs/cognitive_states"):
    """
    Exports current cognitive state to a JSON file.
    """
    state_obj = profile.get("current_state_obj", None)
    if not state_obj:
        return

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    out_path = Path(out_dir) / f"{attacker_name}_state.json"
    with open(out_path, "w") as f:
        json.dump(asdict(state_obj), f, indent=2)
