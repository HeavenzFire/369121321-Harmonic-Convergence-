#!/usr/bin/env python3
"""
Zazo - Avatar-Driven Intelligence Framework

A modular, archetype-aware AI system that makes decisions through identity vectors,
archetype modifiers, and multi-module evaluation. Features persistent memory and
dynamic archetype switching.
"""

import json
import os
import random
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class IdentityVector:
    """Represents the avatar's core identity traits."""
    empathy: float = 0.8      # Impact on others weighting
    curiosity: float = 0.9    # Exploration and learning drive
    creativity: float = 0.7   # Innovation potential
    decisiveness: float = 0.6 # Action-taking confidence
    patience: float = 0.7     # Long-term thinking
    risk_tolerance: float = 0.5  # Willingness to take risks
    ethics: float = 0.9       # Moral consideration
    adaptability: float = 0.8 # Ability to change approaches

    def alignment_score(self, command_features: Dict[str, float]) -> float:
        """Calculate how well a command aligns with this identity."""
        total_score = 0.0
        trait_count = 0

        for trait, weight in asdict(self).items():
            if trait in command_features:
                total_score += weight * command_features[trait]
                trait_count += 1

        return total_score / max(trait_count, 1)


@dataclass
class Archetype:
    """Represents a cognitive archetype with module modifiers."""
    name: str
    description: str
    neuro_modifier: float = 1.0    # NeuroEngine influence multiplier
    swarm_modifier: float = 1.0    # SwarmCore influence multiplier
    quantum_modifier: float = 1.0  # QuantumEngine influence multiplier

    def get_modifier(self, module_name: str) -> float:
        """Get the modifier for a specific module."""
        return getattr(self, f"{module_name}_modifier", 1.0)


class NeuroEngine:
    """Neural network-inspired decision making module."""

    def evaluate(self, command: str) -> float:
        """Evaluate command using neural-like pattern recognition."""
        # Simple heuristic: score based on complexity and keywords
        complexity = len(command.split()) / 10.0
        keywords = ['analyze', 'understand', 'learn', 'think', 'reason']
        keyword_score = sum(1 for word in keywords if word in command.lower()) / len(keywords)
        return min(1.0, complexity + keyword_score)

    def execute(self, command: str) -> Dict[str, Any]:
        """Execute neuro-style processing."""
        return {
            'module': 'neuro',
            'action': 'analyzed',
            'result': f"Neural analysis of: {command}",
            'confidence': self.evaluate(command),
            'timestamp': datetime.now().isoformat()
        }


class SwarmCore:
    """Distributed intelligence coordination module."""

    def evaluate(self, command: str) -> float:
        """Evaluate command for swarm coordination potential."""
        # Score based on collaborative keywords and scale
        collab_keywords = ['coordinate', 'distribute', 'collaborate', 'network', 'scale']
        scale_indicators = ['many', 'multiple', 'distributed', 'parallel']
        collab_score = sum(1 for word in collab_keywords if word in command.lower()) / len(collab_keywords)
        scale_score = sum(1 for word in scale_indicators if word in command.lower()) / len(scale_indicators)
        return min(1.0, collab_score + scale_score)

    def execute(self, command: str) -> Dict[str, Any]:
        """Execute swarm-style coordination."""
        return {
            'module': 'swarm',
            'action': 'coordinated',
            'result': f"Swarm coordination for: {command}",
            'confidence': self.evaluate(command),
            'timestamp': datetime.now().isoformat()
        }


