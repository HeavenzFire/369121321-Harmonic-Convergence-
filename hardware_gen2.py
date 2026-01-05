# LEGION ∞.0: Hardware Gen2 Specifications
# RPi Zero 2W + LoRa + 5G + Satellite Fallback

from typing import Dict, List, Tuple
import time
import random

class HardwareGen2:
    """LEGION Gen2 Hardware Specifications and Capabilities"""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.specs = self._get_base_specs()
        self.connectivity_status = {
            "wifi": True,
            "lora": True,
            "g5": False,  # Requires additional modem
            "satellite": False  # Requires antenna
        }
        self.power_status = {
            "battery_level": 100.0,  # %
            "solar_input": 0.0,  # W
            "power_consumption": 2.5,  # W average
            "autonomy_days": 365
        }
        self.performance_metrics = {
            "verifications_per_day": 0,
            "coherence_calculations": 0,
            "mesh_connections": 0,
            "uptime_hours": 0
        }
        self.last_update = time.time()

    def _get_base_specs(self) -> dict:
        """Get base hardware specifications"""
        return {
            "processor": "Raspberry Pi Zero 2W",
            "cpu": "Quad-core ARM Cortex-A53 @ 1GHz",
            "ram": "512MB LPDDR2",
            "storage": "1TB NVMe SSD",
            "connectivity": {
                "wifi": "802.11ac 2.4/5GHz",
                "bluetooth": "5.0",
                "lora": "915MHz 20dBm (100km range)",
                "usb": "2x USB 2.0",
                "gpio": "40-pin header"
            },
            "power": {
                "battery": "18650 Li-ion 3400mAh",
                "solar": "5V 500mA panel",
                "consumption": "2.5W average, 5W peak",
                "autonomy": "365 days with solar"
            },
            "sensors": {
                "gps": "u-blox NEO-M8N",
                "imu": "MPU-6050",
                "temperature": "DS18B20",
                "light": "TSL2561"
            },
            "expansion": {
                "modem_5g": "Quectel RM500Q (optional)",
                "satellite": "Iridium 9603 (optional)",
                "camera": "Raspberry Pi Camera v3 (optional)"
            },
            "cost": 25.00,  # USD
            "dimensions": "65mm x 30mm x 5mm",
            "weight": "45g"
        }

    def get_specs(self) -> dict:
        """Get complete hardware specifications"""
        return self.specs.copy()

    def update_power_status(self, solar_input: float = None, consumption: float = None):
        """Update power status"""
        if solar_input is not None:
            self.power_status["solar_input"] = solar_input

        if consumption is not None:
            self.power_status["power_consumption"] = consumption

        # Calculate battery level
        net_power = self.power_status["solar_input"] - self.power_status["power_consumption"]
        battery_change = (net_power / 10) * (time.time() - self.last_update) / 3600  # % per hour
        self.power_status["battery_level"] = max(0, min(100,
            self.power_status["battery_level"] + battery_change))

        # Update autonomy estimate
        daily_consumption = self.power_status["power_consumption"] * 24
        daily_generation = self.power_status["solar_input"] * 8  # 8 hours sunlight
        if daily_generation > daily_consumption:
            self.power_status["autonomy_days"] = 365  # Unlimited with solar
        else:
            battery_capacity_wh = 3.7 * 3.4  # 3.7V * 3400mAh
            self.power_status["autonomy_days"] = battery_capacity_wh / (daily_consumption - daily_generation)

        self.last_update = time.time()

    def get_power_status(self) -> dict:
        """Get current power status"""
        return self.power_status.copy()

    def enable_5g_modem(self):
        """Enable 5G connectivity (requires additional hardware)"""
        self.connectivity_status["g5"] = True
        self.specs["cost"] += 50.0  # Additional cost
        print(f"📡 5G MODEM ENABLED: {self.node_id}")

    def enable_satellite(self):
        """Enable satellite connectivity (requires antenna)"""
        self.connectivity_status["satellite"] = True
        self.specs["cost"] += 200.0  # Additional cost
        print(f"🛰️ SATELLITE ENABLED: {self.node_id}")

    def get_connectivity_status(self) -> dict:
        """Get connectivity status"""
        return self.connectivity_status.copy()

    def calculate_range(self, target_node: 'HardwareGen2' = None) -> float:
        """Calculate communication range to target node"""
        if target_node is None:
            # Default ranges
            ranges = {
                "wifi": 50,  # meters
                "lora": 100000,  # 100km
                "g5": 1000,  # 1km
                "satellite": 10000000  # Global
            }
            return max(r for status, r in zip(self.connectivity_status.values(), ranges.values()) if status)
        else:
            # Calculate actual distance (simplified)
            # In real implementation, would use GPS coordinates
            return random.uniform(100, 100000)  # 100m to 100km

    def update_performance_metrics(self, verifications: int = 0, coherence_calcs: int = 0,
                                  mesh_connections: int = 0):
        """Update performance metrics"""
        self.performance_metrics["verifications_per_day"] += verifications
        self.performance_metrics["coherence_calculations"] += coherence_calcs
        self.performance_metrics["mesh_connections"] += mesh_connections
        self.performance_metrics["uptime_hours"] = (time.time() - self.last_update) / 3600

    def get_performance_metrics(self) -> dict:
        """Get performance metrics"""
        return self.performance_metrics.copy()

    def get_capabilities(self) -> dict:
        """Get hardware capabilities summary"""
        capabilities = {
            "verification_capacity": self._calculate_verification_capacity(),
            "communication_range_km": self.calculate_range() / 1000,
            "autonomy_days": self.power_status["autonomy_days"],
            "storage_tb": 1.0,
            "connectivity_types": [k for k, v in self.connectivity_status.items() if v],
            "power_autonomous": self.power_status["solar_input"] > self.power_status["power_consumption"]
        }
        return capabilities

    def _calculate_verification_capacity(self) -> int:
        """Calculate daily verification capacity based on hardware"""
        base_capacity = 10000  # Base verifications per day

        # Adjust for CPU performance
        cpu_multiplier = 1.0  # Zero 2W is baseline

        # Adjust for power status
        power_multiplier = min(1.0, self.power_status["battery_level"] / 100)

        # Adjust for connectivity (more connections = more capacity)
        connectivity_bonus = sum(self.connectivity_status.values()) * 0.1

        return int(base_capacity * cpu_multiplier * power_multiplier * (1 + connectivity_bonus))

    def simulate_operation(self, hours: int = 24):
        """Simulate hardware operation for specified hours"""
        print(f"🔄 SIMULATING {hours} HOURS OPERATION: {self.node_id}")

        for hour in range(hours):
            # Simulate solar input (varies by time of day)
            solar_input = max(0, 3.0 * (1 + 0.5 * (random.random() - 0.5)))  # 0-4.5W

            # Simulate consumption with some variation
            consumption = self.power_status["power_consumption"] * (0.8 + 0.4 * random.random())

            self.update_power_status(solar_input, consumption)

            # Simulate verifications
            verifications = random.randint(100, 500)
            coherence_calcs = verifications * 10
            mesh_connections = random.randint(5, 20)

            self.update_performance_metrics(verifications, coherence_calcs, mesh_connections)

            if hour % 6 == 0:  # Log every 6 hours
                print(f"  Hour {hour}: Battery {self.power_status['battery_level']:.1f}%, "
                      f"Verifications: {self.performance_metrics['verifications_per_day']}")

        print(f"✅ SIMULATION COMPLETE: {self.node_id}")
        print(f"   Final Battery: {self.power_status['battery_level']:.1f}%")
        print(f"   Total Verifications: {self.performance_metrics['verifications_per_day']}")
        print(f"   Autonomy: {self.power_status['autonomy_days']:.1f} days")

