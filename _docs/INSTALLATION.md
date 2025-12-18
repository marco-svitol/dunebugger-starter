# GPIO-NATS Sender Installation & Service Setup

## Prerequisites

- Raspberry Pi with Raspberry Pi OS (or compatible Linux distribution)
- Python 3.7 or higher
- sudo/root access
- Internet connection for downloading dependencies

## Installation Process

### 1. Prepare the Installation

Make the installation scripts executable:
```bash
cd /path/to/gpio-nats-sender
chmod +x install.sh
chmod +x gpio-nats-service.sh
```

### 2. Run the Installation

Execute the installation script as root:
```bash
sudo ./install.sh
```

The installation script will:
- Create `/opt/gpio-nats-sender/` directory
- Copy all application files
- Create a Python virtual environment (`.venv`)
- Install all required dependencies
- Create systemd service file
- Set proper file permissions
- Enable the service (but not start it)

### 3. Configure the Application

Edit the configuration file:
```bash
sudo nano /opt/gpio-nats-sender/app/config/gpio-nats.conf
```

**Key settings to modify:**
```ini
[NATS]
# Change to your remote NATS server IP
natsServer = nats://192.168.1.100:4222

[GPIO]
# Set your GPIO pin (BCM numbering)
gpioPin = 6
```

### 4. Start and Enable the Service

#### Using the service management script:
```bash
# Start the service
sudo ./gpio-nats-service.sh start

# Enable to start at boot
sudo ./gpio-nats-service.sh enable

# Check status
./gpio-nats-service.sh status
```

#### Or using systemctl directly:
```bash
# Start the service
sudo systemctl start gpio-nats-sender

# Enable auto-start at boot
sudo systemctl enable gpio-nats-sender

# Check status
sudo systemctl status gpio-nats-sender
```

## Service Management

### Service Management Script Commands

The `gpio-nats-service.sh` script provides convenient management:

```bash
# Start service
sudo ./gpio-nats-service.sh start

# Stop service
sudo ./gpio-nats-service.sh stop

# Restart service
sudo ./gpio-nats-service.sh restart

# View status
./gpio-nats-service.sh status

# Follow logs in real-time
./gpio-nats-service.sh logs

# Edit configuration
sudo ./gpio-nats-service.sh config

# Uninstall completely
sudo ./gpio-nats-service.sh uninstall
```

### Direct systemctl Commands

```bash
# Service control
sudo systemctl start gpio-nats-sender
sudo systemctl stop gpio-nats-sender
sudo systemctl restart gpio-nats-sender
sudo systemctl reload gpio-nats-sender

# Status and logs
systemctl status gpio-nats-sender
journalctl -u gpio-nats-sender -f
journalctl -u gpio-nats-sender --since "1 hour ago"

# Enable/disable auto-start
sudo systemctl enable gpio-nats-sender
sudo systemctl disable gpio-nats-sender
```

## File Locations

After installation:
```
/opt/gpio-nats-sender/
├── .venv/                    # Python virtual environment
├── app/                      # Application code
│   ├── main.py
│   ├── config/
│   │   └── gpio-nats.conf    # Main configuration file
│   └── ...
├── requirements.txt
└── README.md

/etc/systemd/system/gpio-nats-sender.service    # Systemd service file
```

## Configuration Examples

### Basic Remote Server Setup
```ini
[NATS]
natsServer = nats://192.168.1.100:4222
natsSubject = dunebugger.core.dunebugger_set
natsMessage = c

[GPIO]
gpioPin = 6
gpioEdgeDetection = RISING
bouncingThreshold = 0.2
```

### Multiple NATS Servers
```ini
[NATS]
natsServer = nats://192.168.1.100:4222,nats://192.168.1.101:4222
```

### Different GPIO Configuration
```ini
[GPIO]
gpioPin = 24
gpioPullUpDown = UP
gpioEdgeDetection = FALLING
bouncingThreshold = 0.1
```

## Troubleshooting

### Check Service Status
```bash
systemctl status gpio-nats-sender
```

### View Recent Logs
```bash
journalctl -u gpio-nats-sender --since "10 minutes ago"
```

### Test Configuration
```bash
# Test loading configuration
cd /opt/gpio-nats-sender/app
sudo -u pi /opt/gpio-nats-sender/.venv/bin/python -c "
from gpio_nats_settings import settings
print(f'GPIO Pin: {settings.gpioPin}')
print(f'NATS Server: {settings.natsServer}')
"
```

### Common Issues

1. **Permission Denied on GPIO**: Add user to gpio group:
   ```bash
   sudo usermod -a -G gpio pi
   ```

2. **Network Connection Issues**: Check firewall and network connectivity:
   ```bash
   # Test NATS connectivity
   telnet 192.168.1.100 4222
   ```

3. **Service Won't Start**: Check logs:
   ```bash
   journalctl -u gpio-nats-sender --no-pager
   ```

4. **Python Module Errors**: Reinstall in virtual environment:
   ```bash
   cd /opt/gpio-nats-sender
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Security Notes

The service runs with these security restrictions:
- Non-root user (pi)
- Private temporary directory
- Protected system files
- No new privileges allowed
- Limited file system access

## Updating the Application

To update the application code:
1. Stop the service: `sudo systemctl stop gpio-nats-sender`
2. Replace files in `/opt/gpio-nats-sender/app/`
3. Update dependencies if needed: 
   ```bash
   cd /opt/gpio-nats-sender
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Start service: `sudo systemctl start gpio-nats-sender`