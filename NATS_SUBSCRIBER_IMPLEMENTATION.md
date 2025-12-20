# NATS Queue Subscriber Implementation for Dunebugger-Starter

## Overview

The dunebugger-starter project now includes a NATS message queue subscriber that listens to the `dunebugger.starter.*` queue and handles GPIO control commands, specifically the `sw` (switch) command.

## Architecture

The implementation follows the dunebugger project pattern and consists of:

### 1. NATS Queue Manager (`mqueue.py`)
- **NATSComm**: Full NATS communication class that handles connections, subscriptions, and message handling
- **NullNATSComm**: Null implementation when NATS is disabled
- Subscribes to `dunebugger.starter.*` subjects
- Auto-reconnection with retry logic
- Based on the dunebugger project's `mqueue.py`

### 2. Message Queue Handler (`mqueue_handler.py`)
- Processes incoming NATS messages
- Handles JSON message parsing
- Focuses on `dunebugger_set` subject
- Processes `sw <pin> <on|off>` commands
- Validates command syntax and GPIO pins
- Based on the dunebugger project's `mqueue_handler.py`

### 3. GPIO Handler (`starter_gpio_handler.py`)
- Loads GPIO configuration from `config/gpio.conf`
- Initializes GPIO pins according to configuration
- Handles GPIO output control for configured pins
- Follows the same inverted logic as dunebugger (on=0, off=1)
- Provides GPIO status information
- Based on the dunebugger project's `gpio_handler.py`

### 4. Updated Main Application (`main.py`)
- Integrates all components
- Initializes NATS subscriber alongside existing functionality
- Maintains original GPIO input trigger functionality
- Handles graceful cleanup of all resources

## Configuration

The system uses the existing configuration files:

### `config/dunebugger-starter.conf`
```ini
[General]
natsEnabled = True
clientId = dunebugger-starter

[NATS]
natsServer = nats://10.1.2.2:4222
```

### `config/gpio.conf`
Defines GPIO pin mappings and initial states:
- **Channels**: Physical pin groups
- **ChannelsSetup**: Pin directions and initial states  
- **LogicalChannels**: Logical to physical pin mapping
- **GPIOMaps**: Named GPIO mappings

## NATS Message Format

### Subscription
- **Subject**: `dunebugger.starter.*`
- **Listened subjects**: `dunebugger.starter.dunebugger_set`

### Message Format
```json
{
  "body": "sw <pin> <on|off>",
  "source": "dunebugger-core"
}
```

### Supported Commands
- `sw <pin_number> on`: Set GPIO pin to LOW (0) - turns relay/device ON
- `sw <pin_number> off`: Set GPIO pin to HIGH (1) - turns relay/device OFF

**Note**: GPIO logic is inverted following the dunebugger pattern where `on` = 0 and `off` = 1.

## GPIO Initialization

The GPIO handler:
1. Reads `config/gpio.conf` at startup
2. Configures all defined GPIO pins according to their setup
3. Sets initial states as defined in configuration
4. Only allows control of properly configured OUTPUT pins
5. Provides error messages for invalid pins or states

## Integration with Dunebugger Project

This implementation allows the dunebugger-starter to:
- Receive GPIO control commands from the main dunebugger system
- Control GPIO outputs on the starter device
- Maintain the same command syntax and logic as the main system
- Operate as a remote GPIO controller via NATS messaging

## Error Handling

- Invalid GPIO pin numbers are rejected
- Non-configured pins cannot be controlled
- Input pins cannot be set as outputs (on Raspberry Pi)
- Malformed commands return descriptive error messages
- Connection failures are handled with automatic retries
- All errors are logged with appropriate detail levels

## Testing

A test script `test_starter_components.py` is provided to verify:
- GPIO handler configuration loading
- GPIO status reporting
- GPIO output control
- Message queue command processing
- Error handling for invalid commands

## Usage Example

Send a NATS message to control GPIO pin 5:
```bash
# Turn ON relay connected to GPIO pin 5
nats pub dunebugger.starter.dunebugger_set '{"body": "sw 5 on", "source": "test"}'

# Turn OFF relay connected to GPIO pin 5  
nats pub dunebugger.starter.dunebugger_set '{"body": "sw 5 off", "source": "test"}'
```

The starter will process these commands and control the GPIO pins according to the configuration in `gpio.conf`.