import time
import hashlib
import json
import numpy as np
import threading
import os
import random
from collections import defaultdict
import serial
import glob
import math

STATE_DIR = "sovereign_intel"
INCOMING_DIR = "incoming_signals"
os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(INCOMING_DIR, exist_ok=True)

class SovereignIntelligence:
    def __init__(self, node_id):
        self.node_id = node_id
        self.local_signals = defaultdict(list)
        self.meta_convergences = {}
        self.healing_vectors = np.zeros(64)
        self.anchor_entropy = 0.0
        self.vector_clusters = []
        self.load_state()

    def load_state(self):
        try:
            with open(f"{STATE_DIR}/{self.node_id}_state.json", "r") as f:
                data = json.load(f)
                self.meta_convergences = data.get("metas", {})
                self.healing_vectors = np.array(data.get("vectors", [0]*64))
                self.vector_clusters = data.get("clusters", [])
        except FileNotFoundError:
            pass

    def save_state(self):
        data = {
            "metas": self.meta_convergences,
            "vectors": self.healing_vectors.tolist(),
            "clusters": self.vector_clusters
        }
        with open(f"{STATE_DIR}/{self.node_id}_state.json", "w") as f:
            json.dump(data, f)

    def ingest_signal(self, raw_text):
        h = hashlib.sha256(raw_text.encode()).hexdigest()
        timestamp = time.time()
        value = len(raw_text) * 0.01 + random.uniform(0, 0.3)
        self.local_signals[h].append({
            "text": raw_text,
            "ts": timestamp,
            "value": value
        })
        self.update_anchor_entropy()
        self.heal_vector(h)
        self.update_vector_clusters(h, value)

    def update_anchor_entropy(self):
        self.anchor_entropy = np.sin(time.time() / 3600) * 0.5 + 0.5

    def heal_vector(self, signal_hash):
        idx = int(signal_hash[:8], 16) % 64
        current = self.healing_vectors[idx]
        if abs(current) > 1.5:
            self.healing_vectors[idx] *= 0.7

    def update_vector_clusters(self, signal_hash, value):
        vector = np.array([int(signal_hash[i:i+2], 16) for i in range(0, 16, 2)]) / 255.0
        vector = np.append(vector, value)
        self.vector_clusters.append(vector.tolist())
        if len(self.vector_clusters) > 100:
            self.vector_clusters = self.vector_clusters[-100:]

    def converge_predictive(self):
        if not self.local_signals:
            return

        scored = []
        for signals in self.local_signals.values():
            latest = max(signals, key=lambda x: x["ts"])
            resonance = latest["value"] * (1 + self.anchor_entropy * 0.3)
            scored.append((latest["text"], resonance, latest["ts"]))

        top = sorted(scored, key=lambda x: x[1], reverse=True)[:3]
        if len(top) >= 2:
            meta_id = f"meta_{int(time.time()*1000)}"
            combined = " + ".join(t[0] for t in top)
            meta_value = sum(t[1] for t in top) * 1.15
            self.meta_convergences[meta_id] = {
                "combined": combined,
                "value": meta_value,
                "sources": len(top),
                "ts": time.time()
            }

        self.save_state()

    def watch_incoming_files(self):
        known_files = set()
        while True:
            current_files = set(glob.glob(f"{INCOMING_DIR}/*.txt"))
            new_files = current_files - known_files
            for filepath in new_files:
                try:
                    with open(filepath, "r") as f:
                        content = f.read().strip()
                        if content:
                            self.ingest_signal(content)
                except Exception as e:
                    pass
            known_files = current_files
            time.sleep(5)

    def listen_lora_serial(self):
        try:
            ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        self.ingest_signal(f"LoRa: {line}")
                time.sleep(0.1)
        except Exception as e:
            pass

    def run_forever(self):
        threading.Thread(target=self.watch_incoming_files, daemon=True).start()
        threading.Thread(target=self.listen_lora_serial, daemon=True).start()

        while True:
            if random.random() < 0.4:
                fake_signal = f"Community need: {random.choice(['food', 'legal aid', 'job lead', 'health info'])} at {time.strftime('%H:%M')}"
                self.ingest_signal(fake_signal)

            self.converge_predictive()
            time.sleep(random.uniform(4, 12))

if __name__ == "__main__":
    intel = SovereignIntelligence("Node_Alpha")
    threading.Thread(target=intel.run_forever, daemon=True).start()
    print("Intelligence Layer v0.1 — running quietly in background")
    while True:
        time.sleep(3600)