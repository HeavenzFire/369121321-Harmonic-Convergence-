#!/usr/bin/env python3
"""
CLI Demo for the Minimal Decision Governor.

Demonstrates core functionality through command-line interface.
"""

import argparse
import json
import time
from minimal_governor import DecisionGovernor, DecisionContext
from minimal_rules import get_rules


def create_governor():
    """Create and return a configured DecisionGovernor."""
    rules = get_rules()
    return DecisionGovernor(rules=rules, max_risk=0.8, budget_limit=50.0)


def execute_data_analysis(governor, data_size_mb=50):
    """Execute a data analysis decision."""
    context = DecisionContext(
        intent='data_analysis',
        parameters={'data_size_mb': data_size_mb},
        risk_score=0.2,
        timestamp=time.time(),
        authority_level='medium',
        resource_cost=1.0
    )

    print(f"=== Executing Decision: {context.intent} ===")
    print(f"Parameters: {json.dumps(context.parameters, indent=2)}")
    print(f"Risk Score: {context.risk_score}")
    print(f"Authority: {context.authority_level}")
    print(f"Resource Cost: {context.resource_cost}")

    # Validate
    if not governor.validate_intent(context):
        print("❌ Decision validation failed")
        return False

    print("✅ Decision validated")

    # Log intent
    intent_hash = governor.log_intent(context)
    print(f"📝 Intent logged (hash: {intent_hash[:16]}...)")

    # Execute
    def analyze_data(ctx):
        size = ctx.parameters['data_size_mb']
        return f"Analysis complete: {size}MB dataset processed, insights generated"

    result = governor.execute_decision(analyze_data, context)

    print("🎯 Execution completed:")
    print(f"  Success: {result.success}")
    print(f"  Execution Time: {result.execution_time:.3f}s")
    print(f"  Resource Used: {result.resource_used}")
    if result.error_message:
        print(f"  Error: {result.error_message}")
    else:
        print(f"  Output: {result.output}")

    return result.success


def execute_model_inference(governor, model_name='gemma-2', temperature=0.5):
    """Execute a model inference decision."""
    context = DecisionContext(
        intent='model_inference',
        parameters={
            'model_name': model_name,
            'temperature': temperature,
            'input_text': 'Analyze the following data trends:'
        },
        risk_score=0.3,
        timestamp=time.time(),
        authority_level='medium',
        resource_cost=2.0
    )

    print(f"=== Executing Decision: {context.intent} ===")
    print(f"Parameters: {json.dumps(context.parameters, indent=2)}")
    print(f"Risk Score: {context.risk_score}")
    print(f"Authority: {context.authority_level}")
    print(f"Resource Cost: {context.resource_cost}")

    # Validate
    if not governor.validate_intent(context):
        print("❌ Decision validation failed")
        return False

    print("✅ Decision validated")

    # Log intent
    intent_hash = governor.log_intent(context)
    print(f"📝 Intent logged (hash: {intent_hash[:16]}...)")

    # Execute
    def run_inference(ctx):
        model = ctx.parameters['model_name']
        temp = ctx.parameters['temperature']
        return f"Inference with {model} (temp={temp}): Generated analysis and recommendations"

    result = governor.execute_decision(run_inference, context)

    print("🎯 Execution completed:")
    print(f"  Success: {result.success}")
    print(f"  Execution Time: {result.execution_time:.3f}s")
    print(f"  Resource Used: {result.resource_used}")
    if result.error_message:
        print(f"  Error: {result.error_message}")
    else:
        print(f"  Output: {result.output}")

    return result.success


def show_status(governor):
    """Show governor status."""
    status = governor.get_status()

    print("=== Governor Status ===")
    print(f"Budget Remaining: {status['budget_remaining']:.1f} / {status['budget_limit']:.1f}")
    print(f"Total Decisions: {status['total_decisions']}")
    print(f"Chains Integrity: {status['chains_status']['chains_integrity']}")
    print(f"Intent Chain Length: {status['chains_status']['intent_chain_length']}")
    print(f"Execution Chain Length: {status['chains_status']['execution_chain_length']}")
    print(f"Last Update: {time.ctime(status['timestamp'])}")


