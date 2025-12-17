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

# Connection management (new features)
natsTimeout = 10          # Connection timeout in seconds
natsMaxRetries = 3        # Maximum retry attempts
natsRetryDelay = 5        # Base delay between retries (exponential backoff)
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

### Test Utilities

Several test utilities are provided for troubleshooting and development:

#### Network Connectivity Test
Test basic network connectivity to the NATS server:
```bash
./test_network.py
```

#### NATS Connection Test  
Test the full NATS connection with authentication and message sending:
```bash
./test_nats_connection.py
```

#### Local NATS Testing
For development, you can set up a local NATS server using Docker:
```bash
# Start local NATS server and update config
./local_nats_test.py start

# Test your application with local NATS
python app/main.py

# Stop local NATS and restore original config  
./local_nats_test.py stop
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

### Connection Issues

If you're seeing NATS connection timeout errors like:
```
nats: encountered error
asyncio.exceptions.CancelledError
TimeoutError
```

Follow these steps:

#### 1. Test Network Connectivity
Run the network connectivity test to check if the NATS server is reachable:

```bash
./test_network.py
```

This will test:
- DNS resolution (if using hostnames)
- Ping connectivity
- TCP connection to the NATS port

#### 2. Test NATS Connection
Test the NATS connection specifically:

```bash
./test_nats_connection.py
```

This will test the full NATS connection with retry logic and provide detailed error messages.

#### 3. Check Configuration
Verify your NATS server settings in `app/config/dunebugger-starter.conf`:

```ini
[NATS]
# Ensure this IP/hostname is correct for your network
natsServer = nats://10.1.2.2:4222
# Increase timeout if you have slow network
natsTimeout = 15
# Increase retries for unreliable connections  
natsMaxRetries = 5
# Adjust retry delay
natsRetryDelay = 10
```

### Connection Management Features

The application now includes robust connection management:

- **Automatic Retry**: Configurable retry attempts with exponential backoff
- **Network Connectivity Checks**: Pre-connection TCP tests
- **Graceful Degradation**: Application continues running even if NATS is unavailable
- **Connection Recovery**: Automatic reconnection attempts in main loop
- **Detailed Logging**: Clear error messages for connection issues

### Common Issues

1. **GPIO Permission Errors**: Run with appropriate permissions or add user to gpio group
2. **NATS Server Unreachable**: 
   - Check if NATS server is running: `docker ps` or `systemctl status nats`
   - Verify IP address and port
   - Check firewall settings
   - Test with: `telnet <ip> 4222`
3. **Network Connectivity**: Use `./test_network.py` to diagnose
4. **Module Import Errors**: Ensure all dependencies are installed with pip

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