#!/bin/bash
# HEAVENZFIRE SYNTHROPIC NETWORK STACK
# CAKE Setup Script
# Advanced CAKE configuration for syntropic network optimization

set -e

# Configuration
INTERFACE="${1:-eth0}"
DOWNLOAD_SPEED="${2:-100mbit}"
UPLOAD_SPEED="${3:-20mbit}"
OVERHEAD="${4:-44}"  # ADSL/PPPoE overhead
NAT="${5:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (sudo)"
    exit 1
fi

# Check if interface exists
if ! ip link show "$INTERFACE" >/dev/null 2>&1; then
    log_error "Interface $INTERFACE does not exist"
    exit 1
fi

# Check if tc is available
if ! command -v tc >/dev/null 2>&1; then
    log_error "tc command not found. Install iproute2 package."
    exit 1
fi

log_info "Setting up advanced CAKE queue discipline on interface: $INTERFACE"
log_info "Download: $DOWNLOAD_SPEED, Upload: $UPLOAD_SPEED"

# Remove existing qdisc if present
if tc qdisc show dev "$INTERFACE" | grep -q "qdisc"; then
    log_warn "Removing existing queue discipline..."
    tc qdisc del dev "$INTERFACE" root 2>/dev/null || true
fi

# Build CAKE command
CAKE_CMD="tc qdisc add dev $INTERFACE root cake"

# Add bandwidth settings
CAKE_CMD="$CAKE_CMD bandwidth $DOWNLOAD_SPEED"

# Add diffserv mode
CAKE_CMD="$CAKE_CMD besteffort"

# Add dual host isolation
CAKE_CMD="$CAKE_CMD dual-srchost"

# Add NAT compensation if requested
if [[ "$NAT" == "true" ]]; then
    CAKE_CMD="$CAKE_CMD nat"
fi

# Add ACK filtering
CAKE_CMD="$CAKE_CMD ack-filter"

# Add overhead compensation
CAKE_CMD="$CAKE_CMD overhead $OVERHEAD"

# Add minimum packet size
CAKE_CMD="$CAKE_CMD mpu 64"

log_info "Installing CAKE with command: $CAKE_CMD"

# Execute CAKE setup
eval "$CAKE_CMD"

# Verify installation
log_info "Verifying CAKE installation..."
tc qdisc show dev "$INTERFACE"

# Test CAKE functionality
log_info "Testing CAKE functionality..."
tc -s qdisc show dev "$INTERFACE"

# Create systemd service for persistence
SERVICE_FILE="/etc/systemd/system/syntropic-cake.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=HEAVENZFIRE Syntropic CAKE Queue Discipline
After=network.target
Wants=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c '$CAKE_CMD'
ExecStop=/usr/sbin/tc qdisc del dev $INTERFACE root

[Install]
WantedBy=multi-user.target
EOF

log_info "Systemd service created at $SERVICE_FILE"
systemctl daemon-reload
systemctl enable syntropic-cake

log_info "CAKE setup complete with systemd persistence!"
log_info "Service status: systemctl status syntropic-cake"
log_info "Monitor with: tc -s qdisc show dev $INTERFACE"
log_info "Start syntropic agent with: python3 agent/syntropic_agent.py --interface $INTERFACE"