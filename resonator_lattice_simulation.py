import os
import json
import asyncio
import hashlib
import time
import random
import threading
import socket
import struct
import numpy as np
from scipy.integrate import odeint
import qutip as qt
from typing import Dict, List, Tuple
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# CONFIG
STATE_DIR = "quantum_lattice_state"
os.makedirs(STATE_DIR, exist_ok=True)
BROADCAST_PORT = 12345

class ResonatorCircuit:
    def __init__(self, R=0.4, L=0.9, C=0.7):
        self.R, self.L, self.C = R, L, C
        self.state = [0.15, 0.0]

    def dynamics(self, state, t, Vin):
        V, I = state
        dVdt = I / self.C
        dIdt = (Vin - V - self.R * I) / self.L
        return [dVdt, dIdt]

    def amplify(self, inputs: List[float]) -> float:
        if not inputs: return 0.15
        Vin = np.mean(inputs)
        t = np.linspace(0, 0.6, 60)
        sol = odeint(self.dynamics, self.state, t, args=(Vin,))
        peak = np.max(np.abs(sol[:, 0]))
        self.state = sol[-1].tolist()
        return peak * 1.4

class QuantumResonator:
    def __init__(self):
        self.classical = ResonatorCircuit()
        self.quantum_state = qt.basis(2, 0)

    def quantum_amplify(self, value: float) -> float:
        phi = value * np.pi
        rx_gate = qt.rx(phi)
        amplified = rx_gate * self.quantum_state
        expect = qt.expect(qt.sigmax(), amplified)
        self.quantum_state = amplified
        return abs(expect) * 1.5 + self.classical.amplify([value])

    def entangle(self, other: qt.Qobj) -> qt.Qobj:
        psi = qt.tensor(self.quantum_state, other)
        bell = (qt.tensor(qt.basis(2,0), qt.basis(2,0)) + qt.tensor(qt.basis(2,1), qt.basis(2,1))).unit()
        return bell  # Simplified projection

    def heal_quantum(self, state: qt.Qobj) -> qt.Qobj:
        syndrome = abs(qt.expect(qt.sigmax(), state))
        if syndrome > 0.7:  # Threshold
            corrected = qt.sigmax() * state
            logging.info("QUANTUM HEALING ACTIVATED")
            return corrected.unit()
        return state

class QuantumSignal:
    def __init__(self, sid: int, data: str, origin: str, resonator: QuantumResonator):
        self.sid = sid
        self.data = data
        self.origin = origin
        self.hash = hashlib.sha256(f"{data}{sid}{origin}".encode()).hexdigest()
        self.timestamp = time.time()
        self.processed_by = [origin]
        self.base_value = random.uniform(0.3, 1.0)
        self.boosted_value = resonator.quantum_amplify(self.base_value)
        self.quantum_state = resonator.quantum_state

    def to_dict(self):
        return {
            'sid': self.sid, 'data': self.data, 'origin': self.origin,
            'hash': self.hash, 'timestamp': self.timestamp,
            'processed_by': self.processed_by, 'base_value': self.base_value,
            'boosted_value': self.boosted_value,
            'quantum_array': self.quantum_state.full().tolist()  # Safe serialize
        }

    @classmethod
    def from_dict(cls, d: Dict, resonator: QuantumResonator):
        sig = cls(d['sid'], d['data'], d['origin'], resonator)
        sig.hash = d['hash']
        sig.timestamp = d['timestamp']
        sig.processed_by = d['processed_by']
        sig.base_value = d['base_value']
        sig.boosted_value = d['boosted_value']
        sig.quantum_state = qt.Qobj(np.array(d['quantum_array']))
        return sig

