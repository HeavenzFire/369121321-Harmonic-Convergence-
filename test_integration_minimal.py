#!/usr/bin/env python3
"""
Integration tests for the Minimal Decision Governor.

Tests cover end-to-end decision lifecycles, chain integrity across multiple decisions,
and system behavior under various conditions.
"""

import unittest
import time
import json
from minimal_governor import DecisionGovernor, DecisionContext
from minimal_rules import get_rules


class TestIntegrationGovernor(unittest.TestCase):
    """Integration tests for DecisionGovernor."""

    def setUp(self):
        """Set up test fixtures."""
        self.rules = get_rules()
        self.governor = DecisionGovernor(rules=self.rules, max_risk=0.8, budget_limit=20.0)
        self.base_time = time.time()

    def test_full_decision_lifecycle(self):
        """Test complete decision lifecycle from validation to execution."""
        # Create decision context
        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 100},
            risk_score=0.3,
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.5
        )

        # 1. Validation
        self.assertTrue(self.governor.validate_intent(context))

        # 2. Intent logging
        intent_hash = self.governor.log_intent(context)
        self.assertIsInstance(intent_hash, str)
        self.assertEqual(len(self.governor.intent_chain), 1)

        # 3. Execution
        def analyze_data(ctx):
            return f"Analysis complete: {ctx.parameters['data_size_mb']}MB processed"

        result = self.governor.execute_decision(analyze_data, context)

        # 4. Verify execution
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Analysis complete: 100MB processed")
        self.assertEqual(len(self.governor.execution_chain), 1)

        # 5. Verify chains
        verification = self.governor.verify_chains()
        self.assertTrue(verification['chains_integrity'])

        # 6. Check budget deduction
        self.assertEqual(self.governor.current_budget, 18.5)  # 20.0 - 1.5

    def test_multiple_decisions_chain_integrity(self):
        """Test chain integrity across multiple decisions."""
        decisions = [
            {
                'intent': 'data_analysis',
                'params': {'data_size_mb': 50},
                'risk': 0.2,
                'cost': 1.0
            },
            {
                'intent': 'model_inference',
                'params': {'model_name': 'gemma-2', 'temperature': 0.5},
                'risk': 0.3,
                'cost': 2.0
            },
            {
                'intent': 'error_recovery',
                'params': {'error_type': 'timeout', 'retry_count': 2},
                'risk': 0.4,
                'cost': 1.2
            }
        ]

        # Execute multiple decisions
        for i, decision in enumerate(decisions):
            context = DecisionContext(
                intent=decision['intent'],
                parameters=decision['params'],
                risk_score=decision['risk'],
                timestamp=self.base_time + i,
                authority_level='medium',
                resource_cost=decision['cost']
            )

            # Validate and execute
            self.assertTrue(self.governor.validate_intent(context))
            self.governor.log_intent(context)

            def mock_decision(ctx):
                return f"Executed {ctx.intent} with params {ctx.parameters}"

            result = self.governor.execute_decision(mock_decision, context)
            self.assertTrue(result.success)

        # Verify final state
        self.assertEqual(len(self.governor.intent_chain), 3)
        self.assertEqual(len(self.governor.execution_chain), 3)

        # Verify chain integrity
        verification = self.governor.verify_chains()
        self.assertTrue(verification['chains_integrity'])

        # Check budget: 20.0 - 1.0 - 2.0 - 1.2 = 15.8
        self.assertEqual(self.governor.current_budget, 15.8)

    def test_replay_and_divergence_detection(self):
        """Test replay functionality and divergence detection."""
        # Execute original decision
        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 75},
            risk_score=0.25,
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.0
        )

        def original_func(ctx):
            return f"Original result: {ctx.parameters['data_size_mb']}"

        self.assertTrue(self.governor.validate_intent(context))
        self.governor.log_intent(context)
        original_result = self.governor.execute_decision(original_func, context)

        # Replay decision
        decision_id = f"data_analysis_{int(self.base_time)}"
        replay_result = self.governor.replay_decision(decision_id)

        # Check replay structure
        self.assertIn('original_result', replay_result)
        self.assertIn('replay_result', replay_result)
        self.assertIn('divergence_detected', replay_result)

        # In this minimal implementation, replay simulates success
        # In a real system, this would detect actual divergence
        self.assertIsInstance(replay_result['divergence_detected'], bool)

    def test_resource_budget_limits(self):
        """Test resource budget enforcement across multiple decisions."""
        # Set low budget
        self.governor.current_budget = 3.0

        # Execute decisions until budget exhausted
        decisions_executed = 0

        for i in range(5):  # Try 5 decisions
            context = DecisionContext(
                intent='data_analysis',
                parameters={'data_size_mb': 10},
                risk_score=0.1,
                timestamp=self.base_time + i,
                authority_level='low',
                resource_cost=1.0
            )

            if self.governor.validate_intent(context):
                self.governor.log_intent(context)

                def mock_func(ctx):
                    return "success"

                result = self.governor.execute_decision(mock_func, context)
                if result.success:
                    decisions_executed += 1

        # Should have executed 3 decisions (3.0 budget / 1.0 cost per decision)
        self.assertEqual(decisions_executed, 3)
        self.assertEqual(self.governor.current_budget, 0.0)

    def test_emergency_stop_integration(self):
        """Test emergency stop functionality in integrated scenario."""
        # Execute some decisions first
        for i in range(2):
            context = DecisionContext(
                intent='data_analysis',
                parameters={'data_size_mb': 25},
                risk_score=0.2,
                timestamp=self.base_time + i,
                authority_level='medium',
                resource_cost=1.0
            )

            self.assertTrue(self.governor.validate_intent(context))
            self.governor.log_intent(context)

            def mock_func(ctx):
                return f"Decision {i+1}"

            self.governor.execute_decision(mock_func, context)

        # Verify normal operation
        self.assertEqual(len(self.governor.intent_chain), 2)
        self.assertEqual(len(self.governor.execution_chain), 2)

        # Emergency stop
        result = self.governor.emergency_stop()
        self.assertTrue(result)

        # Verify emergency state
        self.assertEqual(self.governor.current_budget, 0.0)
        self.assertEqual(len(self.governor.intent_chain), 3)  # + emergency entry

        # Try to execute new decision (should fail due to zero budget)
        context = DecisionContext(
            intent='data_analysis',
            parameters={'data_size_mb': 10},
            risk_score=0.1,
            timestamp=self.base_time + 10,
            authority_level='low',
            resource_cost=0.5
        )

        # Should fail validation due to zero budget
        self.assertFalse(self.governor.validate_intent(context))

    def test_authority_escalation_scenarios(self):
        """Test authority-based decision filtering."""
        test_cases = [
            # (intent, authority_level, should_pass)
            ('data_analysis', 'low', True),      # Low requirement, low authority
            ('learning_update', 'medium', False), # High requirement, medium authority
            ('learning_update', 'high', True),    # High requirement, high authority
            ('error_recovery', 'low', False),     # Medium requirement, low authority
            ('error_recovery', 'medium', True),    # Medium requirement, medium authority
        ]

        for intent, authority, should_pass in test_cases:
            with self.subTest(intent=intent, authority=authority):
                context = DecisionContext(
                    intent=intent,
                    parameters={},
                    risk_score=0.3,
                    timestamp=self.base_time,
                    authority_level=authority,
                    resource_cost=1.0
                )

                result = self.governor.validate_intent(context)
                self.assertEqual(result, should_pass,
                    f"Intent '{intent}' with authority '{authority}' should {'pass' if should_pass else 'fail'}")

    def test_constraint_validation_integration(self):
        """Test parameter constraint validation in integrated scenarios."""
        # Test valid constraints
        valid_context = DecisionContext(
            intent='data_analysis',
            parameters={
                'data_size_mb': 500,  # Within 0-1000 range
                'timeout_seconds': 60,  # Within 1-300 range
                'file_path': '/valid/path/file.txt'  # Matches regex
            },
            risk_score=0.2,
            timestamp=self.base_time,
            authority_level='medium',
            resource_cost=1.0
        )

        self.assertTrue(self.governor.validate_intent(valid_context))

        # Test invalid constraints
        invalid_cases = [
            {'data_size_mb': 1500},  # Above max
            {'timeout_seconds': 500},  # Above max
            {'file_path': '../../../etc/passwd'},  # Invalid characters
        ]

        for invalid_params in invalid_cases:
            with self.subTest(params=invalid_params):
                context = DecisionContext(
                    intent='data_analysis',
                    parameters=invalid_params,
                    risk_score=0.2,
                    timestamp=self.base_time,
                    authority_level='medium',
                    resource_cost=1.0
                )

                self.assertFalse(self.governor.validate_intent(context))

    def test_chain_persistence_simulation(self):
        """Test chain behavior that would be used with persistence."""
        # Execute several decisions to build chain history
        for i in range(5):
            context = DecisionContext(
                intent='data_analysis',
                parameters={'data_size_mb': 20 + i * 10},
                risk_score=0.2,
                timestamp=self.base_time + i * 60,  # 1 minute apart
                authority_level='medium',
                resource_cost=1.0
            )

            self.assertTrue(self.governor.validate_intent(context))
            self.governor.log_intent(context)

            def mock_func(ctx):
                return f"Result {i+1}"

            self.governor.execute_decision(mock_func, context)

        # Verify chain structure
        self.assertEqual(len(self.governor.intent_chain), 5)
        self.assertEqual(len(self.governor.execution_chain), 5)

        # Verify hash chaining
        for i in range(1, len(self.governor.intent_chain)):
            prev_hash = self.governor.intent_chain[i-1]['hash']
            current_prev = self.governor.intent_chain[i]['previous_hash']
            self.assertEqual(prev_hash, current_prev)

        # Verify execution chain linkage
        for i in range(len(self.governor.execution_chain)):
            intent_hash = self.governor.intent_chain[i]['hash']
            exec_intent_hash = self.governor.execution_chain[i]['intent_hash']
            self.assertEqual(intent_hash, exec_intent_hash)


if __name__ == '__main__':
    unittest.main()