class QuantumEngine:
    """Quantum-inspired probabilistic decision making."""

    def evaluate(self, command: str) -> float:
        """Evaluate command using quantum-like superposition scoring."""
        # Score based on uncertainty and probabilistic keywords
        uncertain_keywords = ['uncertain', 'probable', 'possible', 'quantum', 'superposition']
        complex_keywords = ['optimize', 'parallel', 'entangle', 'compute']
        uncertain_score = sum(1 for word in uncertain_keywords if word in command.lower()) / len(uncertain_keywords)
        complex_score = sum(1 for word in complex_keywords if word in command.lower()) / len(complex_keywords)
        return min(1.0, uncertain_score + complex_score + random.uniform(0, 0.3))  # Add quantum randomness

    def execute(self, command: str) -> Dict[str, Any]:
        """Execute quantum-style processing."""
        return {
            'module': 'quantum',
            'action': 'computed',
            'result': f"Quantum processing of: {command}",
            'confidence': self.evaluate(command),
            'timestamp': datetime.now().isoformat()
        }


class MetaEvolution:
    """Meta-learning and evolution module."""

    def __init__(self, modules: List[Any]):
        self.modules = modules
        self.learning_history = []

    def tune(self, scores: Dict[str, float]):
        """Learn from decision outcomes."""
        self.learning_history.append({
            'scores': scores,
            'chosen': max(scores, key=scores.get),
            'timestamp': datetime.now().isoformat()
        })

    def get_insights(self) -> Dict[str, Any]:
        """Extract learning insights."""
        if not self.learning_history:
            return {'insights': 'No learning history yet'}

        total_decisions = len(self.learning_history)
        module_counts = {}
        for entry in self.learning_history:
            module = entry['chosen']
            module_counts[module] = module_counts.get(module, 0) + 1

        return {
            'total_decisions': total_decisions,
            'module_preferences': module_counts,
            'most_used_module': max(module_counts, key=module_counts.get) if module_counts else None
        }


