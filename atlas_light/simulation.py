import random
import time
from .gossip import forward_probability
from .routing import node_score

class MeshNode:
    def __init__(self, node_id: int, uptime: float, storage: float, energy: float):
        self.id = node_id
        self.uptime = uptime
        self.storage = storage
        self.energy = energy
        self.seen_content = {}  # cid -> last_seen_time
        self.score = node_score(uptime, storage, energy)

    def should_forward(self, cid: str, lam: float) -> bool:
        last_seen = self.seen_content.get(cid, 0)
        prob = forward_probability(last_seen, lam)
        return random.random() < prob

    def receive_content(self, cid: str):
        self.seen_content[cid] = time.time()

class MeshSimulation:
    def __init__(self, num_nodes: int = 50, lam: float = 0.01,
                 alpha: float = 0.5, beta: float = 0.4, gamma: float = 0.3):
        self.nodes = []
        for i in range(num_nodes):
            uptime = random.uniform(0.5, 1.0)
            storage = random.uniform(0.1, 1.0)
            energy = random.uniform(0.1, 0.5)
            node = MeshNode(i, uptime, storage, energy)
            node.score = node_score(uptime, storage, energy, alpha, beta, gamma)
            self.nodes.append(node)
        self.lam = lam
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def simulate_propagation(self, steps: int = 100) -> dict:
        """Simulate content propagation through the mesh"""
        # Start with one node having content
        content_cid = "test_content_123"
        self.nodes[0].receive_content(content_cid)

        reach_history = []
        for step in range(steps):
            # Sort nodes by score for routing priority
            sorted_nodes = sorted(self.nodes, key=lambda n: n.score, reverse=True)

            for node in sorted_nodes:
                if content_cid in node.seen_content:
                    # Try to forward to neighbors (simplified: random subset)
                    neighbors = random.sample([n for n in self.nodes if n != node], min(5, len(self.nodes)-1))
                    for neighbor in neighbors:
                        if neighbor.should_forward(content_cid, self.lam):
                            neighbor.receive_content(content_cid)

            # Count reached nodes
            reached = sum(1 for n in self.nodes if content_cid in n.seen_content)
            reach_history.append(reached)

        final_reach = reach_history[-1]
        convergence_step = next((i for i, r in enumerate(reach_history) if r == len(self.nodes)), steps)

        return {
            "final_reach": final_reach,
            "total_nodes": len(self.nodes),
            "convergence_step": convergence_step,
            "reach_percentage": final_reach / len(self.nodes),
            "parameters": {
                "lam": self.lam,
                "alpha": self.alpha,
                "beta": self.beta,
                "gamma": self.gamma
            }
        }