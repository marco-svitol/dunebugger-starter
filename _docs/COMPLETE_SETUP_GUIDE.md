# 🚀 Complete Installation & Service Setup Guide

## Overview

This guide provides complete procedures for installing the GPIO-NATS sender application in a virtual environment and running it as a systemctl service.

## 📋 Prerequisites

- **Hardware**: Raspberry Pi (3/4/Zero recommended)
- **OS**: Raspberry Pi OS (Bullseye or newer)
- **Access**: sudo/root privileges
- **Network**: Internet connection for installation
- **Python**: 3.7+ (usually pre-installed)

## 🔧 Installation Methods

### Method 1: Automated Installation (Recommended)

#### Step 1: Prepare Installation
```bash
# Navigate to the project directory
cd /path/to/gpio-nats-sender

# Make scripts executable
chmod +x install.sh gpio-nats-service.sh test-setup.sh

# Run the automated installer
sudo ./install.sh
```

#### Step 2: Configure Application
```bash
# Edit configuration with your settings
sudo ./gpio-nats-service.sh config

# Or edit directly
sudo nano /opt/gpio-nats-sender/app/config/gpio-nats.conf
```

**Essential Configuration Changes:**
```ini
[NATS]
# Change to your remote NATS server
natsServer = nats://192.168.1.100:4222

[GPIO]  
# Set your GPIO pin (BCM numbering)
gpioPin = 21
```

#### Step 3: Start and Enable Service
```bash
# Start the service
sudo ./gpio-nats-service.sh start

# Enable auto-start at boot
sudo ./gpio-nats-service.sh enable

# Check status
./gpio-nats-service.sh status
```

### Method 2: Manual Installation

#### Step 1: Create Installation Directory
```bash
sudo mkdir -p /opt/gpio-nats-sender
cd /opt/gpio-nats-sender
```

#### Step 2: Copy Application Files
```bash
# Copy from your development location
sudo cp -r /path/to/gpio-nats-sender/app ./
sudo cp /path/to/gpio-nats-sender/requirements.txt ./
```

#### Step 3: Create Virtual Environment
```bash
# Create venv
sudo python3 -m venv .venv

# Activate and install dependencies
sudo .venv/bin/pip install --upgrade pip
sudo .venv/bin/pip install -r requirements.txt

# Set ownership (replace 'pi' with your user)
sudo chown -R pi:pi /opt/gpio-nats-sender
```

#### Step 4: Create Systemd Service
```bash
sudo nano /etc/systemd/system/gpio-nats-sender.service
```

**Service file content:**
```ini
[Unit]
Description=GPIO to NATS Sender
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/opt/gpio-nats-sender/app
Environment=PATH=/opt/gpio-nats-sender/.venv/bin
ExecStart=/opt/gpio-nats-sender/.venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Step 5: Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable gpio-nats-sender
sudo systemctl start gpio-nats-sender
```

## 🎛️ Service Management

### Using the Management Script

The `gpio-nats-service.sh` script provides easy service management:

```bash
# Service control
sudo ./gpio-nats-service.sh start      # Start service
sudo ./gpio-nats-service.sh stop       # Stop service  
sudo ./gpio-nats-service.sh restart    # Restart service

# Configuration
sudo ./gpio-nats-service.sh config     # Edit config file

# Monitoring
./gpio-nats-service.sh status          # Show status
./gpio-nats-service.sh logs            # Follow logs

# Boot behavior
sudo ./gpio-nats-service.sh enable     # Auto-start at boot
sudo ./gpio-nats-service.sh disable    # Disable auto-start

# Maintenance
sudo ./gpio-nats-service.sh uninstall  # Complete removal
```

### Using systemctl Directly

```bash
# Basic control
sudo systemctl start gpio-nats-sender
sudo systemctl stop gpio-nats-sender
sudo systemctl restart gpio-nats-sender

# Status and monitoring
systemctl status gpio-nats-sender
journalctl -u gpio-nats-sender -f
journalctl -u gpio-nats-sender --since "1 hour ago"

# Boot configuration
sudo systemctl enable gpio-nats-sender
sudo systemctl disable gpio-nats-sender
```

## 📁 File Structure After Installation

```
/opt/gpio-nats-sender/
├── .venv/                           # Python virtual environment
│   ├── bin/python                   # Python interpreter
│   ├── lib/python3.x/site-packages/# Installed packages
│   └── ...
├── app/                             # Application code
│   ├── main.py                      # Main application
│   ├── gpio_nats_settings.py        # Configuration loader
│   ├── gpio_nats_logging.py         # Logging setup
│   ├── simple_gpio_handler.py       # GPIO management
│   ├── simple_nats_client.py        # NATS messaging
│   ├── utils.py                     # Utilities
│   └── config/
│       └── gpio-nats.conf           # Configuration file
├── requirements.txt                 # Python dependencies
└── README.md                        # Documentation

/etc/systemd/system/gpio-nats-sender.service  # Service definition
```

