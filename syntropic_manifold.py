import numpy as np
import random
from dataclasses import dataclass, field
from typing import Dict, List, Callable
import time

@dataclass
class SyntropicState:
    """Full state vector X_t^full"""
    network_state: np.ndarray = field(default_factory=lambda: np.zeros(10))  # N_t
    logical_state: np.ndarray = field(default_factory=lambda: np.zeros(10))  # X_t^logic
    resonance: float = 1.0  # Current resonance level
    human_presence: bool = False  # h_t
    timestamp: float = field(default_factory=time.time)

    @property
    def full_state(self) -> np.ndarray:
        """Combined network and logical state"""
        return np.concatenate([self.network_state, self.logical_state])

@dataclass
class SyntropicOperator:
    """Individual syntropic operator (J, C, R, H, O, M)"""
    name: str
    function: Callable[[np.ndarray], np.ndarray]
    human_weight: float = 1.0  # α_U^human
    auto_weight: float = 0.8   # α_U^auto

class SyntropicManifold:
    """Dual-mode syntropic manifold system"""

    def __init__(self):
        self.current_state = SyntropicState()
        self.operators = self._initialize_operators()
        self.history: List[SyntropicState] = [self.current_state]
        self.resonance_threshold = 0.1  # Threshold for resonance stabilization

    def _initialize_operators(self) -> Dict[str, SyntropicOperator]:
        """Initialize the six syntropic operators"""
        return {
            'J': SyntropicOperator(  # Justice - balances inequalities
                name='Justice',
                function=lambda x: np.clip(x + 0.1 * (np.mean(x) - x), -1, 1),
                human_weight=1.2,
                auto_weight=0.9
            ),
            'C': SyntropicOperator(  # Convergence - reduces divergence
                name='Convergence',
                function=lambda x: x * 0.95 + np.mean(x) * 0.05,
                human_weight=1.1,
                auto_weight=0.8
            ),
            'R': SyntropicOperator(  # Resonance - amplifies coherence
                name='Resonance',
                function=lambda x: x * (1 + 0.1 * np.cos(np.arange(len(x)) * 0.1)),
                human_weight=1.0,
                auto_weight=0.7
            ),
            'H': SyntropicOperator(  # Harmony - optimizes relationships
                name='Harmony',
                function=lambda x: x + 0.05 * np.roll(x, 1),
                human_weight=1.3,
                auto_weight=0.6
            ),
            'O': SyntropicOperator(  # Optimization - improves efficiency
                name='Optimization',
                function=lambda x: np.sign(x) * np.sqrt(np.abs(x)),
                human_weight=0.9,
                auto_weight=0.8
            ),
            'M': SyntropicOperator(  # Monitoring - detects anomalies
                name='Monitoring',
                function=lambda x: x * (1 - 0.1 * (np.abs(x) > 2).astype(float)),
                human_weight=1.1,
                auto_weight=0.9
            )
        }

    def calculate_resonance_stabilization(self, state: SyntropicState) -> np.ndarray:
        """Calculate R_t^emergent resonance stabilization"""
        # Resonance based on coherence between network and logical states
        coherence = np.dot(state.network_state, state.logical_state) / (
            np.linalg.norm(state.network_state) * np.linalg.norm(state.logical_state) + 1e-8
        )

        # Stabilization vector that reduces destructive interference
        stabilization = np.ones(20) * (1 + coherence * 0.1)

        # Apply to full state
        return stabilization

    def apply_operators(self, state: SyntropicState) -> np.ndarray:
        """Apply syntropic operators based on human presence"""
        operator_contribution = np.zeros(20)

        for op in self.operators.values():
            weight = op.human_weight if state.human_presence else op.auto_weight

            # Apply operator to full state
            op_result = op.function(state.full_state)

            # Weight and accumulate
            operator_contribution += weight * op_result

        return operator_contribution

    def generate_stochastic_disturbance(self) -> np.ndarray:
        """Generate W_t stochastic disturbances"""
        return np.random.normal(0, 0.05, 20)

    def update_state(self, human_present: bool = None) -> SyntropicState:
        """Update state according to the syntropic manifold equation"""
        if human_present is not None:
            self.current_state.human_presence = human_present

        # Calculate components
        operator_effects = self.apply_operators(self.current_state)
        disturbances = self.generate_stochastic_disturbance()
        resonance_stabilization = self.calculate_resonance_stabilization(self.current_state)

        # State update equation
        # X_{t+1}^full = X_t^full + operator_effects + disturbances + resonance_stabilization
        new_full_state = (
            self.current_state.full_state +
            operator_effects +
            disturbances +
            resonance_stabilization
        )

        # Split back into network and logical components
        new_network = new_full_state[:10]
        new_logical = new_full_state[10:]

        # Update resonance based on new coherence
        new_coherence = np.dot(new_network, new_logical) / (
            np.linalg.norm(new_network) * np.linalg.norm(new_logical) + 1e-8
        )
        new_resonance = self.current_state.resonance * 0.9 + new_coherence * 0.1

        # Create new state
        new_state = SyntropicState(
            network_state=new_network,
            logical_state=new_logical,
            resonance=new_resonance,
            human_presence=self.current_state.human_presence,
            timestamp=time.time()
        )

        # Update history
        self.current_state = new_state
        self.history.append(new_state)

        return new_state

    def get_state_summary(self) -> Dict:
        """Get current state summary for visualization"""
        return {
            'network_coherence': float(np.mean(self.current_state.network_state)),
            'logical_coherence': float(np.mean(self.current_state.logical_state)),
            'resonance_level': float(self.current_state.resonance),
            'human_present': self.current_state.human_presence,
            'timestamp': self.current_state.timestamp,
            'operator_count': len(self.operators)
        }