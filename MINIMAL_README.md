# Minimal Decision Governor

A minimal, reproducible implementation of core accountability primitives for autonomous decision-making systems. This provides the essential components for pre-decision validation, dual-chain cryptographic logging, and deterministic replay in offline AI systems.

## Overview

The Decision Governor implements three fundamental architectural primitives:

1. **Pre-Decision Validation**: All decisions are validated against immutable rules before execution
2. **Dual-Chain Logging**: Separate cryptographic chains track intent and execution with SHA256 integrity
3. **Deterministic Replay**: Past decisions can be re-executed to verify consistency and detect divergence

## Architecture

```
[Decision Request] → [Pre-Validation] → [Intent Logging] → [Execution] → [Result Logging]
                      ↓                      ↓                      ↓
                 [Rules Check]        [Intent Chain]        [Execution Chain]
                 [Risk Assessment]    [SHA256 Hash]         [SHA256 Hash]
                 [Resource Budget]    [Chain Linkage]       [Chain Linkage]
```

## Core Components

### DecisionGovernor Class

The main governance engine that enforces accountability:

- **validate_intent()**: Checks decisions against immutable rules
- **log_intent()**: Records decision intent in cryptographic chain
- **execute_decision()**: Runs decision function and logs results
- **verify_chains()**: Validates integrity of both intent and execution chains
- **replay_decision()**: Deterministically re-executes past decisions

### DecisionContext

Data structure containing:
- Intent (decision type)
- Parameters (decision-specific data)
- Risk score (0.0 to 1.0)
- Authority level (low/medium/high/critical)
- Resource cost
- Timestamp

### Immutable Rules

Pre-defined constraints that cannot be modified at runtime:
- Allowed decision intents
- Authority requirements
- Parameter constraints
- Risk thresholds
- Resource costs

## Installation

No external dependencies required beyond Python 3.7+ standard library.

```bash
# Clone or download the files
# No installation needed - run directly
```

## Quick Start

### Basic Usage

```python
from minimal_governor import DecisionGovernor, DecisionContext
from minimal_rules import get_rules

# Initialize governor
governor = DecisionGovernor(rules=get_rules())

# Create decision context
context = DecisionContext(
    intent="data_analysis",
    parameters={"data_size_mb": 50},
    risk_score=0.2,
    timestamp=time.time(),
    authority_level="medium",
    resource_cost=1.0
)

# Validate and execute
if governor.validate_intent(context):
    intent_hash = governor.log_intent(context)
    result = governor.execute_decision(my_decision_function, context)
    print(f"Decision executed: {result.success}")
```

### CLI Demo

The included demo provides a command-line interface:

```bash
# Show governor status
python minimal_demo.py status

# Execute a data analysis decision
python minimal_demo.py execute data_analysis --params '{"data_size_mb": 50}'

# Execute model inference
python minimal_demo.py execute model_inference --model gemma-2

# Show recent chain entries
python minimal_demo.py chains

# Run full demo sequence
python minimal_demo.py demo
```

## Decision Types

The system supports these pre-defined decision intents:

- **data_analysis**: Analyze datasets with size and type constraints
- **model_inference**: Run model predictions with temperature controls
- **resource_allocation**: Allocate CPU/memory with usage limits
- **error_recovery**: Handle errors with retry logic

## Rules and Constraints

### Authority Levels
- **low**: Basic monitoring and analysis
- **medium**: Resource allocation and error recovery
- **high**: Learning updates and model modifications
- **critical**: System-level changes requiring oversight

### Risk Thresholds
- **low**: 0.2 (routine operations)
- **medium**: 0.5 (resource allocation)
- **high**: 0.8 (learning updates)
- **critical**: 0.95 (system modifications)

### Resource Budgeting
- Hourly budget limits prevent resource exhaustion
- Automatic budget reset every hour
- Cost multipliers based on operation complexity

## Cryptographic Integrity

### Dual-Chain Architecture
- **Intent Chain**: Records what the system intended to do
- **Execution Chain**: Records actual outcomes
- **SHA256 Hashing**: Each entry cryptographically linked to previous
- **Chain Verification**: Automatic integrity checking

### Replay Capability
- Deterministic re-execution of past decisions
- Divergence detection for non-deterministic behavior
- Historical decision reconstruction

## Testing

Run the included unit tests:

```bash
python -m pytest test_minimal_governor.py -v
```

## Example Output

```
=== Executing Decision: data_analysis ===
Parameters: {
  "data_size_mb": 50,
  "analysis_type": "statistical"
}
Risk Score: 0.2
Authority: medium
Resource Cost: 1.0
✅ Decision validated
📝 Intent logged (hash: a1b2c3d4...)
🎯 Execution completed:
  Success: true
  Execution Time: 0.045s
  Resource Used: 1.0
  Output: Analyzed data with parameters: {'data_size_mb': 50, 'analysis_type': 'statistical'}
```

## Integration

### With Existing Systems

The governor can wrap existing decision functions:

```python
def my_ai_decision(context):
    # Your existing AI logic here
    return ai_model.predict(context.parameters)

# Wrap with governance
governor = DecisionGovernor(get_rules())
result = governor.execute_decision(my_ai_decision, context)
```

### Extension Points

- Add custom decision intents in `minimal_rules.py`
- Implement domain-specific validation logic
- Extend chain storage to persistent databases
- Add real-time monitoring and alerting

## Security Considerations

- Rules are immutable at runtime
- Cryptographic verification prevents tampering
- Resource limits prevent denial-of-service
- Authority controls prevent unauthorized operations
- Emergency stop capability for critical situations

## Performance Characteristics

- Validation: < 1ms per decision
- Logging: ~5ms per decision (includes hashing)
- Chain verification: O(n) where n = chain length
- Replay: Equivalent to original decision execution time

## Limitations

- In-memory chain storage (extend for persistence)
- Synchronous execution (add async support if needed)
- Basic rule types (extend constraint system as needed)
- No distributed consensus (single-instance governance)

## Contributing

This is a minimal reference implementation. For production use:

1. Add persistent storage for chains
2. Implement distributed consensus for multi-node deployments
3. Add comprehensive monitoring and alerting
4. Extend rule system for domain-specific constraints
5. Add formal verification of decision functions

## License

This implementation is provided as a reference for accountable AI system design. Use and modify according to your needs.