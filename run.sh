#!/bin/bash
# Simple run script for Dunebugger Starter

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/app"

echo "Starting Dunebugger Starter..."
python3 main.py