#!/bin/bash
# Test script for local virtual environment setup (for development/testing)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "=== Dunebugger Starter Local Test Setup =="

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install/update dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "=== Testing Application Imports ==="
cd "$SCRIPT_DIR/app"

# Test imports and configuration
python3 -c "
try:
    from gpio_nats_settings import settings
    from gpio_nats_logging import logger
    from simple_gpio_handler import SimpleGPIOHandler
    from simple_nats_client import SimpleNATSClient
    
    print('✓ All modules imported successfully')
    print(f'✓ GPIO Pin: {getattr(settings, \"gpioPin\", \"Not configured\")}')
    print(f'✓ NATS Server: {getattr(settings, \"natsServer\", \"Not configured\")}')
    print(f'✓ NATS Subject: {getattr(settings, \"natsSubject\", \"Not configured\")}')
    print(f'✓ NATS Message: {getattr(settings, \"natsMessage\", \"Not configured\")}')
    print(f'✓ Running on Raspberry Pi: {getattr(settings, \"ON_RASPBERRY_PI\", False)}')
    print('')
    print('✓ Dunebugger Starter is ready!')
    print('')
    print('To run manually:')
    print(f'  source {VENV_DIR}/bin/activate')
    print(f'  cd {SCRIPT_DIR}/app')
    print('  python3 main.py')
    
except ImportError as e:
    print(f'✗ Import error: {e}')
    exit(1)
except Exception as e:
    print(f'✗ Error: {e}')
    exit(1)
"

echo ""
echo "=== Virtual Environment Setup Complete ==="
echo "Virtual environment location: $VENV_DIR"
echo ""
echo "To activate manually:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "To run the application:"
echo "  cd $SCRIPT_DIR/app"
echo "  python3 main.py"