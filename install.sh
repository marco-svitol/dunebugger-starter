#!/bin/bash
# GPIO-NATS Sender Installation Script
# This script sets up the application with a virtual environment and systemd service

set -e  # Exit on any error

# Configuration
APP_NAME="dunebugger-starter"
APP_DIR="/opt/dunebugger-starter"
SERVICE_USER="pi"  # Change this if you want a different user
VENV_DIR="$APP_DIR/.venv"
SERVICE_FILE="/etc/systemd/system/dunebugger-starter.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Check if service user exists
if ! id "$SERVICE_USER" &>/dev/null; then
    print_error "User '$SERVICE_USER' does not exist. Please create the user or change SERVICE_USER in this script."
    exit 1
fi

print_status "Starting GPIO-NATS Sender installation..."

# Stop service if it's running
if systemctl is-active --quiet dunebugger-starter 2>/dev/null; then
    print_status "Stopping existing dunebugger-starter service..."
    systemctl stop dunebugger-starter
fi

# Create application directory
print_status "Creating application directory: $APP_DIR"
mkdir -p "$APP_DIR"

# Copy application files
print_status "Copying application files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_DIR/app" "$APP_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$APP_DIR/"
cp "$SCRIPT_DIR/README.md" "$APP_DIR/"
cp "$SCRIPT_DIR/QUICK_SETUP.md" "$APP_DIR/"

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"

# Activate virtual environment and install dependencies
print_status "Installing Python dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"
deactivate

# Set ownership
print_status "Setting file ownership to $SERVICE_USER..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR"

# Create systemd service file
print_status "Creating systemd service file..."
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Dunebugger Starter
Documentation=file://$APP_DIR/README.md
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$APP_DIR/app
Environment=PATH=$VENV_DIR/bin
ExecStart=$VENV_DIR/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dunebugger-starter

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR

[Install]
WantedBy=multi-user.target
EOF

# Set service file permissions
chmod 644 "$SERVICE_FILE"

# Reload systemd and enable service
print_status "Reloading systemd daemon..."
systemctl daemon-reload

print_status "Enabling dunebugger-starter service..."
systemctl enable dunebugger-starter

print_success "Installation completed successfully!"
echo ""
print_status "Next steps:"
echo "  1. Edit configuration: $APP_DIR/app/config/gpio-nats.conf"
echo "  2. Set your remote NATS server IP in the [NATS] section"
echo "  3. Start the service: sudo systemctl start dunebugger-starter"
echo "  4. Check status: sudo systemctl status dunebugger-starter"
echo "  5. View logs: sudo journalctl -u dunebugger-starter -f"
echo ""
print_warning "Remember to configure your GPIO pin and NATS settings before starting!"