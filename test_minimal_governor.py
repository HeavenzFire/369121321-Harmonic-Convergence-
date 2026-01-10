#!/usr/bin/env python3
"""
Unit tests for the Minimal Decision Governor.

Tests cover validation, logging, execution, chain verification, and replay functionality.
"""

import unittest
import time
from unittest.mock import Mock

from minimal_governor import DecisionGovernor, DecisionContext, DecisionResult
from minimal_rules import get_rules


class TestDecisionGovernor(unittest.TestCase):
    """Test cases for DecisionGovernor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.rules = get_rules()
        self.governor = DecisionGovernor(rules=self.rules, max_risk=0.8, budget_limit=10.0)
        self.base_time = time.time()

    def test_initialization(self):
        """Test governor initialization."""
        self.assertEqual(self.governor.max_risk, 0.8)
        self.assertEqual(self.governor.budget_limit, 10.0)
        self.assertEqual(len(self.governor.intent_chain), 0)
        self.assertEqual(len(self.governor.execution_chain), 0)

    def test_validate_intent_valid(self):
        """Test validation of valid decision intent."""
        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 50},
            risk_score=0.2,
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.0
        )

        self.assertTrue(self.governor.validate_intent(context))

    def test_validate_intent_invalid_intent(self):
        """Test validation rejects invalid intent."""
        context = DecisionContext(
            intent='invalid_intent',
            parameters={},
            risk_score=0.1,
            timestamp=self.base_time,
            authority_level='low',
            resource_cost=0.5
        )

        self.assertFalse(self.governor.validate_intent(context))

    def test_validate_intent_high_risk(self):
        """Test validation rejects high risk decisions."""
        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 50},
            risk_score=0.9,  # Above max_risk of 0.8
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.0
        )

        self.assertFalse(self.governor.validate_intent(context))

    def test_validate_intent_insufficient_authority(self):
        """Test validation rejects insufficient authority."""
        context = DecisionContext(
            intent='learning_update',  # Requires 'high' authority
            parameters={},
            risk_score=0.3,
            timestamp=self.base_time,
            authority_level='low',  # Insufficient
            resource_cost=3.0
        )

        self.assertFalse(self.governor.validate_intent(context))

    def test_validate_intent_budget_exceeded(self):
        """Test validation rejects when budget exceeded."""
        # Set budget to 0
        self.governor.current_budget = 0.0

        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 50},
            risk_score=0.2,
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.0
        )

        self.assertFalse(self.governor.validate_intent(context))

    def test_validate_intent_constraint_violation(self):
        """Test validation rejects constraint violations."""
        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 2000},  # Above 1000MB limit
            risk_score=0.2,
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.0
        )

        self.assertFalse(self.governor.validate_intent(context))

    def test_log_intent(self):
        """Test intent logging."""
        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 50},
            risk_score=0.2,
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.0
        )

        # Validate first
        self.assertTrue(self.governor.validate_intent(context))

        # Log intent
        intent_hash = self.governor.log_intent(context)

        self.assertIsInstance(intent_hash, str)
        self.assertEqual(len(self.governor.intent_chain), 1)

        entry = self.governor.intent_chain[0]
        self.assertEqual(entry['type'], 'intent')
        self.assertEqual(entry['intent'], 'data_analysis')
        self.assertEqual(entry['hash'], intent_hash)

    def test_execute_decision_success(self):
        """Test successful decision execution."""
        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 50},
            risk_score=0.2,
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.0
        )

        def mock_decision_func(ctx):
            return f"Processed {ctx.parameters['data_size_mb']}MB of data"

        # Validate and log
        self.assertTrue(self.governor.validate_intent(context))
        self.governor.log_intent(context)

        # Execute
        result = self.governor.execute_decision(mock_decision_func, context)

        self.assertTrue(result.success)
        self.assertIsInstance(result.execution_time, float)
        self.assertEqual(result.resource_used, 1.0)
        self.assertEqual(result.output, "Processed 50MB of data")
        self.assertEqual(len(self.governor.execution_chain), 1)

    def test_execute_decision_failure(self):
        """Test failed decision execution."""
        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 50},
            risk_score=0.2,
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.0
        )

        def failing_decision_func(ctx):
            raise ValueError("Decision failed")

        # Validate and log
        self.assertTrue(self.governor.validate_intent(context))
        self.governor.log_intent(context)

        # Execute
        result = self.governor.execute_decision(failing_decision_func, context)

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Decision failed")
        self.assertEqual(len(self.governor.execution_chain), 1)

    def test_verify_chains_valid(self):
        """Test chain verification with valid chains."""
        # Execute a decision to populate chains
        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 50},
            risk_score=0.2,
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.0
        )

        def mock_func(ctx):
            return "success"

        self.assertTrue(self.governor.validate_intent(context))
        self.governor.log_intent(context)
        self.governor.execute_decision(mock_func, context)

        # Verify chains
        verification = self.governor.verify_chains()

        self.assertTrue(verification['intent_chain_valid'])
        self.assertTrue(verification['execution_chain_valid'])
        self.assertTrue(verification['chains_integrity'])
        self.assertEqual(verification['intent_chain_length'], 1)
        self.assertEqual(verification['execution_chain_length'], 1)

    def test_replay_decision(self):
        """Test decision replay functionality."""
        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 50},
            risk_score=0.2,
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.0
        )

        def mock_func(ctx):
            return "original_output"

        # Execute original decision
        self.assertTrue(self.governor.validate_intent(context))
        self.governor.log_intent(context)
        original_result = self.governor.execute_decision(mock_func, context)

        # Replay decision
        decision_id = f"data_analysis_{int(self.base_time)}"
        replay_result = self.governor.replay_decision(decision_id)

        self.assertIn('original_result', replay_result)
        self.assertIn('replay_result', replay_result)
        self.assertIn('divergence_detected', replay_result)

    def test_get_status(self):
        """Test status reporting."""
        status = self.governor.get_status()

        self.assertIn('budget_remaining', status)
        self.assertIn('budget_limit', status)
        self.assertIn('chains_status', status)
        self.assertIn('total_decisions', status)
        self.assertIn('timestamp', status)

        self.assertEqual(status['budget_limit'], 10.0)
        self.assertEqual(status['total_decisions'], 0)

    def test_emergency_stop(self):
        """Test emergency stop functionality."""
        # Execute a decision first
        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 50},
            risk_score=0.2,
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.0
        )

        self.assertTrue(self.governor.validate_intent(context))
        self.governor.log_intent(context)

        # Emergency stop
        result = self.governor.emergency_stop()

        self.assertTrue(result)
        self.assertEqual(self.governor.current_budget, 0.0)
        self.assertEqual(len(self.governor.intent_chain), 2)  # Original + emergency stop

    def test_budget_reset(self):
        """Test automatic budget reset."""
        # Set budget to 0 and old timestamp
        self.governor.current_budget = 0.0
        self.governor.budget_reset_time = time.time() - 3700  # More than 1 hour ago

        # Check status (should trigger reset)
        status = self.governor.get_status()

        # Budget should be reset
        self.assertEqual(status['budget_remaining'], 10.0)


class TestDecisionContext(unittest.TestCase):
    """Test cases for DecisionContext dataclass."""

    def test_context_creation(self):
        """Test DecisionContext creation."""
        context = DecisionContext(
            intent='test_intent',
            parameters={'key': 'value'},
            risk_score=0.5,
            timestamp=1234567890.0,
            authority_level='medium',
            resource_cost=2.0
        )

        self.assertEqual(context.intent, 'test_intent')
        self.assertEqual(context.parameters, {'key': 'value'})
        self.assertEqual(context.risk_score, 0.5)
        self.assertEqual(context.timestamp, 1234567890.0)
        self.assertEqual(context.authority_level, 'medium')
        self.assertEqual(context.resource_cost, 2.0)


class TestDecisionResult(unittest.TestCase):
    """Test cases for DecisionResult dataclass."""

    def test_result_creation_success(self):
        """Test DecisionResult creation for success."""
        result = DecisionResult(
            success=True,
            output="test_output",
            execution_time=0.5,
            resource_used=1.0
        )

        self.assertTrue(result.success)
        self.assertEqual(result.output, "test_output")
        self.assertEqual(result.execution_time, 0.5)
        self.assertEqual(result.resource_used, 1.0)
        self.assertIsNone(result.error_message)

    def test_result_creation_failure(self):
        """Test DecisionResult creation for failure."""
        result = DecisionResult(
            success=False,
            output=None,
            execution_time=0.1,
            resource_used=0.5,
            error_message="Test error"
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.output)
        self.assertEqual(result.execution_time, 0.1)
        self.assertEqual(result.resource_used, 0.5)
        self.assertEqual(result.error_message, "Test error")


if __name__ == '__main__':
    unittest.main()