class QuantumCircuitNode:
    def __init__(self, node_id: str, host: str = "127.0.0.1", port: int = 8000):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.resonator = QuantumResonator()
        self.signals: Dict[str, QuantumSignal] = {}
        self.blockchain: List[Dict] = [{'index': 0, 'hash': 'quantum_genesis', 'prev_hash': '0'}]
        self.pattern_graph = nx.Graph()
        self.peers: List[Tuple[str, int]] = []
        self.connections: Dict[Tuple[str, int], asyncio.StreamWriter] = {}
        self.lock = asyncio.Lock()
        self.discovery_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.discovery_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.discovery_sock.bind(('', BROADCAST_PORT))

    async def start_server(self):
        server = await asyncio.start_server(self.handle_peer, self.host, self.port)
        logging.info(f"{self.node_id} QUANTUM SERVER ONLINE @ {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

    async def discovery_loop(self):
        # Broadcaster
        async def broadcast():
            while True:
                msg = struct.pack('!4sH', socket.inet_aton(self.host), self.port)
                self.discovery_sock.sendto(msg, ('<broadcast>', BROADCAST_PORT))
                await asyncio.sleep(5)

        # Listener
        loop = asyncio.get_running_loop()
        while True:
            data, addr = await loop.run_in_executor(None, self.discovery_sock.recvfrom, 1024)
            peer_host = socket.inet_ntoa(data[:4])
            peer_port = struct.unpack('!H', data[4:6])[0]
            peer = (peer_host, peer_port)
            if peer != (self.host, self.port) and peer not in self.peers:
                self.peers.append(peer)
                await self.connect_to_peer(peer_host, peer_port)
                logging.info(f"{self.node_id} ENTANGLED NEW THREAD: {peer_host}:{peer_port}")

        await broadcast()

    async def connect_to_peer(self, peer_host: str, peer_port: int, retries=5):
        key = (peer_host, peer_port)
        for attempt in range(retries):
            try:
                reader, writer = await asyncio.open_connection(peer_host, peer_port)
                self.connections[key] = writer
                await self.sync_quantum_state(writer)
                asyncio.create_task(self.receive_from_peer(reader, writer))
                logging.info(f"{self.node_id} THREAD CONNECTED & ENTANGLED TO {key}")
                return
            except Exception as e:
                logging.warning(f"Attempt {attempt+1}/{retries} failed: {e}")
                await asyncio.sleep(2 ** attempt)
        logging.error(f"THREAD FRACTURE: Failed to entangle {key}")

    async def receive_from_peer(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer_addr = writer.get_extra_info('peername')
        while True:
            try:
                length_bytes = await reader.readexactly(4)
                length = struct.unpack('!I', length_bytes)[0]
                data = await reader.readexactly(length)
                msg = json.loads(data)
                await self.process_quantum_msg(msg, peer_addr)
            except asyncio.IncompleteReadError:
                break
            except Exception as e:
                logging.error(f"THREAD ERROR FROM {peer_addr}: {e}")
                break
        writer.close()
        await writer.wait_closed()
        self.connections.pop(peer_addr, None)
        # Heal: Reconnect
        await self.connect_to_peer(peer_addr[0], peer_addr[1])

    async def process_quantum_msg(self, msg: Dict, peer_addr):
        async with self.lock:
            if msg['type'] == 'signal':
                sig = QuantumSignal.from_dict(msg['signal'], self.resonator)
                healed_state = self.resonator.heal_quantum(sig.quantum_state)
                sig.quantum_state = healed_state
                entangled = self.resonator.entangle(healed_state)
                sig.boosted_value = self.resonator.quantum_amplify(sig.boosted_value)
                if sig.hash not in self.signals:
                    self.add_signal(sig)
                    await self.broadcast_signal(sig)
            elif msg['type'] == 'chain':
                self.resolve_chain(msg['chain'])

    def add_signal(self, signal: QuantumSignal):
        signal.processed_by.append(self.node_id)
        signal.boosted_value = self.resonator.quantum_amplify(signal.boosted_value)
        self.signals[signal.hash] = signal
        self.update_pattern_graph(signal)
        self.poi_mine(signal)

    def poi_mine(self, signal: QuantumSignal):
        block = {
            'index': len(self.blockchain),
            'signal_hash': signal.hash,
            'stake': signal.boosted_value,
            'prev_hash': self.blockchain[-1]['hash'],
            'nonce': 0,
            'timestamp': time.time()
        }
        diff = max(1, 4 - int(signal.boosted_value * 4))
        target = '0' * diff
        while not hashlib.sha256(json.dumps(block).encode()).hexdigest().startswith(target):
            block['nonce'] += 1
        block['hash'] = hashlib.sha256(json.dumps(block).encode()).hexdigest()
        self.blockchain.append(block)
        logging.info(f"{self.node_id} MINED BLOCK #{block['index']} | stake: {signal.boosted_value:.2f}")

    def update_pattern_graph(self, signal: QuantumSignal):
        self.pattern_graph.add_node(signal.hash, value=signal.boosted_value)
        for h in self.signals:
            if h != signal.hash:
                self.pattern_graph.add_edge(signal.hash, h)
        if nx.density(self.pattern_graph) > 0.5:
            for h in self.pattern_graph.nodes:
                self.signals[h].boosted_value *= 1.2
            logging.info(f"EMERGENT RESONANCE @ {self.node_id}")

    def resolve_chain(self, incoming_chain: List[Dict]):
        if len(incoming_chain) > len(self.blockchain):
            self.blockchain = incoming_chain
            logging.info(f"{self.node_id} adopted longer chain (len={len(incoming_chain)})")

    async def broadcast_signal(self, signal: QuantumSignal):
        msg = json.dumps({'type': 'signal', 'signal': signal.to_dict()}).encode()
        await self.broadcast(msg)

    async def sync_quantum_state(self, writer: asyncio.StreamWriter):
        msg = json.dumps({'type': 'chain', 'chain': self.blockchain}).encode()
        packet = struct.pack('!I', len(msg)) + msg
        writer.write(packet)
        await writer.drain()

    async def broadcast(self, message: bytes):
        packet = struct.pack('!I', len(message)) + message
        to_heal = []
        for key, writer in list(self.connections.items()):
            try:
                writer.write(packet)
                await writer.drain()
            except:
                to_heal.append(key)
        for key in to_heal:
            del self.connections[key]
            await self.connect_to_peer(key[0], key[1])

def spawn_quantum_generator(node: QuantumCircuitNode):
    sid = 0
    while True:
        sig = QuantumSignal(sid, f"Quantum Surge {sid}-{node.node_id}", node.node_id, node.resonator)
        asyncio.run_coroutine_threadsafe(node.propagate_signal(sig), asyncio.get_event_loop())
        node.add_signal(sig)
        sid += 1
        time.sleep(random.uniform(0.5, 2.0))

class LatticeGUI:
    def __init__(self, nodes: List[QuantumCircuitNode]):
        self.nodes = nodes
        self.root = tk.Tk()
        self.root.title("Quantum Resonator Lattice - Entangled Threads")
        self.fig, self.ax = plt.subplots(figsize=(10,8))
        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.update()

    def update(self):
        self.ax.clear()
        G = nx.Graph()
        for node in self.nodes:
            G.add_node(node.node_id, size=len(node.signals)*100)
        for node in self.nodes:
            for peer in node.connections:
                G.add_edge(node.node_id, f"{peer[0]}:{peer[1]}")
        nx.draw(G, with_labels=True, node_color='cyan', node_size=[G.nodes[n]['size'] for n in G.nodes])
        self.ax.set_title(f"Quantum Lattice Active | Chains: {[len(n.blockchain) for n in self.nodes]}")
        self.canvas.draw()
        self.root.after(2000, self.update)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Example: 3 nodes, full mesh via broadcast
    nodes = [
        QuantumCircuitNode("Q-Alpha", "127.0.0.1", 9000),
        QuantumCircuitNode("Q-Beta", "127.0.0.1", 9001),
        QuantumCircuitNode("Q-Gamma", "127.0.0.1", 9002)
    ]
    loop = asyncio.get_event_loop()
    tasks = []
    for node in nodes:
        tasks.append(node.start_server())
        tasks.append(node.discovery_loop())
        # 3 generators for surge
        for _ in range(3):
            threading.Thread(target=spawn_quantum_generator, args=(node,), daemon=True).start()
    asyncio.gather(*tasks)
    gui = LatticeGUI(nodes)
    threading.Thread(target=gui.run, daemon=True).start()
    loop.run_forever()