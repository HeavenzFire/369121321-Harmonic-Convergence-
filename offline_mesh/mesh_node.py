import asyncio
import socket
import json
import random
import time
import threading
from typing import Dict, List, Set
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class ContentCache:
    def __init__(self):
        self.cache = {
            "wikipedia": {
                "health": "Basic health guidelines from CDC...",
                "education": "GED prep resources...",
                "legal": "Texas eviction law basics..."
            },
            "job_boards": {
                "indeed": "Cached job listings for Texas...",
                "linkedin": "Professional networking tips..."
            },
            "legal_aid": {
                "eviction": "Texas eviction process guide...",
                "benefits": "Public assistance programs..."
            }
        }

    def get_content(self, category: str, topic: str) -> str:
        return self.cache.get(category, {}).get(topic, "Content not found")

    def add_content(self, category: str, topic: str, content: str):
        if category not in self.cache:
            self.cache[category] = {}
        self.cache[category][topic] = content

class LocalResonator:
    def __init__(self):
        self.signals = []

    def add_signal(self, signal: Dict):
        self.signals.append(signal)
        if len(self.signals) > 100:  # Keep last 100
            self.signals.pop(0)

    def predict_need(self) -> str:
        if not self.signals:
            return "general_health"
        # Simple prediction based on frequency
        categories = [s.get('category', 'general') for s in self.signals[-20:]]
        most_common = max(set(categories), key=categories.count)
        return most_common

class ESP32Node:
    def __init__(self, node_id: str, position: tuple, solar_power: bool = True):
        self.node_id = node_id
        self.position = position  # (lat, lon)
        self.solar_power = solar_power
        self.power_level = 100.0  # %
        self.content_cache = ContentCache()
        self.resonator = LocalResonator()
        self.peers: Set[str] = set()
        self.server_socket = None
        self.loop = None

    def calculate_distance(self, other_pos: tuple) -> float:
        # Simple Euclidean distance (in km)
        return ((self.position[0] - other_pos[0])**2 + (self.position[1] - other_pos[1])**2)**0.5

    def in_range(self, other_pos: tuple) -> bool:
        return self.calculate_distance(other_pos) <= 1.0  # 1km LoRa range

    async def start_server(self, port: int):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('localhost', port))
        self.server_socket.listen(5)
        self.server_socket.setblocking(False)

        logging.info(f"Node {self.node_id} listening on port {port}")

        while True:
            try:
                client, addr = await asyncio.get_event_loop().sock_accept(self.server_socket)
                asyncio.create_task(self.handle_client(client))
            except:
                await asyncio.sleep(0.1)

    async def handle_client(self, client):
        try:
            data = await asyncio.get_event_loop().sock_recv(client, 1024)
            message = json.loads(data.decode())
            response = await self.process_message(message)
            await asyncio.get_event_loop().sock_sendall(client, json.dumps(response).encode())
        except Exception as e:
            logging.error(f"Error handling client: {e}")
        finally:
            client.close()

    async def process_message(self, message: Dict) -> Dict:
        msg_type = message.get('type')
        if msg_type == 'content_request':
            category = message.get('category')
            topic = message.get('topic')
            content = self.content_cache.get_content(category, topic)
            return {'type': 'content_response', 'content': content}
        elif msg_type == 'signal_broadcast':
            signal = message.get('signal')
            self.resonator.add_signal(signal)
            return {'type': 'ack', 'status': 'received'}
        elif msg_type == 'peer_discovery':
            peer_id = message.get('peer_id')
            peer_pos = message.get('position')
            if self.in_range(peer_pos):
                self.peers.add(peer_id)
                return {'type': 'discovery_ack', 'peers': list(self.peers)}
            else:
                return {'type': 'out_of_range'}
        return {'type': 'error', 'message': 'Unknown message type'}

    async def broadcast_signal(self, signal: Dict):
        for peer in list(self.peers):
            try:
                reader, writer = await asyncio.open_connection('localhost', 8000 + int(peer.split('_')[1]))
                message = {'type': 'signal_broadcast', 'signal': signal}
                writer.write(json.dumps(message).encode())
                await writer.drain()
                response = await reader.read(1024)
                writer.close()
                await writer.wait_closed()
            except:
                self.peers.discard(peer)  # Remove unreachable peers

    def update_power(self):
        if self.solar_power:
            # Simulate solar charging during day
            hour = time.localtime().tm_hour
            if 6 <= hour <= 18:  # Daylight hours
                self.power_level = min(100.0, self.power_level + 2.0)
            else:
                self.power_level = max(0.0, self.power_level - 0.5)
        else:
            self.power_level = max(0.0, self.power_level - 1.0)

    async def run(self, port: int):
        await self.start_server(port)
        while True:
            self.update_power()
            if self.power_level > 10:  # Only operate if power > 10%
                prediction = self.resonator.predict_need()
                signal = {
                    'node_id': self.node_id,
                    'timestamp': time.time(),
                    'category': prediction,
                    'value': random.uniform(0.1, 1.0)
                }
                await self.broadcast_signal(signal)
            await asyncio.sleep(5)

class OfflineMesh:
    def __init__(self):
        self.nodes: Dict[str, ESP32Node] = {}

    def add_node(self, node_id: str, position: tuple, solar_power: bool = True):
        node = ESP32Node(node_id, position, solar_power)
        self.nodes[node_id] = node

    def discover_peers(self):
        for node_id, node in self.nodes.items():
            for other_id, other_node in self.nodes.items():
                if node_id != other_id and node.in_range(other_node.position):
                    node.peers.add(other_id)

    async def start_mesh(self):
        tasks = []
        for i, (node_id, node) in enumerate(self.nodes.items()):
            port = 8000 + i
            task = asyncio.create_task(node.run(port))
            tasks.append(task)
        await asyncio.gather(*tasks)

    def run_simulation(self, duration: int = 60):
        # Run for specified seconds
        async def simulate():
            self.discover_peers()
            await asyncio.wait_for(self.start_mesh(), timeout=duration)

        asyncio.run(simulate())