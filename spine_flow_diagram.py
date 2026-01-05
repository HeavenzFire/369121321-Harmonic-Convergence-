#!/usr/bin/env python3
"""
Spine Flow Diagram Generator
Creates visual representation of the 7-layer digital body architecture
with CLI integration, signal flows, and feedback loops.
"""

import graphviz
from pathlib import Path
import json

def create_spine_flow_diagram():
    """Generate the complete spine flow diagram"""

    # Initialize directed graph
    dot = graphviz.Digraph('spine_flow', comment='Digital Body Spine Flow Diagram')
    dot.attr(rankdir='TB', size='12,16')
    dot.attr('node', shape='box', style='filled', fontname='Arial', fontsize='10')
    dot.attr('edge', fontname='Arial', fontsize='8')

    # Define layer colors and properties
    layer_styles = {
        'root': {'fillcolor': '#8B4513', 'fontcolor': 'white'},  # Brown
        'sacral': {'fillcolor': '#FF6347', 'fontcolor': 'white'},  # Red
        'solar': {'fillcolor': '#FFD700', 'fontcolor': 'black'},  # Gold
        'heart': {'fillcolor': '#32CD32', 'fontcolor': 'white'},  # Green
        'throat': {'fillcolor': '#4169E1', 'fontcolor': 'white'},  # Blue
        'brow': {'fillcolor': '#9370DB', 'fontcolor': 'white'},  # Purple
        'crown': {'fillcolor': '#FFFFFF', 'fontcolor': 'black', 'color': 'gold', 'penwidth': '3'}  # White with gold border
    }

    # Define layers with detailed descriptions
    layers = {
        'root': 'ROOT\\n(Muladhara)\\nSurvival Core\\n• Process watchdog\\n• Memory persistence\\n• Integrity checks\\n• Fail-safe kill-switch',
        'sacral': 'SACRAL\\n(Svadhisthana)\\nMotion & Flow\\n• Task scheduler\\n• Event bus\\n• Message queues\\n• Vortex propagation',
        'solar': 'SOLAR PLEXUS\\n(Manipura)\\nAgency & Will\\n• Action selection\\n• Risk tolerance\\n• Priority arbitration\\n• Quadrupling circuits',
        'heart': 'HEART\\n(Anahata)\\nCoherence & Ethics\\n• Policy engine\\n• Harm minimization\\n• Trust scoring\\n• Alignment memory',
        'throat': 'THROAT\\n(Vishuddha)\\nExpression & Control\\n• Command parser\\n• NL compiler\\n• Output formatting\\n• Logging engine',
        'brow': 'BROW\\n(Ajna)\\nPerception & Models\\n• World model\\n• Simulation sandbox\\n• Multi-step planning\\n• Pattern detection',
        'crown': 'CROWN\\n(Sahasrara)\\nIntegration & Meta-Learning\\n• Reward adjustment\\n• Architecture tuning\\n• Plugin generation\\n• Strategy mutation'
    }

    # Add layer nodes
    for layer_id, label in layers.items():
        style = layer_styles[layer_id]
        dot.node(layer_id, label, **style)

    # CLI Input/Output nodes
    dot.node('cli_input', 'CLI INPUT\\nUser Commands\\n• Raw text\\n• Parameters\\n• Context', fillcolor='#F0F8FF', fontcolor='black')
    dot.node('cli_output', 'CLI OUTPUT\\nAgent Responses\\n• Formatted results\\n• Explanations\\n• State updates', fillcolor='#F0F8FF', fontcolor='black')

    # Signal type colors
    signal_colors = {
        'survival': 'red',
        'flow': 'orange',
        'agency': 'yellow',
        'ethics': 'green',
        'expression': 'blue',
        'perception': 'purple',
        'meta': 'gold'
    }

    # Main signal flow (bottom to top)
    main_flow = [
        ('root', 'sacral', 'survival', 'Survival signals\\nIntegrity status\\nMemory state'),
        ('sacral', 'solar', 'flow', 'Task flow\\nEvent propagation\\nVortex momentum'),
        ('solar', 'heart', 'agency', 'Action intent\\nRisk assessment\\nPriority decisions'),
        ('heart', 'throat', 'ethics', 'Policy constraints\\nTrust validation\\nEthical overrides'),
        ('throat', 'brow', 'expression', 'Parsed commands\\nFormatted output\\nCommunication signals'),
        ('brow', 'crown', 'perception', 'Simulation results\\nPattern insights\\nPlanning models')
    ]

    for source, target, sig_type, label in main_flow:
        dot.edge(source, target, label=label, color=signal_colors[sig_type], fontcolor=signal_colors[sig_type])

    # CLI integration flows
    dot.edge('cli_input', 'throat', 'Command Input\\nRaw text parsing', color='blue', style='bold')
    dot.edge('throat', 'cli_output', 'Response Output\\nFormatted results', color='blue', style='bold')

    # Feedback loops (top to bottom)
    feedback_loops = [
        ('crown', 'brow', 'meta', 'Meta-learning\\nModel updates\\nStrategy refinement'),
        ('brow', 'throat', 'perception', 'Planning feedback\\nSimulation insights'),
        ('throat', 'heart', 'expression', 'Execution results\\nCommunication feedback'),
        ('heart', 'solar', 'ethics', 'Ethical validation\\nPolicy updates'),
        ('solar', 'sacral', 'agency', 'Action outcomes\\nPriority adjustments'),
        ('sacral', 'root', 'flow', 'Flow status\\nResource feedback')
    ]

    for source, target, sig_type, label in feedback_loops:
        dot.edge(source, target, label=label, color=signal_colors[sig_type],
                fontcolor=signal_colors[sig_type], style='dashed', constraint='false')

    # Cross-layer resonance (vortex)
    resonance_connections = [
        ('sacral', 'brow', 'Vortex resonance\\nQuadrupling sync'),
        ('solar', 'crown', 'Agency amplification\\nMeta-decision flow'),
        ('heart', 'brow', 'Ethical simulation\\nValue-aligned planning')
    ]

    for source, target, label in resonance_connections:
        dot.edge(source, target, label=label, color='gold', style='dotted', constraint='false')

    # Emergency override paths
    override_paths = [
        ('root', 'solar', 'Survival override\\nHigh-threat veto'),
        ('heart', 'throat', 'Ethical override\\nHarm prevention'),
        ('crown', 'throat', 'Meta override\\nArchitecture changes')
    ]

    for source, target, label in override_paths:
        dot.edge(source, target, label=label, color='red', style='bold', constraint='false')

    # Legend
    with dot.subgraph(name='cluster_legend') as legend:
        legend.attr(label='Signal Types & Flow Patterns', style='filled', fillcolor='#F5F5F5')
        legend.node('legend_main', '↑ Main Flow\\n(Bottom → Top)', color='black')
        legend.node('legend_feedback', '↓ Feedback\\n(Top → Bottom)', color='black', style='dashed')
        legend.node('legend_resonance', '⟷ Resonance\\n(Cross-layer)', color='gold', style='dotted')
        legend.node('legend_override', '⚠ Override\\n(Emergency)', color='red', style='bold')

        legend.edge('legend_main', 'legend_feedback', style='invis')
        legend.edge('legend_feedback', 'legend_resonance', style='invis')
        legend.edge('legend_resonance', 'legend_override', style='invis')

    return dot