class HardwareFleet:
    """Manages a fleet of Gen2 hardware nodes"""

    def __init__(self):
        self.nodes: Dict[str, HardwareGen2] = {}
        self.fleet_stats = {
            "total_nodes": 0,
            "active_nodes": 0,
            "total_verification_capacity": 0,
            "average_battery_level": 0.0,
            "total_cost": 0.0
        }

    def add_node(self, node: HardwareGen2):
        """Add a node to the fleet"""
        self.nodes[node.node_id] = node
        self._update_fleet_stats()
        print(f"➕ NODE ADDED TO FLEET: {node.node_id}")

    def remove_node(self, node_id: str):
        """Remove a node from the fleet"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self._update_fleet_stats()
            print(f"➖ NODE REMOVED FROM FLEET: {node_id}")

    def _update_fleet_stats(self):
        """Update fleet statistics"""
        self.fleet_stats["total_nodes"] = len(self.nodes)
        self.fleet_stats["active_nodes"] = len([n for n in self.nodes.values()
                                               if n.power_status["battery_level"] > 10])

        total_capacity = sum(n._calculate_verification_capacity() for n in self.nodes.values())
        self.fleet_stats["total_verification_capacity"] = total_capacity

        if self.nodes:
            avg_battery = sum(n.power_status["battery_level"] for n in self.nodes.values()) / len(self.nodes)
            self.fleet_stats["average_battery_level"] = avg_battery

            total_cost = sum(n.specs["cost"] for n in self.nodes.values())
            self.fleet_stats["total_cost"] = total_cost

    def get_fleet_stats(self) -> dict:
        """Get fleet statistics"""
        return self.fleet_stats.copy()

    def simulate_fleet_operation(self, hours: int = 24):
        """Simulate operation of entire fleet"""
        print(f"🚀 SIMULATING FLEET OPERATION: {hours} hours, {len(self.nodes)} nodes")

        for node in self.nodes.values():
            node.simulate_operation(hours)

        self._update_fleet_stats()
        print("✅ FLEET SIMULATION COMPLETE")
        print(f"   Active Nodes: {self.fleet_stats['active_nodes']}/{self.fleet_stats['total_nodes']}")
        print(f"   Total Capacity: {self.fleet_stats['total_verification_capacity']:,} verifications/day")
        print(f"   Average Battery: {self.fleet_stats['average_battery_level']:.1f}%")

    def optimize_fleet(self):
        """Optimize fleet configuration"""
        # Enable 5G on high-traffic nodes
        high_traffic_nodes = sorted(self.nodes.values(),
                                  key=lambda n: n.performance_metrics["verifications_per_day"],
                                  reverse=True)[:len(self.nodes)//4]

        for node in high_traffic_nodes:
            if not node.connectivity_status["g5"]:
                node.enable_5g_modem()

        # Enable satellite on remote nodes (simplified)
        remote_nodes = random.sample(list(self.nodes.values()), len(self.nodes)//10)
        for node in remote_nodes:
            if not node.connectivity_status["satellite"]:
                node.enable_satellite()

        self._update_fleet_stats()
        print("⚡ FLEET OPTIMIZED: 5G and satellite enabled on strategic nodes")

    def get_node_by_location(self, lat: float, lon: float, radius_km: float = 10) -> List[HardwareGen2]:
        """Find nodes within radius of location (simplified)"""
        # In real implementation, would use actual GPS coordinates
        nearby_nodes = random.sample(list(self.nodes.values()), min(5, len(self.nodes)))
        return nearby_nodes