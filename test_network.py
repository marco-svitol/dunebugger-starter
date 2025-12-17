#!/usr/bin/env python3
"""
Network Connectivity Test Utility
Test basic network connectivity to the NATS server.
"""

import socket
import sys
import os
import subprocess
import time

# Add the app directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from gpio_nats_logging import logger
from gpio_nats_settings import settings


def parse_nats_url(nats_url):
    """Parse NATS URL to extract host and port."""
    try:
        # Remove protocol if present
        if '://' in nats_url:
            url_parts = nats_url.split('://', 1)[1]
        else:
            url_parts = nats_url
        
        # Extract host and port
        if ':' in url_parts:
            host, port_str = url_parts.rsplit(':', 1)
            port = int(port_str)
        else:
            host = url_parts
            port = 4222  # Default NATS port
        
        return host, port
    except Exception as e:
        logger.error(f"Failed to parse NATS URL '{nats_url}': {e}")
        return None, None


def test_tcp_connection(host, port, timeout=5):
    """Test TCP connection to host:port."""
    try:
        logger.info(f"Testing TCP connection to {host}:{port} (timeout: {timeout}s)...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start_time = time.time()
        result = sock.connect_ex((host, port))
        end_time = time.time()
        sock.close()
        
        if result == 0:
            logger.info(f"✅ TCP connection successful! ({end_time - start_time:.2f}s)")
            return True
        else:
            logger.error(f"❌ TCP connection failed with error code: {result}")
            return False
    except socket.timeout:
        logger.error(f"❌ TCP connection timed out after {timeout}s")
        return False
    except Exception as e:
        logger.error(f"❌ TCP connection error: {e}")
        return False


def test_dns_resolution(host):
    """Test DNS resolution for the host."""
    try:
        logger.info(f"Testing DNS resolution for '{host}'...")
        ip_address = socket.gethostbyname(host)
        logger.info(f"✅ DNS resolution successful: {host} -> {ip_address}")
        return ip_address
    except socket.gaierror as e:
        logger.error(f"❌ DNS resolution failed: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ DNS resolution error: {e}")
        return None


def test_ping(host, count=3):
    """Test ping connectivity to the host."""
    try:
        logger.info(f"Testing ping to '{host}' ({count} packets)...")
        result = subprocess.run(
            ['ping', '-c', str(count), '-W', '3', host],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            # Extract ping statistics
            lines = result.stdout.strip().split('\\n')
            stats_line = [line for line in lines if 'packets transmitted' in line]
            if stats_line:
                logger.info(f"✅ Ping successful: {stats_line[0]}")
            else:
                logger.info("✅ Ping successful!")
            return True
        else:
            logger.error(f"❌ Ping failed: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Ping timed out")
        return False
    except FileNotFoundError:
        logger.warning("⚠️ Ping command not available")
        return None
    except Exception as e:
        logger.error(f"❌ Ping error: {e}")
        return False


def main():
    """Main entry point."""
    logger.info("Network Connectivity Test")
    logger.info("=" * 50)
    
    # Get NATS server from settings
    nats_server = getattr(settings, 'natsServer', 'nats://localhost:4222')
    logger.info(f"NATS Server: {nats_server}")
    
    # Parse the NATS URL
    host, port = parse_nats_url(nats_server)
    if not host or not port:
        logger.error("Failed to parse NATS server URL")
        sys.exit(1)
    
    logger.info(f"Target: {host}:{port}")
    logger.info("-" * 50)
    
    # Test DNS resolution
    ip_address = test_dns_resolution(host)
    
    # Test ping (if available)
    ping_result = test_ping(host)
    
    # Test TCP connection
    tcp_result = test_tcp_connection(host, port)
    
    # Summary
    logger.info("=" * 50)
    logger.info("Test Summary:")
    logger.info(f"DNS Resolution: {'✅ OK' if ip_address else '❌ Failed'}")
    logger.info(f"Ping: {'✅ OK' if ping_result else '❌ Failed' if ping_result is False else '⚠️ N/A'}")
    logger.info(f"TCP Connection: {'✅ OK' if tcp_result else '❌ Failed'}")
    
    # Overall result
    if tcp_result:
        logger.info("🎉 Network connectivity test PASSED")
        logger.info("The NATS server appears to be reachable.")
        sys.exit(0)
    else:
        logger.error("💥 Network connectivity test FAILED")
        logger.error("The NATS server is not reachable. Check:")
        logger.error("  1. Network connectivity")
        logger.error("  2. NATS server is running")
        logger.error("  3. Firewall settings")
        logger.error("  4. Server configuration")
        sys.exit(1)


if __name__ == "__main__":
    main()