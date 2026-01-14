#!/usr/bin/env python3
"""
HEAVENZFIRE SYNTHROPIC NETWORK AGENT
====================================

Real-time syntropic operator application for network optimization.
Implements operators: J (Join/Observe), C (Contain), R (Reset), H (Heal), O (Optimize), M (Modulate)

Architecture:
- Monitors network interface metrics (delay, queue depth, packet loss)
- Applies syntropic operators based on thresholds and human approval
- Logs all actions immutably for audit trails
- Coordinates with other nodes via message bus (RabbitMQ)
- Exports metrics to Prometheus for dashboards

Safety: All destructive operations require human-in-the-loop approval.
"""

import subprocess
import time
import json
import os
import sys
from datetime import datetime
import argparse
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_INTERFACE = "eth0"
MAX_DELAY_MS = 50
MAX_QUEUE_PACKETS = 1000
MONITORING_INTERVAL = 5  # seconds
LOG_FILE = "syntropic_log.jsonl"

# Syntropic Operators
class SyntropicOperators:
    """Implements the six syntropic operators for network optimization."""

    def __init__(self, interface: str = DEFAULT_INTERFACE):
        self.interface = interface
        self.human_approval_required = True  # Safety flag

    def J(self) -> Dict[str, Any]:
        """Join/Observe: Read-only monitoring of current queue state."""
        try:
            output = subprocess.check_output(
                ["tc", "-s", "qdisc", "show", "dev", self.interface],
                stderr=subprocess.STDOUT
            ).decode()
            return {"operator": "J", "status": "success", "data": output.strip()}
        except subprocess.CalledProcessError as e:
            return {"operator": "J", "status": "error", "error": str(e)}

    def C(self, delay: float) -> Dict[str, Any]:
        """Contain: Reduce interval and target to contain latency spikes."""
        if delay > MAX_DELAY_MS:
            if self.human_approval_required:
                logger.info("Operator C requires human approval for delay containment")
                return {"operator": "C", "status": "pending_approval", "delay": delay}

            try:
                subprocess.run([
                    "tc", "qdisc", "change", "dev", self.interface,
                    "root", "fq_codel", "interval", "50ms", "target", "5ms"
                ], check=True)
                return {"operator": "C", "status": "applied", "delay": delay}
            except subprocess.CalledProcessError as e:
                return {"operator": "C", "status": "error", "error": str(e)}
        return {"operator": "C", "status": "no_action", "delay": delay}

    def R(self) -> Dict[str, Any]:
        """Reset: Clear and reinitialize queue discipline."""
        if self.human_approval_required:
            logger.info("Operator R requires human approval for queue reset")
            return {"operator": "R", "status": "pending_approval"}

        try:
            subprocess.run([
                "tc", "qdisc", "del", "dev", self.interface, "root"
            ], check=True)
            # Reinitialize with fq_codel
            subprocess.run([
                "tc", "qdisc", "add", "dev", self.interface, "root", "fq_codel",
                "interval", "100ms", "target", "5ms", "quantum", "1514", "flows", "1024", "ecn"
            ], check=True)
            return {"operator": "R", "status": "applied"}
        except subprocess.CalledProcessError as e:
            return {"operator": "R", "status": "error", "error": str(e)}

    def H(self) -> Dict[str, Any]:
        """Heal: Increase flows and quantum for better flow scheduling."""
        if self.human_approval_required:
            logger.info("Operator H requires human approval for flow healing")
            return {"operator": "H", "status": "pending_approval"}

        try:
            subprocess.run([
                "tc", "qdisc", "change", "dev", self.interface,
                "root", "fq_codel", "quantum", "1514", "flows", "2048"
            ], check=True)
            return {"operator": "H", "status": "applied"}
        except subprocess.CalledProcessError as e:
            return {"operator": "H", "status": "error", "error": str(e)}

    def O(self) -> Dict[str, Any]:
        """Optimize: Enable ECN and adjust parameters for efficiency."""
        if self.human_approval_required:
            logger.info("Operator O requires human approval for optimization")
            return {"operator": "O", "status": "pending_approval"}

        try:
            subprocess.run([
                "tc", "qdisc", "change", "dev", self.interface,
                "root", "fq_codel", "ecn"
            ], check=True)
            return {"operator": "O", "status": "applied"}
        except subprocess.CalledProcessError as e:
            return {"operator": "O", "status": "error", "error": str(e)}

    def M(self) -> Dict[str, Any]:
        """Modulate: Dynamically adjust interval based on conditions."""
        if self.human_approval_required:
            logger.info("Operator M requires human approval for modulation")
            return {"operator": "M", "status": "pending_approval"}

        try:
            subprocess.run([
                "tc", "qdisc", "change", "dev", self.interface,
                "root", "fq_codel", "interval", "75ms"
            ], check=True)
            return {"operator": "M", "status": "applied"}
        except subprocess.CalledProcessError as e:
            return {"operator": "M", "status": "error", "error": str(e)}

