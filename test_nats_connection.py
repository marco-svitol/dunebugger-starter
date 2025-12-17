#!/usr/bin/env python3
"""
NATS Connection Test Utility
Test NATS connectivity before running the main application.
"""

import asyncio
import sys
import os

# Add the app directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from gpio_nats_logging import logger
from gpio_nats_settings import settings
from simple_nats_client import SimpleNATSClient


async def test_nats_connection():
    """Test NATS connection with current configuration."""
    logger.info("NATS Connection Test")
    logger.info("=" * 40)
    
    # Get settings
    nats_server = getattr(settings, 'natsServer', 'nats://localhost:4222')
    client_id = getattr(settings, 'clientId', 'dunebugger-starter-test')
    timeout = getattr(settings, 'natsTimeout', 10)
    max_retries = getattr(settings, 'natsMaxRetries', 3)
    retry_delay = getattr(settings, 'natsRetryDelay', 5)
    
    logger.info(f"Server: {nats_server}")
    logger.info(f"Client ID: {client_id}")
    logger.info(f"Timeout: {timeout}s")
    logger.info(f"Max Retries: {max_retries}")
    logger.info(f"Retry Delay: {retry_delay}s")
    logger.info("-" * 40)
    
    # Create client
    client = SimpleNATSClient(
        servers=nats_server,
        client_id=client_id,
        connection_timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay
    )
    
    # Test connection
    logger.info("Testing connection...")
    success = await client.connect()
    
    if success:
        logger.info("✅ NATS connection successful!")
        
        # Test sending a message
        test_subject = getattr(settings, 'natsSubject', 'dunebugger.test')
        test_message = "test"
        
        logger.info(f"Testing message send to '{test_subject}'...")
        message_sent = await client.send_message(test_subject, test_message)
        
        if message_sent:
            logger.info("✅ Message sent successfully!")
        else:
            logger.error("❌ Failed to send test message")
        
        # Disconnect
        await client.disconnect()
        logger.info("Connection test completed")
        return True
    else:
        logger.error("❌ NATS connection failed!")
        return False


def main():
    """Main entry point."""
    try:
        result = asyncio.run(test_nats_connection())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()