from zazo.utils.persistence import load_json, save_json
import math

class Identity:
    def __init__(self):
        self.traits = load_json(
            "identity.json",
            {
                "empathy": 0.8,
                "risk": 0.4,
                "innovation": 0.7,
                "stability": 0.9
            }
        )

    def alignment_score(self, command_traits):
        dot = sum(
            self.traits.get(k, 0) * command_traits.get(k, 0)
            for k in command_traits
        )
        norm_a = math.sqrt(sum(v*v for v in self.traits.values()))
        norm_b = math.sqrt(sum(v*v for v in command_traits.values()))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

    def persist(self):
        save_json("identity.json", self.traits)