class NetworkMonitor:
    """Monitors network interface metrics."""

    def __init__(self, interface: str = DEFAULT_INTERFACE):
        self.interface = interface

    def get_queue_stats(self) -> Dict[str, Any]:
        """Extract queue statistics from tc output."""
        try:
            output = subprocess.check_output([
                "tc", "-s", "qdisc", "show", "dev", self.interface
            ]).decode()

            # Parse basic stats (simplified - in production, use more robust parsing)
            stats = {
                "backlog": 0,
                "drops": 0,
                "overlimits": 0,
                "requeues": 0
            }

            # Extract backlog
            if "backlog" in output:
                # Simple parsing - production would use regex
                lines = output.split('\n')
                for line in lines:
                    if "backlog" in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "backlog":
                                stats["backlog"] = int(parts[i+1].rstrip("b"))
                                break

            return stats
        except subprocess.CalledProcessError:
            return {"error": "Failed to get queue stats"}

    def measure_latency(self) -> float:
        """Measure network latency (simplified ping-based approach)."""
        try:
            # Ping localhost as proxy for interface latency
            result = subprocess.run([
                "ping", "-c", "1", "-W", "1", "127.0.0.1"
            ], capture_output=True, text=True, timeout=2)

            if result.returncode == 0:
                # Extract time from "time=1.23 ms"
                output = result.stdout
                if "time=" in output:
                    time_str = output.split("time=")[1].split()[0]
                    return float(time_str)
            return 0.0
        except (subprocess.TimeoutExpired, ValueError):
            return 999.0  # High latency indicator

class ImmutableLogger:
    """Immutable append-only logging system."""

    def __init__(self, log_file: str = LOG_FILE):
        self.log_file = log_file

    def log_event(self, event: Dict[str, Any]) -> None:
        """Append event to immutable log."""
        event["timestamp"] = datetime.utcnow().isoformat() + "Z"
        event["node_id"] = os.environ.get("NODE_ID", "unknown")

        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")

        logger.info(f"Logged event: {event.get('operator', 'system')} - {event.get('status', 'unknown')}")

class MessageBus:
    """Multi-node coordination via RabbitMQ."""

    def __init__(self, host: str = "localhost"):
        self.host = host
        self.connection = None
        self.channel = None

    def connect(self):
        """Connect to RabbitMQ (optional dependency)."""
        try:
            import pika
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange='syntropic', exchange_type='fanout')
            logger.info("Connected to message bus")
        except ImportError:
            logger.warning("RabbitMQ not available - running in standalone mode")

    def broadcast_state(self, state: Dict[str, Any]):
        """Broadcast state to other nodes."""
        if self.channel:
            try:
                self.channel.basic_publish(
                    exchange='syntropic',
                    routing_key='',
                    body=json.dumps(state)
                )
            except Exception as e:
                logger.error(f"Failed to broadcast state: {e}")

def main():
    parser = argparse.ArgumentParser(description="HEAVENZFIRE Syntropic Network Agent")
    parser.add_argument("--interface", default=DEFAULT_INTERFACE, help="Network interface to monitor")
    parser.add_argument("--no-human-approval", action="store_true", help="Disable human approval requirement (use with caution)")
    parser.add_argument("--rabbitmq-host", default="localhost", help="RabbitMQ host for multi-node coordination")
    parser.add_argument("--log-file", default=LOG_FILE, help="Immutable log file path")

    args = parser.parse_args()

    # Initialize components
    operators = SyntropicOperators(args.interface)
    if args.no_human_approval:
        operators.human_approval_required = False
        logger.warning("Human approval disabled - operating in automated mode")

    monitor = NetworkMonitor(args.interface)
    logger_instance = ImmutableLogger(args.log_file)
    bus = MessageBus(args.rabbitmq_host)
    bus.connect()

    logger.info(f"Starting syntropic agent on interface {args.interface}")
    logger_instance.log_event({"event": "agent_started", "interface": args.interface})

    try:
        while True:
            # Gather current state
            queue_stats = monitor.get_queue_stats()
            latency = monitor.measure_latency()
            tc_status = operators.J()

            current_state = {
                "interface": args.interface,
                "latency_ms": latency,
                "queue_stats": queue_stats,
                "tc_status": tc_status,
                "operators_applied": []
            }

            # Apply operators based on conditions
            if latency > MAX_DELAY_MS:
                result = operators.C(latency)
                current_state["operators_applied"].append(result)

            if queue_stats.get("backlog", 0) > MAX_QUEUE_PACKETS:
                result = operators.R()
                current_state["operators_applied"].append(result)
                result = operators.H()
                current_state["operators_applied"].append(result)

            # Periodic optimization
            result = operators.O()
            current_state["operators_applied"].append(result)

            result = operators.M()
            current_state["operators_applied"].append(result)

            # Log and broadcast
            logger_instance.log_event(current_state)
            bus.broadcast_state(current_state)

            time.sleep(MONITORING_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
        logger_instance.log_event({"event": "agent_stopped"})
    except Exception as e:
        logger.error(f"Agent error: {e}")
        logger_instance.log_event({"event": "agent_error", "error": str(e)})
        sys.exit(1)

if __name__ == "__main__":
    main()