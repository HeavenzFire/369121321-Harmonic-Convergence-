#!/usr/bin/env python3
"""
Verifiable Decision Traces Logger
Captures all decisions made by the Sovereign Intelligence Evolution System
with cryptographic integrity and chain of custody.
"""

import hashlib
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import threading

class DecisionTraceLogger:
    """
    Cryptographically verifiable decision trace logger.
    Maintains an immutable chain of all decisions made by the system.
    """

    def __init__(self, log_file: str = "decision_traces.json"):
        self.log_file = log_file
        self.traces: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        self.previous_hash = "0" * 64  # Genesis hash
        self.load_existing_traces()

    def load_existing_traces(self):
        """Load existing traces from file and verify integrity."""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
                self.traces = data.get('traces', [])
                self.previous_hash = data.get('latest_hash', "0" * 64)

                # Verify chain integrity
                if not self.verify_chain():
                    print("[TRACE] Warning: Decision trace chain integrity compromised!")
                    # Reset to empty chain if corrupted
                    self.traces = []
                    self.previous_hash = "0" * 64
        except FileNotFoundError:
            # Initialize empty chain
            self.traces = []
            self.previous_hash = "0" * 64

    def log_decision(self, decision_type: str, parameters: Dict[str, Any],
                    outcome: Any, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a decision with full context and cryptographic verification.

        Args:
            decision_type: Type of decision (e.g., 'evolution_cycle', 'christ_forgiveness')
            parameters: Input parameters for the decision
            outcome: Result of the decision
            context: Additional context information

        Returns:
            The hash of the logged trace
        """
        with self.lock:
            timestamp = datetime.utcnow().isoformat()

            trace_data = {
                'timestamp': timestamp,
                'decision_type': decision_type,
                'parameters': parameters,
                'outcome': outcome,
                'context': context or {},
                'previous_hash': self.previous_hash
            }

            # Create hash of this trace
            trace_json = json.dumps(trace_data, sort_keys=True, default=str)
            current_hash = hashlib.sha256(trace_json.encode('utf-8')).hexdigest()

            # Add hash to trace
            trace_data['hash'] = current_hash

            # Add to traces
            self.traces.append(trace_data)
            self.previous_hash = current_hash

            # Save to file
            self._save_traces()

            return current_hash

    def _save_traces(self):
        """Save traces to file with latest hash."""
        data = {
            'traces': self.traces,
            'latest_hash': self.previous_hash,
            'total_traces': len(self.traces)
        }

        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def verify_chain(self) -> bool:
        """Verify the integrity of the entire decision trace chain."""
        if not self.traces:
            return True

        previous_hash = "0" * 64

        for trace in self.traces:
            # Recalculate hash
            trace_copy = trace.copy()
            expected_hash = trace_copy.pop('hash')

            trace_json = json.dumps(trace_copy, sort_keys=True, default=str)
            calculated_hash = hashlib.sha256(trace_json.encode('utf-8')).hexdigest()

            # Check hash matches
            if calculated_hash != expected_hash:
                return False

            # Check chain continuity
            if trace['previous_hash'] != previous_hash:
                return False

            previous_hash = expected_hash

        return True

    def get_traces_by_type(self, decision_type: str) -> List[Dict[str, Any]]:
        """Get all traces of a specific decision type."""
        return [t for t in self.traces if t['decision_type'] == decision_type]

    def get_recent_traces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent traces."""
        return self.traces[-limit:] if self.traces else []

    def get_trace_statistics(self) -> Dict[str, Any]:
        """Get statistics about the decision traces."""
        if not self.traces:
            return {'total_traces': 0, 'types': {}, 'verified': True}

        types = {}
        for trace in self.traces:
            t = trace['decision_type']
            types[t] = types.get(t, 0) + 1

        return {
            'total_traces': len(self.traces),
            'types': types,
            'verified': self.verify_chain(),
            'latest_timestamp': self.traces[-1]['timestamp'] if self.traces else None,
            'chain_hash': self.previous_hash
        }

    def export_traces(self, filename: str):
        """Export traces to a separate file for analysis."""
        data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'traces': self.traces,
            'statistics': self.get_trace_statistics()
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)

# Global logger instance
decision_logger = DecisionTraceLogger()