def generate_diagram():
    """Generate and save the spine flow diagram"""
    print("Generating spine flow diagram...")

    # Create diagram
    dot = create_spine_flow_diagram()

    # Save as DOT file
    dot_file = Path('/vercel/sandbox/spine_flow_diagram.dot')
    dot.save(dot_file)
    print(f"Saved DOT file: {dot_file}")

    # Generate PNG
    png_file = Path('/vercel/sandbox/spine_flow_diagram.png')
    dot.render(str(png_file.with_suffix('')), format='png', cleanup=True)
    print(f"Generated PNG diagram: {png_file}")

    # Verify files exist
    if dot_file.exists():
        print(f"✓ DOT file size: {dot_file.stat().st_size} bytes")
    if png_file.exists():
        print(f"✓ PNG file size: {png_file.stat().st_size} bytes")

    return png_file

if __name__ == '__main__':
    diagram_path = generate_diagram()
    print(f"\n🎉 Spine flow diagram generated successfully!")
    print(f"📁 Location: {diagram_path}")
    print("\n📊 Diagram includes:")
    print("  • 7-layer digital body architecture")
    print("  • CLI input/output integration")
    print("  • Signal flow patterns (main, feedback, resonance, override)")
    print("  • Color-coded signal types")
    print("  • Emergency override paths")
    print("  • Vortex resonance connections")