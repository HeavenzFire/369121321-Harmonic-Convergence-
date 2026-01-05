# LEGION ∞.0: Universal Verification Contexts Configuration
# 10+ domains with coherence thresholds and daily limits

VERIFICATION_CONTEXTS = {
    "child_safety": {
        "daily_limit": 240,
        "coherence_threshold": 0.92,
        "description": "Child safety pattern verification",
        "premium_multiplier": 1.5,
        "economic_value": 15.0  # $/verification
    },
    "food_safety": {
        "daily_limit": 1000,
        "coherence_threshold": 0.95,
        "description": "Food safety and contamination verification",
        "premium_multiplier": 1.8,
        "economic_value": 25.0
    },
    "medical_records": {
        "daily_limit": 50,
        "coherence_threshold": 0.98,
        "description": "Medical record and treatment verification",
        "premium_multiplier": 2.0,
        "economic_value": 40.0
    },
    "elections": {
        "daily_limit": 10,
        "coherence_threshold": 0.99,
        "description": "Election integrity and vote verification",
        "premium_multiplier": 3.0,
        "economic_value": 300.0
    },
    "science": {
        "daily_limit": 100,
        "coherence_threshold": 0.97,
        "description": "Scientific experiment reproducibility",
        "premium_multiplier": 2.2,
        "economic_value": 50.0
    },
    "supply_chain": {
        "daily_limit": 5000,
        "coherence_threshold": 0.94,
        "description": "Supply chain authenticity and safety",
        "premium_multiplier": 1.6,
        "economic_value": 20.0
    },
    "climate": {
        "daily_limit": 200,
        "coherence_threshold": 0.96,
        "description": "Climate data and environmental verification",
        "premium_multiplier": 1.9,
        "economic_value": 30.0
    },
    "finance": {
        "daily_limit": 100,
        "coherence_threshold": 0.97,
        "description": "Financial transaction and audit verification",
        "premium_multiplier": 4.0,
        "economic_value": 100.0
    },
    "education": {
        "daily_limit": 500,
        "coherence_threshold": 0.93,
        "description": "Educational credential and content verification",
        "premium_multiplier": 1.4,
        "economic_value": 12.0
    },
    "justice": {
        "daily_limit": 25,
        "coherence_threshold": 0.98,
        "description": "Legal document and evidence verification",
        "premium_multiplier": 2.5,
        "economic_value": 75.0
    }
}

class VerificationContextManager:
    """Manages verification contexts and their configurations"""

    def __init__(self):
        self.contexts = VERIFICATION_CONTEXTS.copy()
        self.active_contexts = set(self.contexts.keys())

    def get_context(self, context_name: str) -> dict:
        """Get configuration for a specific context"""
        return self.contexts.get(context_name, {})

    def get_all_active(self) -> dict:
        """Get all active verification contexts"""
        return {k: v for k, v in self.contexts.items() if k in self.active_contexts}

    def activate_context(self, context_name: str):
        """Activate a verification context"""
        if context_name in self.contexts:
            self.active_contexts.add(context_name)
            print(f"✅ ACTIVATED: {context_name} verification")

    def deactivate_context(self, context_name: str):
        """Deactivate a verification context"""
        if context_name in self.active_contexts:
            self.active_contexts.remove(context_name)
            print(f"❌ DEACTIVATED: {context_name} verification")

    def get_daily_capacity(self) -> int:
        """Calculate total daily verification capacity across all active contexts"""
        return sum(ctx["daily_limit"] for ctx in self.get_all_active().values())

    def get_economic_value(self, context_name: str, coherence: float) -> float:
        """Calculate economic value of a verification based on coherence"""
        ctx = self.get_context(context_name)
        if not ctx or coherence < ctx["coherence_threshold"]:
            return 0.0
        premium = ctx["premium_multiplier"] * (coherence / ctx["coherence_threshold"])
        return ctx["economic_value"] * premium