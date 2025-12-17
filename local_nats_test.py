#!/usr/bin/env python3
"""
Local NATS Test Setup
Helps test the application with a local NATS server using Docker.
"""

import subprocess
import sys
import time
import os

def run_command(cmd, check=True, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e}")
        return None

def check_docker():
    """Check if Docker is available."""
    result = run_command("docker --version", check=False)
    if result and result.returncode == 0:
        print("✅ Docker is available")
        return True
    else:
        print("❌ Docker is not available or not running")
        return False

def start_local_nats():
    """Start a local NATS server using Docker."""
    print("Starting local NATS server...")
    
    # Stop any existing NATS container
    run_command("docker stop nats-test 2>/dev/null", check=False)
    run_command("docker rm nats-test 2>/dev/null", check=False)
    
    # Start new NATS container
    cmd = "docker run -d --name nats-test -p 4222:4222 -p 8222:8222 nats:latest"
    result = run_command(cmd)
    
    if result and result.returncode == 0:
        print("✅ NATS server started successfully")
        print("   - NATS port: 4222")
        print("   - HTTP monitoring: http://localhost:8222")
        
        # Wait a moment for the server to start
        print("Waiting for NATS to start...")
        time.sleep(3)
        
        # Test connection
        test_result = run_command("docker exec nats-test nats pub test 'hello'", check=False)
        if test_result and test_result.returncode == 0:
            print("✅ NATS server is responding")
            return True
        else:
            print("⚠️ NATS server started but may not be ready yet")
            return True
    else:
        print("❌ Failed to start NATS server")
        return False

def stop_local_nats():
    """Stop the local NATS server."""
    print("Stopping local NATS server...")
    result = run_command("docker stop nats-test", check=False)
    run_command("docker rm nats-test", check=False)
    
    if result and result.returncode == 0:
        print("✅ NATS server stopped")
    else:
        print("⚠️ NATS server may not have been running")

def update_config_for_local():
    """Update configuration to use localhost NATS."""
    config_file = "app/config/dunebugger-starter.conf"
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    print(f"Updating {config_file} for local NATS server...")
    
    # Read current config
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Update NATS server line
    lines = content.split('\\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('natsServer'):
            lines[i] = 'natsServer = nats://localhost:4222'
            print("✅ Updated natsServer to localhost:4222")
            break
    
    # Write updated config
    with open(config_file, 'w') as f:
        f.write('\\n'.join(lines))
    
    return True

def restore_config():
    """Restore original configuration."""
    config_file = "app/config/dunebugger-starter.conf"
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    print(f"Restoring {config_file} to original settings...")
    
    # Read current config
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Update NATS server line back to original
    lines = content.split('\\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('natsServer'):
            lines[i] = 'natsServer = nats://10.1.2.2:4222'
            print("✅ Restored natsServer to 10.1.2.2:4222")
            break
    
    # Write updated config
    with open(config_file, 'w') as f:
        f.write('\\n'.join(lines))
    
    return True

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ./local_nats_test.py start   - Start local NATS and update config")
        print("  ./local_nats_test.py stop    - Stop local NATS and restore config")
        print("  ./local_nats_test.py test    - Test connection to current config")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == "start":
        print("🚀 Setting up local NATS test environment")
        print("=" * 50)
        
        if not check_docker():
            sys.exit(1)
        
        if start_local_nats():
            if update_config_for_local():
                print("=" * 50)
                print("🎉 Local NATS test environment ready!")
                print("You can now run:")
                print("  ./test_nats_connection.py")
                print("  python app/main.py")
                print("")
                print("When done, run: ./local_nats_test.py stop")
            else:
                stop_local_nats()
                sys.exit(1)
        else:
            sys.exit(1)
    
    elif action == "stop":
        print("🛑 Stopping local NATS test environment")
        print("=" * 50)
        stop_local_nats()
        restore_config()
        print("✅ Local test environment cleaned up")
    
    elif action == "test":
        print("🔍 Testing current NATS configuration")
        print("=" * 50)
        os.system("./test_nats_connection.py")
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()