class Zazo:
    """Main Zazo avatar intelligence class."""

    def __init__(self, identity: IdentityVector, archetypes: Dict[str, Archetype]):
        self.identity = identity
        self.archetypes = archetypes
        self.active_archetype = archetypes.get('Savior', list(archetypes.values())[0])

        # Initialize modules
        self.neuro = NeuroEngine()
        self.swarm = SwarmCore()
        self.quantum = QuantumEngine()
        self.meta = MetaEvolution([self.neuro, self.swarm, self.quantum])

        # Memory and artifacts
        self.artifacts = []
        self.memory_file = os.path.join(os.path.dirname(__file__), 'zazo_memory.json')
        self.load_memory()

    def load_memory(self):
        """Load persistent memory from file."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.artifacts = data.get('artifacts', [])
                    self.meta.learning_history = data.get('learning_history', [])
            except json.JSONDecodeError:
                print("Warning: Could not load memory file. Starting fresh.")

    def save_memory(self):
        """Save current state to persistent memory."""
        data = {
            'artifacts': self.artifacts[-100:],  # Keep last 100 artifacts
            'learning_history': self.meta.learning_history[-50:],  # Keep last 50 learning entries
            'identity': asdict(self.identity),
            'active_archetype': self.active_archetype.name,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.memory_file, 'w') as f:
            json.dump(data, f, indent=2)

    def extract_command_features(self, command: str) -> Dict[str, float]:
        """Extract feature vector from command text."""
        features = {}
        command_lower = command.lower()

        # Empathy features
        if any(word in command_lower for word in ['help', 'care', 'support', 'empathy']):
            features['empathy'] = 0.8

        # Curiosity features
        if any(word in command_lower for word in ['explore', 'discover', 'learn', 'understand']):
            features['curiosity'] = 0.9

        # Creativity features
        if any(word in command_lower for word in ['create', 'innovate', 'design', 'imagine']):
            features['creativity'] = 0.7

        # Decisiveness features
        if any(word in command_lower for word in ['decide', 'choose', 'action', 'execute']):
            features['decisiveness'] = 0.8

        # Risk tolerance features
        if any(word in command_lower for word in ['risk', 'gamble', 'experiment', 'bold']):
            features['risk_tolerance'] = 0.6

        # Ethics features
        if any(word in command_lower for word in ['moral', 'right', 'good', 'ethical']):
            features['ethics'] = 0.9

        return features

    def dispatch(self, command: str) -> Dict[str, Any]:
        """Dispatch command through identity and archetype filtering."""
        # Get base scores from modules
        scores = {
            'neuro': self.neuro.evaluate(command),
            'swarm': self.swarm.evaluate(command),
            'quantum': self.quantum.evaluate(command)
        }

        # Extract command features for identity alignment
        command_features = self.extract_command_features(command)
        identity_alignment = self.identity.alignment_score(command_features)

        # Apply identity and archetype weighting
        weighted_scores = {}
        for module_name, base_score in scores.items():
            archetype_modifier = self.active_archetype.get_modifier(module_name)
            weighted_score = base_score * identity_alignment * archetype_modifier
            weighted_scores[module_name] = weighted_score

        # Choose the module with highest weighted score
        chosen_module = max(weighted_scores, key=weighted_scores.get)

        # Execute the chosen module
        result = getattr(self, chosen_module).execute(command)

        # Add decision metadata
        result.update({
            'identity_alignment': identity_alignment,
            'archetype': self.active_archetype.name,
            'scores': weighted_scores,
            'chosen_module': chosen_module
        })

        # Store artifact and learn
        self.artifacts.append(result)
        self.meta.tune(weighted_scores)
        self.save_memory()

        return result

    def switch_archetype(self, archetype_name: str) -> bool:
        """Switch to a different archetype."""
        if archetype_name in self.archetypes:
            self.active_archetype = self.archetypes[archetype_name]
            self.save_memory()
            return True
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            'identity': asdict(self.identity),
            'active_archetype': {
                'name': self.active_archetype.name,
                'description': self.active_archetype.description,
                'modifiers': {
                    'neuro': self.active_archetype.neuro_modifier,
                    'swarm': self.active_archetype.swarm_modifier,
                    'quantum': self.active_archetype.quantum_modifier
                }
            },
            'artifacts_count': len(self.artifacts),
            'learning_insights': self.meta.get_insights(),
            'available_archetypes': list(self.archetypes.keys())
        }


def create_default_archetypes() -> Dict[str, Archetype]:
    """Create the default set of archetypes."""
    return {
        'Savior': Archetype(
            name='Savior',
            description='Prioritizes humanitarian, life-saving commands',
            neuro_modifier=1.2,    # Higher neural analysis for understanding needs
            swarm_modifier=1.3,    # Strong coordination for rescue operations
            quantum_modifier=0.8   # Lower quantum for predictable, urgent actions
        ),
        'Explorer': Archetype(
            name='Explorer',
            description='Prioritizes discovery, experimentation, and learning',
            neuro_modifier=1.4,    # High neural for pattern recognition
            swarm_modifier=0.9,    # Moderate coordination
            quantum_modifier=1.2   # Higher quantum for probabilistic exploration
        ),
        'Guardian': Archetype(
            name='Guardian',
            description='Prioritizes security, stability, and infrastructure',
            neuro_modifier=1.1,    # Balanced analysis
            swarm_modifier=1.4,    # High coordination for defense
            quantum_modifier=0.7   # Lower quantum for stable, predictable actions
        ),
        'Sage': Archetype(
            name='Sage',
            description='Prioritizes analysis, prediction, and knowledge preservation',
            neuro_modifier=1.5,    # Highest neural for deep analysis
            swarm_modifier=0.8,    # Lower coordination needs
            quantum_modifier=1.1   # Moderate quantum for predictive modeling
        )
    }


def create_default_identity() -> IdentityVector:
    """Create a default balanced identity vector."""
    return IdentityVector(
        empathy=0.8,
        curiosity=0.9,
        creativity=0.7,
        decisiveness=0.6,
        patience=0.7,
        risk_tolerance=0.5,
        ethics=0.9,
        adaptability=0.8
    )


def main():
    """Main CLI interface for Zazo."""
    print("🤖 Zazo - Avatar-Driven Intelligence Framework")
    print("=" * 50)

    # Initialize Zazo with default identity and archetypes
    identity = create_default_identity()
    archetypes = create_default_archetypes()
    zazo = Zazo(identity, archetypes)

    print(f"Active Archetype: {zazo.active_archetype.name}")
    print(f"Identity Traits: {', '.join(f'{k}={v:.1f}' for k, v in asdict(identity).items())}")
    print("\nCommands:")
    print("  status          - Show current system status")
    print("  switch <type>   - Switch archetype (Savior, Explorer, Guardian, Sage)")
    print("  analyze <text>  - Analyze and process text")
    print("  learn           - Show learning insights")
    print("  help            - Show this help")
    print("  quit            - Exit Zazo")
    print()

    while True:
        try:
            command = input("zazo> ").strip()

            if not command:
                continue

            if command == 'quit':
                print("Saving memory and shutting down...")
                zazo.save_memory()
                break

            elif command == 'help':
                print("\nCommands:")
                print("  status          - Show current system status")
                print("  switch <type>   - Switch archetype (Savior, Explorer, Guardian, Sage)")
                print("  analyze <text>  - Analyze and process text")
                print("  learn           - Show learning insights")
                print("  help            - Show this help")
                print("  quit            - Exit Zazo")

            elif command == 'status':
                status = zazo.get_status()
                print("\n🤖 Zazo Status:")
                print(f"Active Archetype: {status['active_archetype']['name']}")
                print(f"Description: {status['active_archetype']['description']}")
                print(f"Artifacts: {status['artifacts_count']}")
                print(f"Available Archetypes: {', '.join(status['available_archetypes'])}")
                print("\nIdentity Vector:")
                for trait, value in status['identity'].items():
                    print(f"  {trait}: {value:.2f}")
                print("\nArchetype Modifiers:")
                for module, modifier in status['active_archetype']['modifiers'].items():
                    print(f"  {module}: {modifier:.1f}x")

            elif command.startswith('switch '):
                archetype_name = command[7:].strip()
                if zazo.switch_archetype(archetype_name):
                    print(f"Switched to {archetype_name} archetype")
                    print(f"Description: {zazo.active_archetype.description}")
                else:
                    print(f"Unknown archetype: {archetype_name}")
                    print(f"Available: {', '.join(zazo.archetypes.keys())}")

            elif command.startswith('analyze '):
                text = command[8:].strip()
                if text:
                    result = zazo.dispatch(text)
                    print(f"\n🧠 {result['module'].title()} Module Result:")
                    print(f"Action: {result['action']}")
                    print(f"Result: {result['result']}")
                    print(f"Confidence: {result['confidence']:.2f}")
                    print(f"Identity Alignment: {result['identity_alignment']:.2f}")
                    print(f"Archetype: {result['archetype']}")
                else:
                    print("Please provide text to analyze")

            elif command == 'learn':
                insights = zazo.meta.get_insights()
                print("\n📚 Learning Insights:")
                print(f"Total Decisions: {insights['total_decisions']}")
                if insights['module_preferences']:
                    print("Module Usage:")
                    for module, count in insights['module_preferences'].items():
                        print(f"  {module}: {count} times")
                    print(f"Most Used: {insights['most_used_module']}")
                else:
                    print("No learning history yet")

            else:
                # Treat as a general command to dispatch
                result = zazo.dispatch(command)
                print(f"\n🧠 {result['module'].title()} Module Result:")
                print(f"Action: {result['action']}")
                print(f"Result: {result['result']}")
                print(f"Confidence: {result['confidence']:.2f}")
                print(f"Identity Alignment: {result['identity_alignment']:.2f}")
                print(f"Archetype: {result['archetype']}")

        except KeyboardInterrupt:
            print("\nSaving memory and shutting down...")
            zazo.save_memory()
            break
        except Exception as e:
            print(f"Error: {e}")

    print("Goodbye! 👋")


if __name__ == '__main__':
    main()