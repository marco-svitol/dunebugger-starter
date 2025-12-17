# Dunebugger Starter

A simple, lightweight application based on the dunebugger architecture pattern that monitors a GPIO input and sends NATS messages to a remote server.

## Overview

This application:
- Monitors a single GPIO pin for input changes (rising/falling edge)
- Sends configurable NATS messages to a specified topic
- Provides robust error handling and logging
- Supports both Raspberry Pi and development environments (with mock GPIO)

## Features

- **Simple Configuration**: Single configuration file with clear parameters
- **Flexible GPIO Setup**: Configurable pin, pull resistors, and edge detection
- **NATS Integration**: Send messages to any NATS server with custom subjects and payloads
- **Robust Logging**: File and console logging with configurable levels
- **Mock Support**: Runs on non-Raspberry Pi systems for development
- **Graceful Shutdown**: Proper cleanup on SIGINT/SIGTERM signals

## Installation

### Prerequisites

- Python 3.7 or higher
- Raspberry Pi (for actual GPIO functionality)
- NATS server accessible on the network

### Setup

1. Clone or copy this project to your target directory:
   ```bash
   cd /path/to/your/projects
   cp -r dunebugger-starter ./
   cd dunebugger-starter
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the application by editing `app/config/gpio-nats.conf`

## Configuration

Edit `app/config/gpio-nats.conf` to customize the application:

### Key Settings

- **GPIO Pin**: `gpioPin = 18` (BCM pin number)
- **NATS Server**: `natsServer = nats://192.168.1.100:4222` (replace with your target IP)
- **NATS Subject**: `natsSubject = dunebugger.core.dunebugger_set`
- **Message**: `natsMessage = c`

### Example Configuration for Remote Server

```ini
[NATS]
# Replace with your target server IP
natsServer = nats://192.168.1.100:4222
natsSubject = dunebugger.core.dunebugger_set
natsMessage = c
```

## Usage

### Running the Application

```bash
cd app
python main.py
```

### Running as a Service

Create a systemd service file `/etc/systemd/system/dunebugger-starter.service`:

```ini
[Unit]
Description=Dunebugger Starter
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/path/to/dunebugger-starter/app
ExecStart=/usr/bin/python3 /path/to/dunebugger-starter/app/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable dunebugger-starter
sudo systemctl start dunebugger-starter
sudo systemctl status dunebugger-starter
```

## GPIO Wiring

Connect your input device to the configured GPIO pin:

- **Pin 18** (default): BCM GPIO 18 (Physical pin 12)
- **Ground**: Any GND pin
- **Pull Resistor**: Configured in software (UP/DOWN)

### Example: Button Connection
```
Button ---- GPIO 18 (Pin 12)
Button ---- GND (Pin 6)
```

## Logging

Logs are written to:
- **Console**: Real-time output with colored formatting
- **File**: `dunebugger-starter.log` (in project root)

Log levels can be adjusted in the logging setup within `gpio_nats_logging.py`.

## Development and Testing

The application includes mock GPIO support for development on non-Raspberry Pi systems:

```bash
# Will use mock GPIO automatically on non-Pi systems
python app/main.py
```

## NATS Message Format

The application sends messages in JSON format:
```json
{
  "body": "c",
  "sender": "dunebugger-starter"
}
```

## Troubleshooting

### Common Issues

1. **GPIO Permission Errors**: Run with appropriate permissions or add user to gpio group
2. **NATS Connection Failures**: Check server IP, port, and network connectivity
3. **Module Import Errors**: Ensure all dependencies are installed with pip

### Debug Mode

Enable debug mode in configuration:
```ini
[General]
debugMode = True
```

This provides additional logging information for troubleshooting.

## Architecture

Based on the dunebugger pattern with these components:

- **Settings Module**: Configuration management
- **Logging Module**: Centralized logging setup
- **GPIO Handler**: Hardware abstraction for GPIO operations
- **NATS Client**: Simplified NATS messaging
- **Main Application**: Orchestrates components and handles lifecycle

## Customization

### Changing the Message

Edit the configuration file:
```ini
[NATS]
natsMessage = your_custom_message
```

### Multiple Remote Servers

Support for multiple NATS servers:
```ini
[NATS]
natsServer = nats://server1:4222,nats://server2:4222
```

### Different GPIO Configurations

Modify GPIO settings:
```ini
[GPIO]
gpioPin = 24
gpioEdgeDetection = FALLING
gpioPullUpDown = UP
bouncingThreshold = 0.1
```

## License

This project follows the same license as the parent dunebugger project.