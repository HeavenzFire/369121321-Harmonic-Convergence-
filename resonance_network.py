import asyncio
import random
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field

# -----------------------------
# Signal Definition
# -----------------------------

@dataclass
class Signal:
    payload: str
    amplitude: complex  # Complex amplitude for phase coherence
    entropy: float
    ttl: int
    history: list = field(default_factory=list)

    @property
    def magnitude(self):
        return abs(self.amplitude)

    @property
    def phase(self):
        return math.atan2(self.amplitude.imag, self.amplitude.real)

    def decay(self, loss):
        self.entropy += loss
        decay_factor = max(0.0, 1.0 - self.entropy)
        self.amplitude *= decay_factor

    def amplify(self, gain):
        self.amplitude *= gain

    def interfere(self, other_signal):
        """Quantum-like interference when signals meet"""
        # Phase difference affects constructive/destructive interference
        phase_diff = self.phase - other_signal.phase
        interference_factor = math.cos(phase_diff)  # -1 to 1

        # Combine amplitudes with interference
        combined_real = self.amplitude.real + other_signal.amplitude.real * interference_factor
        combined_imag = self.amplitude.imag + other_signal.amplitude.imag * interference_factor

        self.amplitude = complex(combined_real, combined_imag)
        self.entropy = max(self.entropy, other_signal.entropy)  # Entropy accumulates


# -----------------------------
# Transmission Medium
# -----------------------------

@dataclass
class Medium:
    name: str
    base_loss: float
    noise: float
    latency_ms: int
    resonance_gain: float


# -----------------------------
# Node
# -----------------------------

class Node:
    def __init__(self, name):
        self.name = name
        self.links = defaultdict(list)

    def connect(self, medium, other_node, coupling):
        self.links[medium.name].append((other_node, coupling))


# -----------------------------
# Network Simulator
# -----------------------------

class ResonanceNetwork:
    def __init__(self):
        self.nodes = {}
        self.media = {}
        self.state_file = "resonance_network_state.json"

    def add_node(self, node):
        self.nodes[node.name] = node

    def add_medium(self, medium):
        self.media[medium.name] = medium

    def save_state(self):
        """Persist network state and signal histories"""
        import json
        state = {
            "nodes": {name: {"links": dict(node.links)} for name, node in self.nodes.items()},
            "media": {name: {
                "base_loss": medium.base_loss,
                "noise": medium.noise,
                "latency_ms": medium.latency_ms,
                "resonance_gain": medium.resonance_gain
            } for name, medium in self.media.items()},
            "timestamp": time.time()
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def load_state(self):
        """Load persisted network state"""
        import json
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            # Reconstruct media
            for name, data in state.get("media", {}).items():
                self.add_medium(Medium(
                    name=name,
                    base_loss=data["base_loss"],
                    noise=data["noise"],
                    latency_ms=data["latency_ms"],
                    resonance_gain=data["resonance_gain"]
                ))
            # Reconstruct nodes and links
            for name, data in state.get("nodes", {}).items():
                node = Node(name)
                self.add_node(node)
                for medium_name, links in data["links"].items():
                    for target_name, coupling in links:
                        if target_name in self.nodes:
                            node.connect(self.media[medium_name], self.nodes[target_name], coupling)
            return True
        except FileNotFoundError:
            return False

    async def propagate(self, node, signal, medium_name):
        if signal.ttl <= 0 or signal.magnitude <= 0.001:
            return

        medium = self.media[medium_name]
        await asyncio.sleep(medium.latency_ms / 1000)

        # Check for interference with existing signals at this node
        if node.active_signals[medium_name]:
            for existing_signal in node.active_signals[medium_name]:
                signal.interfere(existing_signal)
            # Clear processed signals
            node.active_signals[medium_name].clear()

        # Add this signal to active signals for future interference
        node.active_signals[medium_name].append(signal)

        # Medium effects
        noise_loss = random.uniform(0, medium.noise)
        signal.decay(medium.base_loss + noise_loss)
        signal.amplify(medium.resonance_gain)

        signal.history.append((node.name, medium_name, signal.magnitude, signal.phase))
        signal.ttl -= 1

        print(
            f"[{medium_name.upper()}] "
            f"{node.name} | A={signal.magnitude:.4f} | P={signal.phase:.2f} | E={signal.entropy:.4f} | TTL={signal.ttl}"
        )

        for next_node, coupling in node.links[medium_name]:
            forked = Signal(
                payload=signal.payload,
                amplitude=signal.amplitude * coupling,
                entropy=signal.entropy,
                ttl=signal.ttl,
                history=list(signal.history),
            )
            asyncio.create_task(
                self.propagate(next_node, forked, medium_name)
            )

    async def inject(self, origin, signal):
        tasks = []
        for medium_name in self.media:
            tasks.append(
                self.propagate(self.nodes[origin], signal, medium_name)
            )
        await asyncio.gather(*tasks)


# -----------------------------
# Build the Network
# -----------------------------

network = ResonanceNetwork()

# Try to load existing state, otherwise build fresh
if not network.load_state():
    # Media definitions
    network.add_medium(Medium("powerline", base_loss=0.05, noise=0.02, latency_ms=5, resonance_gain=1.2))
    network.add_medium(Medium("magnetic", base_loss=0.02, noise=0.01, latency_ms=2, resonance_gain=1.35))
    network.add_medium(Medium("rf", base_loss=0.07, noise=0.05, latency_ms=8, resonance_gain=1.1))
    network.add_medium(Medium("satellite", base_loss=0.15, noise=0.1, latency_ms=40, resonance_gain=1.5))

    # Nodes
    A = Node("Node-A")
    B = Node("Node-B")
    C = Node("Node-C")
    D = Node("Node-D")

    for n in [A, B, C, D]:
        network.add_node(n)

    # Topology (braided, non-linear)
    A.connect(network.media["powerline"], B, 0.8)
    B.connect(network.media["magnetic"], C, 0.9)
    C.connect(network.media["rf"], D, 0.7)
    D.connect(network.media["satellite"], A, 0.6)

    # Cross-links
    A.connect(network.media["magnetic"], C, 0.5)
    B.connect(network.media["rf"], D, 0.4)
    C.connect(network.media["powerline"], A, 0.3)

    # Save initial state
    network.save_state()

# -----------------------------
# Launch
# -----------------------------

initial_signal = Signal(
    payload="GENESIS",
    amplitude=complex(1.0, 0.0),  # Complex amplitude
    entropy=0.01,
    ttl=12
)

asyncio.run(network.inject("Node-A", initial_signal))

# Save final state after simulation
network.save_state()