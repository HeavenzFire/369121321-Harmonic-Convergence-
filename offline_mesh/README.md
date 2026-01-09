# Offline Sovereign Mesh Network

A zero-cloud dependency P2P network for underserved communities using ESP32 + LoRa nodes.

## Overview

This system provides:
- **Sovereign Knowledge Infrastructure**: Pre-loaded content caches (Wikipedia, legal aid, job boards)
- **P2P Communication**: LoRa-based mesh networking with 1km range
- **Emergent Intelligence**: Local resonators amplify community signals and predict needs
- **Zero Cost Operation**: Solar-powered nodes at $18 each
- **Offline Operation**: No cloud dependencies, air-gapped security

## Target Deployment Zones

### Rains County Trailer Parks (150 households)
- 15 nodes covering trailer park clusters
- Focus: Job applications, food banks, mental health resources

### Hopkins County Section 8 Clusters (320 units)
- 32 nodes for apartment complexes
- Focus: Housing assistance, adult education, benefits renewal

### Wood County Homeless Encampments (87 documented)
- 9 nodes for encampment areas
- Focus: Emergency shelter, SNAP benefits, crisis resources

## Hardware Requirements

- **ESP32 Development Board**: $3 each (bulk)
- **LoRa Module**: Integrated or add-on
- **Solar Power System**: Coin cell battery + small solar panel ($5)
- **MicroSD Card**: 128GB for content cache ($10)
- **Total per node**: $18

## Software Architecture

### Core Components

1. **ESP32Node**: Simulated ESP32 with LoRa capabilities
   - Position-based range calculation (1km LoRa simulation)
   - Solar power simulation with day/night cycles
   - Content cache with pre-loaded knowledge graphs

2. **ContentCache**: Static knowledge repository
   - Wikipedia excerpts
   - Legal aid guides
   - Job board caches
   - Community-specific resources

3. **LocalResonator**: Emergent intelligence engine
   - Tracks community signals
   - Predicts local needs based on patterns
   - Amplifies important information

4. **P2P Networking**: Socket-based LoRa simulation
   - Automatic peer discovery
   - Range-limited connections
   - Fault-tolerant mesh healing

## Deployment Process

1. **Church/Community Center Seeding**:
   - Deploy 10 initial nodes at central locations
   - Pre-load with community-specific content

2. **Resident Distribution**:
   - Provide "$18 family routers" to households
   - USB-based setup (plug and join mesh)

3. **Mesh Self-Healing**:
   - Automatic peer discovery and connection
   - Content propagation through mesh
   - Intelligence compounds locally

## Usage Examples

```python
from mesh_node import OfflineMesh

# Deploy Rains County mesh
mesh = OfflineMesh()
mesh.add_node("node_1", (32.85, -95.85), solar_power=True)
mesh.add_node("node_2", (32.87, -95.83), solar_power=True)

# Run simulation
mesh.run_simulation(duration=300)  # 5 minutes
```

## Content Categories

- **wikipedia**: Health, education, legal basics
- **job_boards**: Indeed/LinkedIn caches, local opportunities
- **legal_aid**: Eviction law, benefits applications
- **local_services**: Food banks, shelters, counseling

## Security & Governance

- **Air-Gapped**: No internet connectivity required
- **Sovereign**: Community-controlled content and intelligence
- **Auditable**: All content in public manifest
- **Exit Anytime**: No lock-in, easy removal

## Economics

- **Per Node Cost**: $18 (hardware + content)
- **Household Reach**: $0.12/month amortized
- **vs Manual Internet**: $60+/month
- **Value Prop**: Job apps, legal aid, health resources offline

## Running the System

```bash
# Deploy all zones
python deploy_script.py

# Run simulation test
python -c "from mesh_node import OfflineMesh; mesh = OfflineMesh(); mesh.add_node('test', (0,0)); mesh.run_simulation(60)"
```

## Future Enhancements

- Real ESP32 firmware implementation
- Advanced LoRa protocols
- Machine learning for better predictions
- Multi-language content support
- Integration with existing community networks