## ⚙️ Configuration Examples

### Basic Remote Setup
```ini
[General]
gpioEnabled = True
natsEnabled = True
debugMode = False
clientId = gpio-nats-sender-001

[GPIO]
gpioPin = 21
gpioPullUpDown = DOWN
gpioEdgeDetection = RISING
bouncingThreshold = 0.2

[NATS]
natsServer = nats://192.168.1.100:4222
natsSubject = dunebugger.core.dunebugger_set
natsMessage = c
natsTimeout = 5
```

### Multiple Servers with Custom Message
```ini
[NATS]
natsServer = nats://server1:4222,nats://server2:4222
natsSubject = my.custom.trigger
natsMessage = button_pressed
```

### High-Sensitivity GPIO Setup
```ini
[GPIO]
gpioPin = 24
gpioPullUpDown = UP
gpioEdgeDetection = FALLING
bouncingThreshold = 0.05
```

## 🔍 Testing and Verification

### Test Virtual Environment
```bash
# Test local setup (development)
./test-setup.sh

# Test production installation
sudo -u pi /opt/gpio-nats-sender/.venv/bin/python -c "
import sys
sys.path.insert(0, '/opt/gpio-nats-sender/app')
from gpio_nats_settings import settings
print(f'GPIO Pin: {settings.gpioPin}')
print(f'NATS Server: {settings.natsServer}')
"
```

### Test GPIO Connection
```bash
# Monitor GPIO events (requires running service)
sudo journalctl -u gpio-nats-sender -f

# Manually trigger GPIO (if you have a button connected)
# Press the button and watch the logs
```

### Test NATS Connectivity
```bash
# Test network connection to NATS server
telnet 192.168.1.100 4222

# If telnet works, you should see:
# Trying 192.168.1.100...
# Connected to 192.168.1.100.
# INFO {...}
```

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check service status and logs
systemctl status gpio-nats-sender
journalctl -u gpio-nats-sender --no-pager

# Common issues:
# 1. Permission problems
sudo chown -R pi:pi /opt/gpio-nats-sender

# 2. Python path issues
sudo systemctl edit gpio-nats-sender
# Add:
# [Service]
# Environment=PYTHONPATH=/opt/gpio-nats-sender/app
```

### GPIO Permission Errors
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Verify group membership
groups pi

# Reboot may be required
sudo reboot
```

### Network/NATS Issues
```bash
# Test network connectivity
ping 192.168.1.100

# Check firewall
sudo ufw status

# Test NATS port specifically
nc -zv 192.168.1.100 4222
```

### Dependency Issues
```bash
# Reinstall in virtual environment
cd /opt/gpio-nats-sender
sudo -u pi .venv/bin/pip install --force-reinstall -r requirements.txt

# For development systems (no RPi.GPIO):
sudo -u pi .venv/bin/pip install nats-py python-dotenv
```

## 🔄 Updates and Maintenance

### Update Application Code
```bash
# Stop service
sudo systemctl stop gpio-nats-sender

# Update files (example)
sudo cp new_version/app/* /opt/gpio-nats-sender/app/

# Update dependencies if needed
cd /opt/gpio-nats-sender
sudo -u pi .venv/bin/pip install -r requirements.txt

# Start service
sudo systemctl start gpio-nats-sender
```

### Backup Configuration
```bash
# Backup current config
sudo cp /opt/gpio-nats-sender/app/config/gpio-nats.conf \
       /opt/gpio-nats-sender/app/config/gpio-nats.conf.backup

# Restore from backup
sudo cp /opt/gpio-nats-sender/app/config/gpio-nats.conf.backup \
       /opt/gpio-nats-sender/app/config/gpio-nats.conf
```

### Log Rotation
```bash
# View log size
journalctl --disk-usage

# Clean old logs (keep 1 week)
sudo journalctl --vacuum-time=1week
```

## 🔐 Security Considerations

The service includes these security measures:
- **Non-root execution**: Runs as 'pi' user
- **Filesystem restrictions**: Limited write access
- **No privilege escalation**: Cannot gain additional privileges
- **Private temporary space**: Isolated temp directory

### Additional Hardening
```bash
# Create dedicated service user (optional)
sudo useradd --system --shell /bin/false --home /opt/gpio-nats-sender gpio-nats

# Update service file to use dedicated user
sudo systemctl edit gpio-nats-sender
# Change User=gpio-nats and Group=gpio-nats
```

## 📞 Support

For issues or questions:
1. Check logs: `journalctl -u gpio-nats-sender -f`
2. Verify configuration: `sudo ./gpio-nats-service.sh config`
3. Test connectivity: Network and NATS server accessibility
4. Check GPIO permissions and hardware connections