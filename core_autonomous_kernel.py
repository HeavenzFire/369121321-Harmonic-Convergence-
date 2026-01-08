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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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