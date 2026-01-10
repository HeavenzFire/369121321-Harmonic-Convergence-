import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import random
import os
import hashlib
import math
import statistics
from collections import deque
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConfidenceTier(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ActionPermission(Enum):
    OBSERVE = "observe"
    REVIEW = "review"
    ESCALATE = "escalate"

class DecisionThresholds:
    """
    Governance framework for causal inference outputs.
    Defines when evidence is sufficient for action and how uncertainty is communicated.
    """

    def __init__(self):
        self.confidence_thresholds = {
            ConfidenceTier.LOW: (0.0, 0.3),
            ConfidenceTier.MEDIUM: (0.3, 0.7),
            ConfidenceTier.HIGH: (0.7, 1.0)
        }

        self.action_permissions = {
            ConfidenceTier.LOW: ActionPermission.OBSERVE,
            ConfidenceTier.MEDIUM: ActionPermission.REVIEW,
            ConfidenceTier.HIGH: ActionPermission.ESCALATE
        }

        self.audit_log: List[Dict[str, Any]] = []

    def evaluate_causal_output(self, causal_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluate causal inference results against governance thresholds.

        Args:
            causal_metrics: Dictionary containing causal_strength, intervention_effect, counterfactual_confidence

        Returns:
            Decision governance result with tier, permission, and uncertainty report
        """
        # Calculate overall confidence score
        confidence_score = self._calculate_overall_confidence(causal_metrics)

        # Determine confidence tier
        tier = self._get_confidence_tier(confidence_score)

        # Get action permission
        permission = self.action_permissions[tier]

        # Generate uncertainty report
        uncertainty_report = self._generate_uncertainty_report(causal_metrics, confidence_score)

        # Create governance decision
        decision = {
            'timestamp': datetime.now().isoformat(),
            'confidence_score': confidence_score,
            'confidence_tier': tier.value,
            'action_permission': permission.value,
            'uncertainty_report': uncertainty_report,
            'causal_metrics': causal_metrics,
            'human_override_required': permission != ActionPermission.OBSERVE,
            'audit_id': hashlib.sha256(f"{datetime.now().isoformat()}_{json.dumps(causal_metrics, sort_keys=True)}".encode()).hexdigest()[:16]
        }

        # Log decision
        self._log_decision(decision)

        return decision

    def _calculate_overall_confidence(self, metrics: Dict[str, float]) -> float:
        """Calculate weighted confidence score from multiple causal metrics."""
        weights = {
            'causal_strength': 0.4,
            'intervention_effect': 0.3,
            'counterfactual_confidence': 0.3
        }

        confidence = 0.0
        total_weight = 0.0

        for metric, weight in weights.items():
            if metric in metrics:
                # Normalize metric to 0-1 scale (assuming metrics are already 0-1)
                normalized_value = max(0.0, min(1.0, metrics[metric]))
                confidence += normalized_value * weight
                total_weight += weight

        return confidence / total_weight if total_weight > 0 else 0.0

    def _get_confidence_tier(self, confidence_score: float) -> ConfidenceTier:
        """Determine confidence tier based on score."""
        for tier, (min_val, max_val) in self.confidence_thresholds.items():
            if min_val <= confidence_score <= max_val:
                return tier
        return ConfidenceTier.LOW  # Default to lowest tier

    def _generate_uncertainty_report(self, metrics: Dict[str, float], confidence_score: float) -> Dict[str, Any]:
        """Generate human-readable uncertainty assessment."""
        report = {
            'confidence_level': f"{confidence_score:.2%}",
            'confidence_interpretation': self._interpret_confidence(confidence_score),
            'key_uncertainties': [],
            'recommendations': []
        }

        # Analyze individual metrics for uncertainties
        if 'causal_strength' in metrics:
            strength = metrics['causal_strength']
            if strength < 0.4:
                report['key_uncertainties'].append("Weak causal relationship detected")
            elif strength > 0.8:
                report['key_uncertainties'].append("Strong causal evidence present")

        if 'intervention_effect' in metrics:
            effect = metrics['intervention_effect']
            if effect < 0.2:
                report['key_uncertainties'].append("Minimal intervention impact observed")
            elif effect > 0.6:
                report['key_uncertainties'].append("Significant intervention effect detected")

        if 'counterfactual_confidence' in metrics:
            cf_conf = metrics['counterfactual_confidence']
            if cf_conf < 0.5:
                report['key_uncertainties'].append("Counterfactual predictions have high uncertainty")

        # Generate recommendations based on tier
        tier = self._get_confidence_tier(confidence_score)
        if tier == ConfidenceTier.LOW:
            report['recommendations'].extend([
                "Continue monitoring with additional data collection",
                "Consider alternative analytical approaches",
                "Human review recommended before any action"
            ])
        elif tier == ConfidenceTier.MEDIUM:
            report['recommendations'].extend([
                "Schedule human review of causal evidence",
                "Validate findings with additional data sources",
                "Document decision rationale for audit trail"
            ])
        else:  # HIGH
            report['recommendations'].extend([
                "Immediate human review required",
                "Consider escalation to decision authorities",
                "Prepare intervention documentation"
            ])

        return report

    def _interpret_confidence(self, score: float) -> str:
        """Provide natural language interpretation of confidence score."""
        if score < 0.3:
            return "Low confidence - evidence is weak or inconclusive"
        elif score < 0.7:
            return "Medium confidence - evidence is moderate, review recommended"
        else:
            return "High confidence - evidence is strong, action may be warranted"

    def _log_decision(self, decision: Dict[str, Any]):
        """Log governance decision for audit purposes."""
        self.audit_log.append(decision)

        # Keep only last 1000 decisions to prevent memory bloat
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

        logging.info(f"Governance decision logged: {decision['audit_id']} - {decision['confidence_tier']} confidence")

    def get_audit_trail(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent governance decisions for audit."""
        return self.audit_log[-limit:]

    def export_audit_log(self, filepath: str):
        """Export complete audit log to file."""
        with open(filepath, 'w') as f:
            json.dump({
                'export_timestamp': datetime.now().isoformat(),
                'audit_log': self.audit_log
            }, f, indent=2)
        logging.info(f"Audit log exported to {filepath} with {len(self.audit_log)} entries")

class CoreAutonomousKernel:
    """
    Core Autonomous Kernel (CAK) - Self-orchestrating decision-making and systemic evolution.

    Functions:
    - Multi-modal perception: Ingests data from code, sensors, networks, and emergent patterns
    - Syntropic state mapping: Tracks energy, entropy, and convergence metrics across all subsystems
    - Self-directed experimentation: Launches micro-R&D threads autonomously based on emergent anomalies or opportunities
    """

    def __init__(self, convergence_state_path: str = 'convergence_state.json'):
        self.convergence_state_path = convergence_state_path
        self.perception_buffer: List[Dict[str, Any]] = []
        self.active_experiments: Dict[str, threading.Thread] = {}
        self.syntropic_metrics = {
            'energy_level': 1.0,
            'entropy_rate': 0.0,
            'convergence_velocity': 0.0,
            'anomaly_score': 0.0
        }
        self.running = False
        self.perception_thread: Optional[threading.Thread] = None

    def start_kernel(self):
        """Start the CAK main loop with all subsystems."""
        self.running = True

        # Start perception system
        self.perception_thread = threading.Thread(target=self._perception_loop, daemon=True)
        self.perception_thread.start()

        # Start evolution engine
        self.evolution_thread = threading.Thread(target=self._evolution_loop, daemon=True)
        self.evolution_thread.start()

        # Start learning system
        self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
        self.learning_thread.start()

        logging.info("Core Autonomous Kernel started with full evolution capabilities")

    def stop_kernel(self):
        """Stop the CAK and all experiments."""
        self.running = False
        for exp_id, thread in self.active_experiments.items():
            thread.join(timeout=5.0)
        if self.perception_thread:
            self.perception_thread.join(timeout=5.0)
        logging.info("Core Autonomous Kernel stopped")

    def ingest_data(self, data_source: str, data: Dict[str, Any]):
        """Ingest data from various sources with enhanced metadata."""
        perception_entry = {
            'timestamp': datetime.now().isoformat(),
            'source': data_source,
            'data': data,
            'processed': False,
            'data_hash': hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest(),
            'priority': self._calculate_data_priority(data)
        }
        self.perception_buffer.append(perception_entry)
        logging.debug(f"Ingested data from {data_source} with priority {perception_entry['priority']}")

    def _calculate_data_priority(self, data: Dict[str, Any]) -> float:
        """Calculate processing priority based on data characteristics."""
        priority = 0.5  # Base priority

        # Increase priority for critical indicators
        if 'error' in data or 'anomaly' in data:
            priority += 0.3
        if 'success' in data or 'convergence' in data:
            priority += 0.2
        if 'threat' in data or 'alert' in data:
            priority += 0.4

        # Cap at 1.0
        return min(priority, 1.0)

    def _perception_loop(self):
        """Main perception and processing loop."""
        while self.running:
            self._process_perception_buffer()
            self._update_syntropic_metrics()
            self._check_for_anomalies()
            time.sleep(1.0)  # Process every second

    def _process_perception_buffer(self):
        """Process unprocessed perception entries."""
        for entry in self.perception_buffer:
            if not entry['processed']:
                self._analyze_data(entry)
                entry['processed'] = True

    def _analyze_data(self, entry: Dict[str, Any]):
        """Advanced data analysis with pattern recognition and learning."""
        data = entry['data']
        source = entry['source']

        # Enhanced pattern detection
        anomaly_indicators = ['error', 'failure', 'threat', 'anomaly', 'breach']
        success_indicators = ['success', 'convergence', 'optimization', 'learning']

        for indicator in anomaly_indicators:
            if indicator in str(data).lower():
                self.syntropic_metrics['anomaly_score'] += 0.15

        for indicator in success_indicators:
            if indicator in str(data).lower():
                self.syntropic_metrics['energy_level'] += 0.08

        # Source-specific analysis
        if source == 'filesystem':
            self._analyze_filesystem_patterns(data)
        elif source == 'network':
            self._analyze_network_patterns(data)
        elif source == 'system':
            self._analyze_system_patterns(data)

        # Update learning model
        self._update_learning_model(entry)

    def _update_syntropic_metrics(self):
        """Update syntropic state mapping metrics."""
        # Simulate metric updates based on system state
        self.syntropic_metrics['entropy_rate'] = random.uniform(0.0, 1.0)
        self.syntropic_metrics['convergence_velocity'] = random.uniform(-0.1, 0.1)

        # Decay anomaly score over time
        self.syntropic_metrics['anomaly_score'] *= 0.95

        # Update convergence state
        self._update_convergence_state()

    def _update_convergence_state(self):
        """Update the convergence state with current metrics."""
        try:
            with open(self.convergence_state_path, 'r') as f:
                state = json.load(f)

            state['syntropic_metrics'] = self.syntropic_metrics
            state['timestamp'] = datetime.now().isoformat()

            with open(self.convergence_state_path, 'w') as f:
                json.dump(state, f, indent=2)

        except FileNotFoundError:
            logging.warning("Convergence state file not found")

    def _check_for_anomalies(self):
        """Advanced anomaly detection with multiple triggers."""
        anomaly_triggers = [
            ('high_anomaly', self.syntropic_metrics['anomaly_score'] > 0.7),
            ('low_energy', self.syntropic_metrics['energy_level'] < 0.3),
            ('high_entropy', self.syntropic_metrics['entropy_rate'] > 0.8),
            ('divergent_convergence', abs(self.syntropic_metrics['convergence_velocity']) > 0.15)
        ]

        for trigger_name, condition in anomaly_triggers:
            if condition:
                self._launch_experiment(f'{trigger_name}_response')

    def _launch_experiment(self, experiment_type: str):
        """Launch a self-directed experiment."""
        exp_id = f"{experiment_type}_{int(time.time())}"
        thread = threading.Thread(target=self._run_experiment, args=(exp_id, experiment_type), daemon=True)
        self.active_experiments[exp_id] = thread
        thread.start()
        logging.info(f"Launched experiment: {exp_id}")

    def _run_experiment(self, exp_id: str, experiment_type: str):
        """Run a micro-R&D experiment."""
        # Simulate experiment execution
        time.sleep(random.uniform(1.0, 5.0))
        result = {
            'experiment_id': exp_id,
            'type': experiment_type,
            'outcome': random.choice(['success', 'failure', 'insight']),
            'timestamp': datetime.now().isoformat()
        }

        # Log result to artifact vault (placeholder)
        logging.info(f"Experiment {exp_id} completed: {result['outcome']}")

        # Clean up
        del self.active_experiments[exp_id]

    def get_syntropic_state(self) -> Dict[str, float]:
        """Get current syntropic metrics."""
        return self.syntropic_metrics.copy()