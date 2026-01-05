import threading
import socket
import json
import time
import random
import os
from typing import Dict, Any, List

ARTIFACTS_FILE = "mesh_state.json"

class GlobalMeshNode:
    def __init__(self, name, port, storage_file=ARTIFACTS_FILE):
        self.name = name
        self.port = port
        self.peers: List[int] = []
        self.state: Dict[int, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        self.artifact_counter = 1000
        self.storage_file = storage_file
        self.load_state()

    # ===== Persistent Storage =====
    def save_state(self):
        with self.lock:
            with open(self.storage_file, "w") as f:
                json.dump(self.state, f)

    def load_state(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r") as f:
                try:
                    self.state = json.load(f)
                    self.artifact_counter = max(map(int, self.state.keys()), default=1000)+1
                except:
                    self.state = {}

    # ===== TCP Server =====
    def start_server(self):
        def server():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('0.0.0.0', self.port))
            s.listen()
            print(f"[{self.name}] Listening on port {self.port}")
            while True:
                conn, addr = s.accept()
                data = conn.recv(8192)
                if data:
                    artifact = json.loads(data.decode())
                    self.receive_artifact(artifact)
                conn.close()
        threading.Thread(target=server, daemon=True).start()

    # ===== Peer Communication =====
    def broadcast_artifact(self, artifact: Dict[str, Any]):
        self.save_state()
        for peer_port in self.peers:
            threading.Thread(target=self.send_to_peer, args=(peer_port, artifact), daemon=True).start()

    def send_to_peer(self, peer_port: int, artifact: Dict[str, Any]):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', peer_port))
            s.send(json.dumps(artifact).encode())
            s.close()
        except ConnectionRefusedError:
            pass  # Peer offline

    # ===== Artifact Handling =====
    def receive_artifact(self, artifact: Dict[str, Any]):
        artifact_id = artifact["id"]
        with self.lock:
            existing = self.state.get(str(artifact_id))
            if not existing or artifact["timestamp"] > existing["timestamp"]:
                self.state[str(artifact_id)] = artifact
                self.evolve_artifact(artifact)

    def evolve_artifact(self, artifact):
        artifact["processed_by"] = artifact.get("processed_by", []) + [self.name]
        artifact["timestamp"] = time.time()
        artifact["value"] = artifact.get("value", 0) + random.random()
        self.broadcast_artifact(artifact)

    # ===== Autonomous Artifact Generation =====
    def generate_new_artifacts(self):
        while True:
            new_id = self.artifact_counter
            artifact = {
                "id": new_id,
                "data": f"Global Insight #{new_id}",
                "processed_by": [self.name],
                "timestamp": time.time(),
                "value": random.random()
            }
            self.artifact_counter += 1
            with self.lock:
                self.state[str(new_id)] = artifact
            self.broadcast_artifact(artifact)
            time.sleep(random.uniform(1, 2))

    # ===== Self-Healing & Artifact Propagation =====
    def self_heal(self):
        while True:
            with self.lock:
                for artifact in list(self.state.values()):
                    self.broadcast_artifact(artifact)
            time.sleep(5)

    # ===== Peer Discovery =====
    def add_peer(self, peer_port: int):
        if peer_port not in self.peers:
            self.peers.append(peer_port)

# ===== Multi-Device Mesh Initialization =====
ports = [5001, 5002, 5003, 5004, 5005, 5006]
nodes = [GlobalMeshNode(f"Node{i+1}", port) for i, port in enumerate(ports)]

# Fully connected dynamic peers
for node in nodes:
    node.peers = [p for p in ports if p != node.port]

# Start servers and autonomous threads
for node in nodes:
    node.start_server()
    threading.Thread(target=node.generate_new_artifacts, daemon=True).start()
    threading.Thread(target=node.self_heal, daemon=True).start()

# Seed initial artifacts if state empty
for i, node in enumerate(nodes):
    if not node.state:
        seed_artifact = {
            "id": i+1,
            "data": f"Seed Insight #{i+1}",
            "processed_by": [node.name],
            "timestamp": time.time(),
            "value": random.random()
        }
        node.broadcast_artifact(seed_artifact)

# ===== Continuous Monitoring =====
try:
    while True:
        time.sleep(5)
        print("\n--- Global Mesh Summary ---")
        for node in nodes:
            print(f"[{node.name}] Total artifacts: {len(node.state)}")
except KeyboardInterrupt:
    print("Global offline mesh stopped manually.")