#!/usr/bin/env python3
"""
Evolve CLI - Longitudinal Prevention System Runner
Executes the LongitudinalPreventionSystem with deterministic sample data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'phase7-temporal'))

from phase7_longitudinal_prevention import LongitudinalPreventionSystem
import json

def main():
    # Deterministic sample intake data
    sample_cases = [
        {
            "case_id": "CASE_001",
            "features": {
                "age": 5,
                "income_level": "low",
                "family_stress_indicators": 3,
                "prior_reports": 1,
                "housing_stability": "unstable"
            },
            "historical_outcome": "false_negative"
        },
        {
            "case_id": "CASE_002",
            "features": {
                "age": 8,
                "income_level": "medium",
                "family_stress_indicators": 1,
                "prior_reports": 0,
                "housing_stability": "stable"
            },
            "historical_outcome": "true_positive"
        },
        {
            "case_id": "CASE_003",
            "features": {
                "age": 12,
                "income_level": "low",
                "family_stress_indicators": 4,
                "prior_reports": 2,
                "housing_stability": "unstable"
            },
            "historical_outcome": "false_negative"
        }
    ]

    # Initialize the prevention system
    prevention_system = LongitudinalPreventionSystem()

    # Process retrospective correction
    retrospective_results = prevention_system.retrospective_correction(sample_cases)

    # Process short-horizon intervention
    intervention_results = prevention_system.short_horizon_intervention(sample_cases)

    # Process statistical cascade reduction
    cascade_results = prevention_system.statistical_cascade_reduction(sample_cases)

    # Structured output
    output = {
        "system_status": "operational",
        "sample_cases_processed": len(sample_cases),
        "retrospective_correction": retrospective_results,
        "short_horizon_intervention": intervention_results,
        "statistical_cascade_reduction": cascade_results,
        "deterministic_hash": "evolve_v1_2026"
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()