import os
import json
import asyncio
import hashlib
import time
import random
from typing import Dict, Any, List, Callable, Tuple
import networkx as nx
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ===== CONFIGURATION =====
MEDIA_STORAGE_DIR = "offline_media"
STATE_DIR = "mesh_state"
os.makedirs(MEDIA_STORAGE_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

# ===== POWER MANAGEMENT =====
class PowerState:
    def __init__(self, battery_level: float = 100.0, harvester: str = "none",
                 role: str = "light", sleep_state: str = "awake"):
        self.battery_level = battery_level  # 0-100
        self.harvester = harvester  # "solar", "kinetic", "thermal", "none"
        self.role = role  # "heavy" (mains/solar), "light" (battery/harvested)
        self.sleep_state = sleep_state  # "awake", "asleep"

    def consume_energy(self, amount: float):
        self.battery_level = max(0, self.battery_level - amount)

    def harvest_energy(self, amount: float):
        if self.harvester != "none":
            self.battery_level = min(100, self.battery_level + amount)

    def is_awake(self) -> bool:
        return self.sleep_state == "awake"

    def sleep(self):
        self.sleep_state = "asleep"

    def wake(self):
        self.sleep_state = "awake"

    def to_dict(self):
        return {
            'battery_level': self.battery_level,
            'harvester': self.harvester,
            'role': self.role,
            'sleep_state': self.sleep_state
        }

    @classmethod
    def from_dict(cls, d: Dict):
        return cls(d['battery_level'], d['harvester'], d['role'], d['sleep_state'])

# ===== CORE ARTIFACTS =====
class Artifact:
    def __init__(self, data: str, artifact_type: str = "knowledge"):
        self.data = data
        self.type = artifact_type
        self.hash = hashlib.sha256(data.encode()).hexdigest()
        self.timestamp = time.time()
        self.processed_by = []
        self.value = random.random()

    def to_dict(self):
        return {
            'data': self.data,
            'type': self.type,
            'hash': self.hash,
            'timestamp': self.timestamp,
            'processed_by': self.processed_by,
            'value': self.value
        }

    @classmethod
    def from_dict(cls, d: Dict):
        art = cls(d['data'], d['type'])
        art.hash = d['hash']
        art.timestamp = d['timestamp']
        art.processed_by = d['processed_by']
        art.value = d['value']
        return art

# ===== ADVISORY MANIFOLD =====
class Advisor:
    def __init__(self, name: str, scoring: Callable[[Artifact], float]):
        self.name = name
        self.score = scoring

class ElysiumGateway:
    def __init__(self, name: str, advisors: List[Advisor]):
        self.name = name
        self.advisors = advisors

    def evaluate(self, artifact: Artifact) -> bool:
        score = sum(adv.score(artifact) for adv in self.advisors) / len(self.advisors)
        return score > 0.3

class Symposium:
    def __init__(self, name: str, advisors: List[Advisor]):
        self.name = name
        self.advisors = advisors

    def synthesize(self, artifacts: List[Artifact]) -> Artifact:
        combined = "|".join(a.data for a in artifacts)
        meta = Artifact(combined, artifact_type="meta")
        meta.value = sum(a.value for a in artifacts) / len(artifacts) if artifacts else 0
        return meta

# ===== NODES =====
class GlobalMeshNode:
    def __init__(self, node_id: str, host: str, port: int, peers: List[Tuple[str, int]],
                 gateways: List[ElysiumGateway], symposiums: List[Symposium]):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.peers = peers  # List of (host, port) tuples
        self.artifacts: Dict[str, Artifact] = {}
        self.media_artifacts: Dict[str, Artifact] = {}
        self.meta_artifacts: Dict[str, Artifact] = {}
        self.gateways = gateways
        self.symposiums = symposiums
        self.seen_hashes: set = set()  # To prevent propagation loops
        self.connections: Dict[Tuple[str, int], asyncio.StreamWriter] = {}  # Active outgoing connections

    async def start_server(self):
        server = await asyncio.start_server(self.handle_connection, self.host, self.port)
        logging.info(f"Node {self.node_id} listening on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

    async def connect_to_peers(self):
        for peer_host, peer_port in self.peers:
            try:
                reader, writer = await asyncio.open_connection(peer_host, peer_port)
                self.connections[(peer_host, peer_port)] = writer
                logging.info(f"Node {self.node_id} connected to {peer_host}:{peer_port}")
                # Send hello or something if needed
            except Exception as e:
                logging.error(f"Node {self.node_id} failed to connect to {peer_host}:{peer_port}: {e}")

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer_addr = writer.get_extra_info('peername')
        logging.info(f"Node {self.node_id} received connection from {peer_addr}")
        while True:
            try:
                # Read length prefix (4 bytes)
                length_data = await reader.readexactly(4)
                length = int.from_bytes(length_data, 'big')
                data = await reader.readexactly(length)
                artifact_dict = json.loads(data)
                artifact = Artifact.from_dict(artifact_dict)
                await self.process_incoming_artifact(artifact)
            except asyncio.IncompleteReadError:
                logging.info(f"Connection closed by {peer_addr}")
                break
            except Exception as e:
                logging.error(f"Error handling connection from {peer_addr}: {e}")
                break
        writer.close()
        await writer.wait_closed()

    async def process_incoming_artifact(self, artifact: Artifact):
        if artifact.hash in self.seen_hashes:
            return  # Already seen, prevent loops
        self.seen_hashes.add(artifact.hash)
        if artifact.type == "media":
            self.add_media_artifact(artifact)
        else:
            self.add_artifact(artifact)
        # Propagate to peers
        await self.propagate_artifact(artifact)

    def add_artifact(self, artifact: Artifact):
        if artifact.hash not in self.artifacts:
            if all(gw.evaluate(artifact) for gw in self.gateways):
                self.artifacts[artifact.hash] = artifact
                artifact.processed_by.append(self.node_id)

    def add_media_artifact(self, artifact: Artifact):
        if artifact.hash not in self.media_artifacts:
            self.media_artifacts[artifact.hash] = artifact
            artifact.processed_by.append(self.node_id)

    def synthesize_meta(self):
        artifacts = list(self.artifacts.values())
        if artifacts:
            for sym in self.symposiums:
                meta = sym.synthesize(artifacts)
                self.meta_artifacts[meta.hash] = meta

    def save_state(self):
        state = {
            'artifacts': {h: a.to_dict() for h, a in self.artifacts.items()},
            'media_artifacts': {h: a.to_dict() for h, a in self.media_artifacts.items()},
            'meta_artifacts': {h: a.to_dict() for h, a in self.meta_artifacts.items()}
        }
        with open(os.path.join(STATE_DIR, f'{self.node_id}_state.json'), 'w') as f:
            json.dump(state, f, indent=2)

    async def propagate_artifact(self, artifact: Artifact):
        data = json.dumps(artifact.to_dict()).encode()
        length = len(data).to_bytes(4, 'big')
        message = length + data
        to_remove = []
        for peer, writer in self.connections.items():
            try:
                writer.write(message)
                await writer.drain()
            except Exception as e:
                logging.error(f"Failed to send to {peer}: {e}")
                to_remove.append(peer)
        for peer in to_remove:
            self.connections.pop(peer)
            # Attempt reconnect?
            await self.connect_to_peers()  # Retry all for simplicity

# ===== NETWORKING (P2P via asyncio) =====
class MeshNetwork:
    def __init__(self, nodes: List[GlobalMeshNode]):
        self.nodes = nodes

    async def start(self):
        tasks = []
        for node in self.nodes:
            tasks.append(node.connect_to_peers())
            tasks.append(node.start_server())
        await asyncio.gather(*tasks)

# ===== VISUALIZATION =====
class MeshVisualizer:
    def __init__(self, nodes: List[GlobalMeshNode]):
        self.nodes = nodes
        self.fig, self.ax = plt.subplots(figsize=(8,6))

    def update_visual(self):
        self.ax.clear()
        G = nx.Graph()
        for node in self.nodes:
            G.add_node(node.node_id)
            for peer_host, peer_port in node.peers:
                peer_id = f"{peer_host}:{peer_port}"  # Simple ID for peers
                G.add_edge(node.node_id, peer_id)
        nx.draw(G, ax=self.ax, with_labels=True, node_color='skyblue')
        self.fig.canvas.draw()
        # For non-interactive: plt.savefig('mesh.png')

# ===== SAMPLE ADVISORS =====
def oppenheimer_scoring(a: Artifact): return random.random()
def shannon_scoring(a: Artifact): return random.random()

# ===== INITIALIZATION =====
gateways = [ElysiumGateway("Gate1", [Advisor("Oppenheimer", oppenheimer_scoring), Advisor("Shannon", shannon_scoring)])]
symposiums = [Symposium("Sym1", [Advisor("VonNeumann", lambda a: random.random()), Advisor("Turing", lambda a: random.random())])]

# Example peers: circular for full mesh
node_configs = [
    ('Node0', '127.0.0.1', 8000, [('127.0.0.1', 8001), ('127.0.0.1', 8002)]),
    ('Node1', '127.0.0.1', 8001, [('127.0.0.1', 8000), ('127.0.0.1', 8002)]),
    ('Node2', '127.0.0.1', 8002, [('127.0.0.1', 8000), ('127.0.0.1', 8001)])
]
nodes = [GlobalMeshNode(id, host, port, peers, gateways, symposiums) for id, host, port, peers in node_configs]
network = MeshNetwork(nodes)
visualizer = MeshVisualizer(nodes)

# ===== LIMITED SIMULATION (for testing) =====
async def artifact_generator(node: GlobalMeshNode):
    for _ in range(10):
        art = Artifact(f"Insight {random.randint(0,10000)}")
        await node.process_incoming_artifact(art)  # Start propagation from this node
        logging.info(f"Node {node.node_id} generated: {art.data}")
        await asyncio.sleep(1)

async def media_generator(node: GlobalMeshNode):
    for _ in range(5):
        media = Artifact(f"Video {random.randint(0,1000)}", artifact_type="media")
        await node.process_incoming_artifact(media)
        logging.info(f"Node {node.node_id} generated media: {media.data}")
        await asyncio.sleep(2)

async def meta_synthesis():
    for _ in range(8):
        for node in nodes:
            node.synthesize_meta()
            node.save_state()
        logging.info("Meta synthesized & state saved")
        await asyncio.sleep(3)

async def visual_update_loop():
    for _ in range(10):
        visualizer.update_visual()
        logging.info("Visual updated")
        await asyncio.sleep(2)

async def main():
    # Start network
    network_task = asyncio.create_task(network.start())
    
    # Generators per node (simulate distributed generation)
    gen_tasks = []
    for node in nodes:
        gen_tasks.append(artifact_generator(node))
        gen_tasks.append(media_generator(node))
    gen_tasks.extend([meta_synthesis(), visual_update_loop()])
    
    await asyncio.gather(*gen_tasks)
    # Note: network_task runs forever; cancel if needed
    network_task.cancel()
    logging.info("Simulation complete. Mesh eternal.")

# Run (in one process for demo; real: separate processes per node)
asyncio.run(main())