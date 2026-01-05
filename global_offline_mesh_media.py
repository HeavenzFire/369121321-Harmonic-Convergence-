import threading
import socket
import json
import time
import random
import hashlib
import os
from typing import Dict, Any, List
import tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ===== CONFIGURATION =====
MEDIA_STORAGE_DIR = "offline_media"  # Folder for cached videos
os.makedirs(MEDIA_STORAGE_DIR, exist_ok=True)

# ===== Global Mesh Node =====
class GlobalMeshNode:
    def __init__(self, name: str, port: int, discovery_port: int = 6000):
        self.name = name
        self.port = port
        self.discovery_port = discovery_port
        self.state: Dict[str, Dict[str, Any]] = {}  # Knowledge/artifact state
        self.media_state: Dict[str, Dict[str, Any]] = {}  # Media/video artifacts
        self.peers: List[int] = []
        self.lock = threading.Lock()
        self.artifact_counter = 1000

    # ===== TCP Server for Artifact Reception =====
    def start_server(self):
        def server():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', self.port))
            s.listen()
            while True:
                conn, _ = s.accept()
                data = conn.recv(8192*4)  # allow larger payloads for media metadata
                if data:
                    artifact = json.loads(data.decode())
                    if artifact.get("type") == "media":
                        self.receive_media_artifact(artifact)
                    else:
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
        artifact_id = str(artifact["id"])
        with self.lock:
            existing = self.state.get(artifact_id)
            if not existing or artifact["timestamp"] > existing["timestamp"]:
                self.state[artifact_id] = artifact
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

    # ===== Self-Healing =====
    def self_heal(self):
        while True:
            with self.lock:
                for artifact in list(self.state.values()):
                    self.broadcast_artifact(artifact)
                for media in list(self.media_state.values()):
                    self.broadcast_artifact(media)
            time.sleep(5)

    # ===== Peer Discovery =====
    def announce_presence(self):
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = json.dumps({"name": self.name, "port": self.port}).encode()
        while True:
            udp_sock.sendto(message, ('<broadcast>', self.discovery_port))
            time.sleep(3)

    def listen_for_peers(self):
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_sock.bind(('', self.discovery_port))
        while True:
            data, addr = udp_sock.recvfrom(1024)
            peer_info = json.loads(data.decode())
            peer_port = peer_info["port"]
            if peer_port != self.port and peer_port not in self.peers:
                self.peers.append(peer_port)

    # ===== Persistent State =====
    def save_state(self):
        with open(f"{self.name}_state.json", "w") as f:
            json.dump(self.state, f)
        with open(f"{self.name}_media.json", "w") as f:
            json.dump(self.media_state, f)

    # ===== Media Artifact Handling =====
    def add_media_artifact(self, video_id: str, title: str, file_path: str):
        hash_value = hashlib.sha256(video_id.encode()).hexdigest()
        artifact = {
            "id": hash_value,
            "type": "media",
            "video_id": video_id,
            "title": title,
            "file_path": file_path,
            "timestamp": time.time(),
            "processed_by": [self.name]
        }
        with self.lock:
            self.media_state[hash_value] = artifact
        self.broadcast_artifact(artifact)

    def receive_media_artifact(self, artifact: Dict[str, Any]):
        media_id = artifact["id"]
        with self.lock:
            existing = self.media_state.get(media_id)
            if not existing or artifact["timestamp"] > existing["timestamp"]:
                self.media_state[media_id] = artifact
                self.fetch_media_file(artifact)

    def fetch_media_file(self, artifact):
        # Attempt to copy the file from local peer storage (simplified)
        if os.path.exists(artifact["file_path"]):
            return  # Already have it
        # In real deployment, request file transfer from peers
        # Placeholder: mark as missing
        artifact["file_missing"] = True

# ===== GUI Visualization =====
class MeshVisualizer:
    def __init__(self, nodes: List[GlobalMeshNode]):
        self.nodes = nodes
        self.root = tk.Tk()
        self.root.title("Global Offline Mesh + Media Visualizer")
        self.fig, self.ax = plt.subplots(figsize=(7,7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()
        self.graph = nx.Graph()

    def update_graph(self):
        self.graph.clear()
        for node in self.nodes:
            total_artifacts = len(node.state) + len(node.media_state)
            self.graph.add_node(node.name, artifacts=total_artifacts)
            for peer_port in node.peers:
                peer_name = next((n.name for n in self.nodes if n.port == peer_port), None)
                if peer_name:
                    self.graph.add_edge(node.name, peer_name)
        self.ax.clear()
        pos = nx.spring_layout(self.graph)
        node_labels = {n: f"{n}\n{self.graph.nodes[n]['artifacts']} items" for n in self.graph.nodes}
        nx.draw(self.graph, pos, ax=self.ax, with_labels=True, labels=node_labels,
                node_color='lightgreen', node_size=1500, font_size=10)
        self.canvas.draw()
        self.root.after(1000, self.update_graph)

    def run(self):
        self.update_graph()
        self.root.mainloop()

# ===== Multi-Device Mesh Initialization =====
ports = [5001, 5002, 5003]
nodes = [GlobalMeshNode(f"Node{i+1}", port) for i, port in enumerate(ports)]

for node in nodes:
    node.start_server()
    threading.Thread(target=node.generate_new_artifacts, daemon=True).start()
    threading.Thread(target=node.self_heal, daemon=True).start()
    threading.Thread(target=node.announce_presence, daemon=True).start()
    threading.Thread(target=node.listen_for_peers, daemon=True).start()

# Seed initial media artifacts (simulate cached YouTube)
for i, node in enumerate(nodes):
    fake_video_path = os.path.join(MEDIA_STORAGE_DIR, f"video_{i+1}.mp4")
    # Create placeholder file
    with open(fake_video_path, "wb") as f:
        f.write(os.urandom(1024))  # 1KB dummy
    node.add_media_artifact(video_id=f"YT{i+1}", title=f"Offline Video {i+1}", file_path=fake_video_path)

# Seed initial knowledge artifacts
for i, node in enumerate(nodes):
    if not node.state:
        artifact = {
            "id": i+1,
            "data": f"Seed Insight #{i+1}",
            "processed_by": [node.name],
            "timestamp": time.time(),
            "value": random.random()
        }
        node.broadcast_artifact(artifact)

# ===== Run Visualizer =====
visualizer = MeshVisualizer(nodes)
visualizer.run()