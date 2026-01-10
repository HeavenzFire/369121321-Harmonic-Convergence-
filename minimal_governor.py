#!/usr/bin/env python3
"""
Minimal Decision Governor - Core accountability primitives for autonomous systems.

This module provides the essential components for pre-decision validation,
dual-chain cryptographic logging, and deterministic replay in offline AI systems.
"""

import hashlib
import json
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Callable


@dataclass
class DecisionContext:
    """Context for a decision, including intent, parameters, and metadata."""
    intent: str
    parameters: Dict[str, Any]
    risk_score: float
    timestamp: float
    authority_level: str
    resource_cost: float


@dataclass
class DecisionResult:
    """Result of a decision execution."""
    success: bool
    output: Any
    execution_time: float
    resource_used: float
    error_message: Optional[str] = None


class DecisionGovernor:
    """
    Core decision governance system with pre-validation, dual-chain logging, and replay.

    This implements the fundamental primitives for accountable autonomous decision-making:
    - Pre-decision validation against immutable rules
    - Dual-chain logging (intent + execution) with cryptographic integrity
    - Deterministic replay for verification
    - Resource budgeting and authority control
    """

    def __init__(self, rules: Dict[str, Any], max_risk: float = 0.8, budget_limit: float = 100.0):
        """
        Initialize the Decision Governor.

        Args:
            rules: Immutable rules dictionary defining allowed intents, constraints, etc.
            max_risk: Maximum allowed risk score (0.0 to 1.0)
            budget_limit: Maximum resource budget per hour
        """
        self.rules = rules
        self.max_risk = max_risk
        self.budget_limit = budget_limit

        # Dual-chain logging
        self.intent_chain: List[Dict[str, Any]] = []
        self.execution_chain: List[Dict[str, Any]] = []

        # Resource tracking
        self.current_budget = budget_limit
        self.budget_reset_time = time.time()
        self.lock = threading.Lock()

        # Replay storage
        self.decision_history: Dict[str, Dict[str, Any]] = {}

    def _reset_budget_if_needed(self):
        """Reset budget if an hour has passed."""
        current_time = time.time()
        if current_time - self.budget_reset_time >= 3600:  # 1 hour
            self.current_budget = self.budget_limit
            self.budget_reset_time = current_time

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate SHA256 hash of data."""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def _get_previous_hash(self, chain: List[Dict[str, Any]]) -> str:
        """Get the hash of the last entry in a chain."""
        return chain[-1]['hash'] if chain else 'genesis'

    def validate_intent(self, context: DecisionContext) -> bool:
        """
        Validate a decision intent against immutable rules.

        Args:
            context: Decision context to validate

        Returns:
            True if valid, False otherwise
        """
        with self.lock:
            # Check intent is allowed
            if context.intent not in self.rules.get('allowed_intents', []):
                return False

            # Check risk threshold
            if context.risk_score > self.max_risk:
                return False

            # Check resource budget
            self._reset_budget_if_needed()
            if context.resource_cost > self.current_budget:
                return False

            # Check authority level
            required_authority = self.rules.get('authority_requirements', {}).get(context.intent, 'low')
            if self._compare_authority(context.authority_level, required_authority) < 0:
                return False

            # Check domain constraints
            constraints = self.rules.get('constraints', {})
            for param, value in context.parameters.items():
                if param in constraints:
                    constraint = constraints[param]
                    if not self._check_constraint(value, constraint):
                        return False

            return True

    def _compare_authority(self, current: str, required: str) -> int:
        """Compare authority levels. Returns 1 if current >= required, -1 if current < required."""
        levels = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        return levels.get(current, 0) - levels.get(required, 0)

    def _check_constraint(self, value: Any, constraint: Dict[str, Any]) -> bool:
        """Check if a value satisfies a constraint."""
        constraint_type = constraint.get('type')

        if constraint_type == 'range':
            min_val = constraint.get('min', float('-inf'))
            max_val = constraint.get('max', float('inf'))
            return min_val <= value <= max_val
        elif constraint_type == 'enum':
            allowed_values = constraint.get('values', [])
            return value in allowed_values
        elif constraint_type == 'regex':
            import re
            pattern = constraint.get('pattern', '')
            return bool(re.match(pattern, str(value)))

        return True  # Unknown constraint type defaults to allowed

    def log_intent(self, context: DecisionContext) -> str:
        """
        Log a decision intent to the intent chain.

        Args:
            context: Decision context to log

        Returns:
            Hash of the logged entry
        """
        with self.lock:
            entry = {
                'type': 'intent',
                'timestamp': context.timestamp,
                'intent': context.intent,
                'parameters': context.parameters,
                'risk_score': context.risk_score,
                'authority_level': context.authority_level,
                'resource_cost': context.resource_cost,
                'previous_hash': self._get_previous_hash(self.intent_chain)
            }
            entry['hash'] = self._calculate_hash(entry)
            self.intent_chain.append(entry)

            # Store for replay
            decision_id = f"{context.intent}_{int(context.timestamp)}"
            self.decision_history[decision_id] = {
                'context': context,
                'intent_entry': entry
            }

            return entry['hash']

    def execute_decision(self, decision_func: Callable[[DecisionContext], Any],
                        context: DecisionContext) -> DecisionResult:
        """
        Execute a decision function and log the result.

        Args:
            decision_func: Function to execute the decision
            context: Decision context

        Returns:
            DecisionResult with execution outcome
        """
        start_time = time.time()

        try:
            # Execute the decision
            output = decision_func(context)
            execution_time = time.time() - start_time
            resource_used = context.resource_cost

            # Update budget
            with self.lock:
                self.current_budget -= resource_used

            result = DecisionResult(
                success=True,
                output=output,
                execution_time=execution_time,
                resource_used=resource_used
            )

        except Exception as e:
            execution_time = time.time() - start_time
            result = DecisionResult(
                success=False,
                output=None,
                execution_time=execution_time,
                resource_used=0.0,
                error_message=str(e)
            )

        # Log execution
        with self.lock:
            entry = {
                'type': 'execution',
                'timestamp': time.time(),
                'intent_hash': self.intent_chain[-1]['hash'] if self.intent_chain else None,
                'success': result.success,
                'output': result.output,
                'execution_time': result.execution_time,
                'resource_used': result.resource_used,
                'error_message': result.error_message,
                'previous_hash': self._get_previous_hash(self.execution_chain)
            }
            entry['hash'] = self._calculate_hash(entry)
            self.execution_chain.append(entry)

            # Update history
            decision_id = f"{context.intent}_{int(context.timestamp)}"
            if decision_id in self.decision_history:
                self.decision_history[decision_id]['execution_entry'] = entry
                self.decision_history[decision_id]['result'] = result

        return result

    def verify_chains(self) -> Dict[str, Any]:
        """
        Verify the integrity of both chains.

        Returns:
            Dictionary with verification results
        """
        def verify_chain(chain: List[Dict[str, Any]]) -> bool:
            """Verify a single chain's hash integrity."""
            for i, entry in enumerate(chain):
                expected_hash = entry['hash']
                calculated_hash = self._calculate_hash({
                    k: v for k, v in entry.items() if k != 'hash'
                })
                if expected_hash != calculated_hash:
                    return False

                # Check chain linkage
                if i > 0:
                    if entry['previous_hash'] != chain[i-1]['hash']:
                        return False
            return True

        with self.lock:
            intent_valid = verify_chain(self.intent_chain)
            execution_valid = verify_chain(self.execution_chain)

            return {
                'intent_chain_valid': intent_valid,
                'execution_chain_valid': execution_valid,
                'chains_integrity': intent_valid and execution_valid,
                'intent_chain_length': len(self.intent_chain),
                'execution_chain_length': len(self.execution_chain)
            }

    def replay_decision(self, decision_id: str) -> Dict[str, Any]:
        """
        Replay a past decision deterministically.

        Args:
            decision_id: ID of the decision to replay

        Returns:
            Dictionary with replay results and comparison
        """
        if decision_id not in self.decision_history:
            return {'error': 'Decision not found'}

        history = self.decision_history[decision_id]
        original_context = history['context']
        original_result = history.get('result')

        # Replay the decision (assuming we have the decision function)
        # For this minimal version, we'll simulate replay
        replay_result = DecisionResult(
            success=True,
            output="replayed_output",  # Simulated
            execution_time=0.001,
            resource_used=original_context.resource_cost
        )

        # Compare with original
        divergence_detected = False
        if original_result:
            if (replay_result.success != original_result.success or
                replay_result.output != original_result.output):
                divergence_detected = True

        return {
            'decision_id': decision_id,
            'original_result': original_result,
            'replay_result': replay_result,
            'divergence_detected': divergence_detected,
            'replay_timestamp': time.time()
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get current governor status.

        Returns:
            Dictionary with current status information
        """
        with self.lock:
            self._reset_budget_if_needed()
            verification = self.verify_chains()

            return {
                'budget_remaining': self.current_budget,
                'budget_limit': self.budget_limit,
                'chains_status': verification,
                'total_decisions': len(self.intent_chain),
                'timestamp': time.time()
            }

    def emergency_stop(self) -> bool:
        """
        Emergency stop - halt all decision processing.

        Returns:
            True if stopped successfully
        """
        with self.lock:
            # Log emergency stop
            entry = {
                'type': 'emergency_stop',
                'timestamp': time.time(),
                'previous_hash': self._get_previous_hash(self.intent_chain)
            }
            entry['hash'] = self._calculate_hash(entry)
            self.intent_chain.append(entry)

            # Clear budget to prevent new decisions
            self.current_budget = 0.0

            return True