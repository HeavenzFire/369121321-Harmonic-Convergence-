# Civic Shield Network Deployment Guide

## Overview

This guide provides complete instructions for deploying CSN nodes in pilot environments. The deployment prioritizes **security**, **simplicity**, and **verifiability**.

## Prerequisites

### Hardware Requirements
- **Raspberry Pi 4 Model B** (4GB RAM minimum) or equivalent
- **32GB microSD card** (Class 10, UHS-I)
- **Power supply** (5V, 3A USB-C)
- **Ethernet cable** (for initial setup) or WiFi module
- **Optional**: Case, cooling fan, UPS backup

### Software Requirements
- **Host system**: Linux/macOS/Windows with Docker support
- **Docker Engine** 20.10+ installed
- **Git** for repository access
- **USB drive** (8GB minimum) for air-gapped transfer

### Network Requirements
- **Air-gapped by default**: No internet connectivity required
- **Optional LAN**: Isolated network segment for multi-node coordination
- **Secure channels**: Encrypted peer-to-peer when connectivity needed

## Node Specifications

### Hardware Configuration
```bash
# Raspberry Pi 4B specifications for CSN node
CPU: Quad-core ARM Cortex-A72 @ 1.5GHz
RAM: 4GB LPDDR4
Storage: 32GB microSD (encrypted)
Network: Gigabit Ethernet + WiFi 5
Power: 5V/3A USB-C
```

### Software Stack
- **OS**: Raspberry Pi OS Lite (64-bit)
- **Container**: Docker with security hardening
- **Application**: CSN node software (Python/Node.js)
- **Security**: AppArmor, SELinux, encrypted storage

### Performance Targets
- **Boot time**: < 60 seconds
- **Memory usage**: < 512MB at idle
- **CPU usage**: < 10% average
- **Storage**: < 8GB for 1 year of logs
- **Uptime**: 99.9% target

## Installation Procedure

### Step 1: Prepare Installation Media
```bash
# Download and verify CSN image
wget https://releases.csn.local/node-v1.0.0.img.gz
wget https://releases.csn.local/node-v1.0.0.img.gz.sha256
sha256sum -c node-v1.0.0.img.gz.sha256

# Flash to microSD card
gunzip node-v1.0.0.img.gz
sudo dd if=node-v1.0.0.img of=/dev/sdX bs=4M status=progress
```

### Step 2: Initial Configuration
```bash
# Boot Raspberry Pi with prepared SD card
# Initial setup (runs automatically on first boot)

# Configure node identity
sudo csn-config --node-id "pilot-001" --location "Community Center A"

# Set security parameters
sudo csn-config --airgap-mode true --encryption-key "generate"
```

### Step 3: Network Setup
```bash
# Air-gapped mode (default)
sudo csn-config --network-mode airgap

# Optional: Isolated LAN mode
sudo csn-config --network-mode lan --subnet 192.168.100.0/24

# Optional: Secure peer-to-peer
sudo csn-config --network-mode p2p --peers "node1,node2,node3"
```

### Step 4: Service Activation
```bash
# Start CSN services
sudo systemctl enable csn-node
sudo systemctl start csn-node

# Verify operation
sudo csn-status
# Expected output: "CSN Node Active - Air-gapped Mode"
```

## Multi-Node Deployment

### Pilot Network Setup (5 Nodes)
```bash
# Node 1: Central coordinator
sudo csn-config --role coordinator --peers "node2,node3,node4,node5"

# Node 2-5: Worker nodes
sudo csn-config --role worker --coordinator "node1"
```

### Mesh Synchronization
```bash
# Manual sync via USB (air-gapped)
sudo csn-sync --method usb --device /dev/sda

# LAN sync (isolated network)
sudo csn-sync --method lan --interval 300

# Encrypted P2P sync
sudo csn-sync --method p2p --encryption aes256
```

## Maintenance Procedures

### Daily Checks
- [ ] Verify node status: `csn-status`
- [ ] Check system logs: `journalctl -u csn-node`
- [ ] Monitor resource usage: `htop`
- [ ] Test alert generation: `csn-test-alert`

### Weekly Maintenance
- [ ] Update system packages: `sudo apt update && sudo apt upgrade`
- [ ] Rotate log files: `sudo logrotate /etc/logrotate.d/csn`
- [ ] Backup configuration: `sudo csn-backup --config`
- [ ] Verify peer connectivity: `csn-ping-peers`

### Monthly Maintenance
- [ ] Full system backup: `sudo csn-backup --full`
- [ ] Security audit: `sudo csn-audit --security`
- [ ] Performance analysis: `sudo csn-analyze --performance`
- [ ] Firmware updates: `sudo rpi-update`

## Troubleshooting

### Common Issues

#### Node Won't Start
```bash
# Check system logs
journalctl -u csn-node -n 50

# Verify configuration
sudo csn-config --validate

# Restart services
sudo systemctl restart csn-node
```

#### Network Connectivity Issues
```bash
# Test local network
ping 192.168.100.1

# Check firewall rules
sudo ufw status

# Verify peer certificates
sudo csn-cert --verify-peers
```

#### High Resource Usage
```bash
# Monitor processes
htop

# Check for memory leaks
sudo csn-diagnose --memory

# Restart problematic services
sudo systemctl restart csn-alert-engine
```

### Emergency Procedures

#### System Compromise
1. **Immediate isolation**: Disconnect from all networks
2. **Evidence preservation**: `sudo csn-forensic --capture`
3. **Secure shutdown**: `sudo shutdown -h now`
4. **Contact security**: zachary@local.engineer

#### Data Loss Recovery
1. **Assess damage**: `sudo csn-diagnose --data-integrity`
2. **Restore from backup**: `sudo csn-restore --backup /path/to/backup`
3. **Verify integrity**: `sudo csn-verify --data`
4. **Resume operation**: `sudo systemctl start csn-node`

## Claims Lock Verification

### Verifiable Deployment Claims
- **Hardware specs**: Measurable performance metrics
- **Installation time**: < 30 minutes from prepared media
- **Uptime target**: Logged and auditable
- **Security hardening**: Open-source configuration files

### Independent Testing
- **Hardware verification**: Standard Raspberry Pi benchmarks
- **Software integrity**: SHA256 checksums for all components
- **Network isolation**: Packet capture analysis
- **Performance metrics**: Automated monitoring scripts

## Support and Resources

### Documentation
- **User guide**: https://docs.csn.local/user-guide
- **API reference**: https://docs.csn.local/api
- **Troubleshooting**: https://docs.csn.local/troubleshoot

### Community Support
- **Forum**: https://community.csn.local
- **Mailing list**: support@csn.local
- **Emergency**: +1-XXX-XXX-XXXX (24/7)

### Professional Services
- **Deployment assistance**: deployment@csn.local
- **Custom configuration**: consulting@csn.local
- **Training**: training@csn.local

---

*This deployment guide ensures reliable, secure CSN node operation. All procedures are tested and verified.*