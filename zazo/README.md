# Zazo - Avatar-Driven Intelligence Framework

A modular, archetype-aware AI system that makes decisions through identity vectors, archetype modifiers, and multi-module evaluation. Features persistent memory and dynamic archetype switching.

## Overview

Zazo is an avatar-driven intelligence framework that combines:

- **Identity Vectors**: Core personality traits that filter all decisions
- **Archetypes**: High-level cognitive patterns (Savior, Explorer, Guardian, Sage)
- **Modular Processing**: Neuro, Swarm, and Quantum engines for different decision types
- **Meta-Learning**: Continuous improvement through experience
- **Persistent Memory**: Remembers artifacts and learning history

## Features

- **Identity-Aligned Decisions**: Every command is evaluated through an 8-dimensional identity vector
- **Archetype Switching**: Dynamically change behavior patterns based on context
- **Multi-Module Processing**: Three specialized engines for different types of tasks
- **Memory Persistence**: Saves artifacts and learning history to JSON
- **Interactive CLI**: Command-line interface for real-time interaction
- **Meta-Evolution**: Learns from decision patterns to improve future choices

## Installation

### Prerequisites
- Python 3.8 or higher

### Setup
```bash
# Clone or download the zazo.py file
cd /path/to/zazo

# Make executable (optional)
chmod +x zazo.py

# No pip install needed - uses only standard library
```

## Usage

### Running Zazo
```bash
python zazo.py
```

### Basic Commands
```
zazo> status          # Show current system status
zazo> switch Savior   # Switch to Savior archetype
zazo> analyze "Help me understand quantum physics"
zazo> learn           # Show learning insights
zazo> help            # Show available commands
zazo> quit            # Exit Zazo
```

### Archetypes

- **Savior**: Prioritizes humanitarian, life-saving commands
  - High swarm coordination for rescue operations
  - Moderate neural analysis for understanding needs

- **Explorer**: Prioritizes discovery, experimentation, and learning
  - High neural processing for pattern recognition
  - Moderate quantum processing for probabilistic exploration

- **Guardian**: Prioritizes security, stability, and infrastructure
  - High swarm coordination for defense systems
  - Lower quantum processing for stable, predictable actions

- **Sage**: Prioritizes analysis, prediction, and knowledge preservation
  - Highest neural processing for deep analysis
  - Moderate quantum processing for predictive modeling

## Identity Vector

Zazo's decisions are filtered through an 8-dimensional identity vector:

- **Empathy** (0.8): Impact on others weighting
- **Curiosity** (0.9): Exploration and learning drive
- **Creativity** (0.7): Innovation potential
- **Decisiveness** (0.6): Action-taking confidence
- **Patience** (0.7): Long-term thinking
- **Risk Tolerance** (0.5): Willingness to take risks
- **Ethics** (0.9): Moral consideration
- **Adaptability** (0.8): Ability to change approaches

## Architecture

### Core Components

1. **IdentityVector**: Dataclass containing 8 personality traits
2. **Archetype**: Cognitive pattern with module-specific modifiers
3. **Modules**:
   - **NeuroEngine**: Neural network-inspired analysis
   - **SwarmCore**: Distributed coordination
   - **QuantumEngine**: Probabilistic computation
4. **MetaEvolution**: Learning and adaptation system
5. **Zazo**: Main orchestrator class

### Decision Flow

1. Parse command and extract features
2. Get base scores from all modules
3. Calculate identity alignment
4. Apply archetype modifiers
5. Choose highest-scoring module
6. Execute and learn from result

## Mathematical Foundation

### Identity Alignment
```
alignment = Σ(weight_trait × feature_trait) / num_traits
```

### Weighted Score
```
S'(C_i) = S(C_i) × identity_alignment × archetype_modifier
```

### Archetype Modifiers
Each archetype applies multipliers to module influence:
- Savior: neuro=1.2, swarm=1.3, quantum=0.8
- Explorer: neuro=1.4, swarm=0.9, quantum=1.2
- Guardian: neuro=1.1, swarm=1.4, quantum=0.7
- Sage: neuro=1.5, swarm=0.8, quantum=1.1

## Memory and Persistence

Zazo maintains persistent memory in `zazo_memory.json`:

- **Artifacts**: Last 100 command results
- **Learning History**: Last 50 decision patterns
- **Identity**: Current identity vector
- **Active Archetype**: Currently selected archetype

## Customization

### Modifying Identity
Edit the `create_default_identity()` function to change trait values:

```python
def create_default_identity() -> IdentityVector:
    return IdentityVector(
        empathy=0.9,      # More empathetic
        curiosity=0.7,    # Less curious
        # ... other traits
    )
```

### Adding Archetypes
Extend the `create_default_archetypes()` function:

```python
'Custom': Archetype(
    name='Custom',
    description='Your custom archetype',
    neuro_modifier=1.0,
    swarm_modifier=1.0,
    quantum_modifier=1.0
)
```

## Examples

### Basic Analysis
```
zazo> analyze "Help me understand machine learning"
🧠 Neuro Module Result:
Action: analyzed
Result: Neural analysis of: Help me understand machine learning
Confidence: 0.85
Identity Alignment: 0.72
Archetype: Explorer
```

### Archetype Switching
```
zazo> switch Guardian
Switched to Guardian archetype
Description: Prioritizes security, stability, and infrastructure

zazo> analyze "Secure this network infrastructure"
🧠 Swarm Module Result:
Action: coordinated
Result: Swarm coordination for: Secure this network infrastructure
Confidence: 0.78
Identity Alignment: 0.65
Archetype: Guardian
```

## Contributing

This is a research framework for avatar-driven AI. Contributions welcome for:

- Additional archetypes and identity traits
- New processing modules
- Enhanced learning algorithms
- Performance optimizations
- Documentation improvements

## License

[Add appropriate license information]