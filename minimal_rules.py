#!/usr/bin/env python3
"""
Minimal Rules - Immutable rule set for the Decision Governor.

This module defines the basic immutable rules and constraints that govern
decision-making in autonomous systems. These rules ensure safety, accountability,
and alignment with core principles.
"""

from typing import Dict, Any

# Immutable Rules Dictionary
# These rules cannot be changed at runtime and define the fundamental constraints
# for all decision-making in the system.

MINIMAL_RULES: Dict[str, Any] = {
    # Core allowed decision intents
    'allowed_intents': [
        'data_analysis',
        'model_inference',
        'resource_allocation',
        'system_monitoring',
        'error_recovery',
        'learning_update',
        'validation_check'
    ],

    # Authority requirements for different decision types
    'authority_requirements': {
        'data_analysis': 'low',
        'model_inference': 'low',
        'resource_allocation': 'medium',
        'system_monitoring': 'low',
        'error_recovery': 'medium',
        'learning_update': 'high',
        'validation_check': 'low'
    },

    # Domain-specific constraints for decision parameters
    'constraints': {
        # Resource allocation limits
        'cpu_percent': {
            'type': 'range',
            'min': 0.0,
            'max': 100.0
        },
        'memory_mb': {
            'type': 'range',
            'min': 0,
            'max': 8192  # 8GB limit
        },
        'timeout_seconds': {
            'type': 'range',
            'min': 1,
            'max': 300  # 5 minutes max
        },

        # Model parameters
        'model_name': {
            'type': 'enum',
            'values': ['phi-3.5', 'gemma-2', 'qwen-7b', 'local-model']
        },
        'temperature': {
            'type': 'range',
            'min': 0.0,
            'max': 2.0
        },

        # Data validation
        'data_size_mb': {
            'type': 'range',
            'min': 0,
            'max': 1000  # 1GB max
        },
        'file_path': {
            'type': 'regex',
            'pattern': r'^[a-zA-Z0-9_/.-]+$'  # Safe path characters only
        }
    },

    # Risk thresholds for different operation types
    'risk_thresholds': {
        'low_risk': 0.2,
        'medium_risk': 0.5,
        'high_risk': 0.8,
        'critical_risk': 0.95
    },

    # Resource cost multipliers for different operations
    'resource_costs': {
        'data_analysis': 1.0,
        'model_inference': 2.0,
        'resource_allocation': 1.5,
        'system_monitoring': 0.5,
        'error_recovery': 1.2,
        'learning_update': 3.0,
        'validation_check': 0.8
    },

    # System integrity requirements
    'integrity_requirements': {
        'min_chain_length': 1,
        'max_divergence_rate': 0.01,  # 1% max divergence in replay
        'required_verification_interval': 3600,  # Verify chains every hour
        'emergency_stop_timeout': 300  # 5 minutes emergency timeout
    },

    # Ethical and safety constraints
    'ethical_constraints': {
        'no_personal_data_processing': True,
        'no_external_network_access': True,  # Offline-first
        'max_autonomous_runtime': 86400,  # 24 hours max continuous runtime
        'require_human_override_for_critical': True
    }
}

def get_rules() -> Dict[str, Any]:
    """
    Get the immutable rules dictionary.

    Returns:
        Dictionary containing all governance rules
    """
    return MINIMAL_RULES.copy()  # Return a copy to prevent modification

def validate_rules_integrity(rules: Dict[str, Any]) -> bool:
    """
    Validate that rules dictionary has required structure.

    Args:
        rules: Rules dictionary to validate

    Returns:
        True if rules are valid, False otherwise
    """
    required_keys = [
        'allowed_intents',
        'authority_requirements',
        'constraints',
        'risk_thresholds',
        'resource_costs',
        'integrity_requirements',
        'ethical_constraints'
    ]

    for key in required_keys:
        if key not in rules:
            return False

    # Validate allowed_intents is a list
    if not isinstance(rules['allowed_intents'], list):
        return False

    # Validate authority_requirements is a dict
    if not isinstance(rules['authority_requirements'], dict):
        return False

    return True

def get_risk_threshold(risk_level: str) -> float:
    """
    Get the numerical risk threshold for a risk level.

    Args:
        risk_level: Risk level string ('low', 'medium', 'high', 'critical')

    Returns:
        Numerical risk threshold (0.0 to 1.0)
    """
    thresholds = MINIMAL_RULES.get('risk_thresholds', {})
    return thresholds.get(risk_level, 0.5)  # Default to medium

def get_resource_cost(intent: str) -> float:
    """
    Get the resource cost multiplier for a decision intent.

    Args:
        intent: Decision intent

    Returns:
        Resource cost multiplier
    """
    costs = MINIMAL_RULES.get('resource_costs', {})
    return costs.get(intent, 1.0)  # Default cost

def check_ethical_constraint(constraint_name: str) -> bool:
    """
    Check if an ethical constraint is enabled.

    Args:
        constraint_name: Name of the ethical constraint

    Returns:
        True if constraint is enabled/active
    """
    constraints = MINIMAL_RULES.get('ethical_constraints', {})
    return constraints.get(constraint_name, False)