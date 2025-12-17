#!/usr/bin/env python3
"""
Dunebugger Starter
Simple application that listens to a GPIO input and sends NATS messages.
Based on the dunebugger architecture pattern.
"""

import asyncio
import signal
import sys
from gpio_nats_logging import logger
from gpio_nats_settings import settings
from simple_gpio_handler import SimpleGPIOHandler
from simple_nats_client import SimpleNATSClient


class GPIONATSSender:
    """Main application class for dunebugger-starter."""
    
    def __init__(self):
        self.running = False
        self.gpio_handler = None
        self.nats_client = None
        
        # Configuration from settings
        self.nats_server = getattr(settings, 'natsServer', 'nats://localhost:4222')
        self.nats_subject = getattr(settings, 'natsSubject', 'dunebugger.core.dunebugger_set')
        self.nats_message = getattr(settings, 'natsMessage', 'c')
        self.client_id = getattr(settings, 'clientId', 'dunebugger-starter')
        
        logger.info(f"Configured to send '{self.nats_message}' to '{self.nats_subject}' on '{self.nats_server}'")
    
    async def gpio_trigger_callback(self, channel):
        """Callback function called when GPIO is triggered."""
        logger.info(f"GPIO trigger detected on channel {channel}")
        
        # Send NATS message
        if self.nats_client and self.nats_client.get_connection_status():
            success = await self.nats_client.send_message(
                self.nats_subject,
                self.nats_message
            )
            if success:
                logger.info(f"Successfully sent NATS message: '{self.nats_message}' to '{self.nats_subject}'")
            else:
                logger.error("Failed to send NATS message")
        else:
            logger.error("Cannot send message: NATS client not connected")
    
    async def initialize(self):
        """Initialize the application components."""
        logger.info("Initializing Dunebugger Starter...")
        
        try:
            # Initialize NATS client if enabled
            if getattr(settings, 'natsEnabled', True):
                self.nats_client = SimpleNATSClient(
                    servers=self.nats_server,
                    client_id=self.client_id
                )
                await self.nats_client.connect()
            else:
                logger.warning("NATS is disabled in configuration")
            
            # Initialize GPIO handler if enabled
            if getattr(settings, 'gpioEnabled', True):
                self.gpio_handler = SimpleGPIOHandler(
                    callback_function=self.gpio_trigger_callback
                )
            else:
                logger.warning("GPIO is disabled in configuration")
            
            logger.info("Initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup application resources."""
        logger.info("Cleaning up resources...")
        
        try:
            # Cleanup GPIO
            if self.gpio_handler:
                self.gpio_handler.cleanup()
            
            # Disconnect NATS
            if self.nats_client:
                await self.nats_client.disconnect()
            
            logger.info("Cleanup completed")
        
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False
    
    async def run(self):
        """Main application run loop."""
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Initialize components
        if not await self.initialize():
            logger.error("Failed to initialize application")
            return False
        
        # Main loop
        self.running = True
        logger.info("Dunebugger Starter is running. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                # Check NATS connection status
                if self.nats_client and not self.nats_client.get_connection_status():
                    logger.warning("NATS connection lost, attempting to reconnect...")
                    try:
                        await self.nats_client.connect()
                    except Exception as e:
                        logger.error(f"Failed to reconnect to NATS: {e}")
                
                # Sleep for a short time to prevent busy waiting
                await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        
        finally:
            await self.cleanup()
            logger.info("Application stopped")
        
        return True


async def main():
    """Application entry point."""
    logger.info("Starting Dunebugger Starter")
    logger.info(f"Debug mode: {getattr(settings, 'debugMode', False)}")
    
    app = GPIONATSSender()
    success = await app.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())