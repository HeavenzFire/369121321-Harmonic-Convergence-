import threading
import socket
import json
import time
import random
import os
from typing import Dict, Any, List
import tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ===== Global Mesh Node =====
class GlobalMeshNode:
    def __init__(self, name: str, port: int, discovery_port: int = 6000):
        self.name = name
        self.port = port
        self.discovery_port = discovery_port
        self.state: Dict[str, Dict[str, Any]] = {}
        self.meta_artifacts: Dict[str, Dict[str, Any]] = {}
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
            pass

    # ===== Artifact Handling =====
    def receive_artifact(self, artifact: Dict[str, Any]):
        artifact_id = str(artifact["id"])
        with self.lock:
            existing = self.state.get(artifact_id) or self.meta_artifacts.get(artifact_id)
            if not existing or artifact["timestamp"] > existing["timestamp"]:
                target = self.meta_artifacts if artifact.get("predicted") else self.state
                target[artifact_id] = artifact
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
                for artifact in list(self.state.values()) + list(self.meta_artifacts.values()):
                    self.broadcast_artifact(artifact)
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

    # ===== USB/Local Device Discovery =====
    def usb_discovery(self):
        """Scan /media, /mnt for mesh_state.json files and merge."""
        while True:
            for root in ["/media", "/mnt"]:
                if not os.path.exists(root):
                    continue
                for mount in os.listdir(root):
                    path = os.path.join(root, mount, "mesh_state.json")
                    if os.path.isfile(path):
                        try:
                            with open(path, "r") as f:
                                data = json.load(f)
                            with self.lock:
                                for aid, artifact in data.get("state", {}).items():
                                    if aid not in self.state or artifact["timestamp"] > self.state[aid]["timestamp"]:
                                        self.state[aid] = artifact
                                for mid, meta in data.get("meta_artifacts", {}).items():
                                    if mid not in self.meta_artifacts or meta["timestamp"] > self.meta_artifacts[mid]["timestamp"]:
                                        self.meta_artifacts[mid] = meta
                        except Exception:
                            continue
            time.sleep(10)

    # ===== Predictive Meta-Artifact Layer =====
    def predictive_forecasting(self):
        while True:
            with self.lock:
                if not self.state:
                    time.sleep(2)
                    continue
                growth_scores = {aid: artifact["value"]*len(artifact.get("processed_by", []))
                                 for aid, artifact in self.state.items()}
                top_artifacts = sorted(growth_scores.items(), key=lambda x: x[1], reverse=True)[:5]
                if not top_artifacts:
                    time.sleep(2)
                    continue
                predicted_meta_id = f"pred_meta_{int(time.time())}"
                predicted_meta_data = " + ".join([self.state[aid]["data"] for aid, _ in top_artifacts])
                predicted_value = sum([self.state[aid]["value"] for aid, _ in top_artifacts])*1.1
                predictive_meta = {
                    "id": predicted_meta_id,
                    "data": predicted_meta_data,
                    "processed_by": [self.name],
                    "timestamp": time.time(),
                    "value": predicted_value,
                    "predicted": True
                }
                self.meta_artifacts[predicted_meta_id] = predictive_meta
                self.broadcast_artifact(predictive_meta)
            time.sleep(5)

    # ===== Persistent State =====
    def save_state(self):
        with self.lock:
            with open(f"{self.name}_state.json", "w") as f:
                json.dump({"state": self.state, "meta_artifacts": self.meta_artifacts}, f)