def show_chains(governor, limit=5):
    """Show recent chain entries."""
    print("=== Recent Intent Chain Entries ===")
    for i, entry in enumerate(governor.intent_chain[-limit:]):
        print(f"{i+1}. {entry['intent']} (risk: {entry['risk_score']}) - {entry['hash'][:16]}...")

    print("\n=== Recent Execution Chain Entries ===")
    for i, entry in enumerate(governor.execution_chain[-limit:]):
        success = "✅" if entry['success'] else "❌"
        print(f"{i+1}. {success} {entry['execution_time']:.3f}s - {entry['hash'][:16]}...")


def run_demo_sequence(governor):
    """Run a complete demo sequence."""
    print("🚀 Starting Minimal Decision Governor Demo")
    print("=" * 50)

    # Show initial status
    print("\n1. INITIAL STATUS")
    show_status(governor)

    # Execute data analysis
    print("\n2. DATA ANALYSIS DECISION")
    execute_data_analysis(governor, data_size_mb=75)

    # Execute model inference
    print("\n3. MODEL INFERENCE DECISION")
    execute_model_inference(governor, model_name='phi-3.5', temperature=0.3)

    # Execute another data analysis
    print("\n4. SECOND DATA ANALYSIS DECISION")
    execute_data_analysis(governor, data_size_mb=100)

    # Show chains
    print("\n5. CHAIN STATUS")
    show_chains(governor)

    # Show final status
    print("\n6. FINAL STATUS")
    show_status(governor)

    # Verify chains
    print("\n7. CHAIN VERIFICATION")
    verification = governor.verify_chains()
    print(f"Intent Chain Valid: {verification['intent_chain_valid']}")
    print(f"Execution Chain Valid: {verification['execution_chain_valid']}")
    print(f"Overall Integrity: {verification['chains_integrity']}")

    print("\n✨ Demo completed successfully!")
    print("The Decision Governor has demonstrated:")
    print("- Pre-decision validation")
    print("- Dual-chain cryptographic logging")
    print("- Resource budget management")
    print("- Chain integrity verification")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Minimal Decision Governor CLI Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python minimal_demo.py status
  python minimal_demo.py execute data_analysis --params '{"data_size_mb": 50}'
  python minimal_demo.py execute model_inference --model gemma-2 --temperature 0.5
  python minimal_demo.py chains
  python minimal_demo.py demo
        """
    )

    parser.add_argument('command', choices=['status', 'execute', 'chains', 'demo'],
                       help='Command to execute')

    # Execute subcommand arguments
    parser.add_argument('--intent', choices=['data_analysis', 'model_inference'],
                       help='Decision intent for execute command')
    parser.add_argument('--params', type=json.loads, default={},
                       help='Parameters as JSON string')
    parser.add_argument('--model', default='gemma-2',
                       help='Model name for inference')
    parser.add_argument('--temperature', type=float, default=0.5,
                       help='Temperature for inference')
    parser.add_argument('--data-size', type=int, default=50,
                       help='Data size in MB for analysis')

    args = parser.parse_args()

    # Create governor
    governor = create_governor()

    if args.command == 'status':
        show_status(governor)

    elif args.command == 'execute':
        if args.intent == 'data_analysis':
            execute_data_analysis(governor, args.data_size)
        elif args.intent == 'model_inference':
            execute_model_inference(governor, args.model, args.temperature)
        else:
            print("Please specify --intent (data_analysis or model_inference)")

    elif args.command == 'chains':
        show_chains(governor)

    elif args.command == 'demo':
        run_demo_sequence(governor)


if __name__ == '__main__':
    main()