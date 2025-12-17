from nats.aio.client import Client as NATS
import json
import asyncio
from gpio_nats_logging import logger


class SimpleNATSClient:
    """Simplified NATS client for sending messages only."""
    
    def __init__(self, servers, client_id="dunebugger-starter"):
        self.nc = NATS()
        self.servers = servers if isinstance(servers, list) else [servers]
        self.client_id = client_id
        self.is_connected = False
        
        # Set up connection callbacks
        self.nc.on_connect = self._on_connect
        self.nc.on_disconnect = self._on_disconnect
        self.nc.on_reconnect = self._on_reconnect

    async def _on_connect(self, nc):
        """Called when connected to NATS."""
        self.is_connected = True
        logger.info(f"Connected to NATS server: {self.servers}")

    async def _on_disconnect(self, nc):
        """Called when disconnected from NATS."""
        self.is_connected = False
        logger.warning("Disconnected from NATS server")

    async def _on_reconnect(self, nc):
        """Called when reconnected to NATS."""
        self.is_connected = True
        logger.info("Reconnected to NATS server")

    async def connect(self):
        """Connect to NATS server."""
        try:
            await self.nc.connect(
                servers=self.servers,
                name=self.client_id,
                reconnect_time_wait=10,
                max_reconnect_attempts=-1  # Infinite reconnect attempts
            )
            logger.info(f"NATS client '{self.client_id}' connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            self.is_connected = False

    async def disconnect(self):
        """Disconnect from NATS server."""
        if self.nc.is_connected:
            await self.nc.close()
            logger.info("Disconnected from NATS server")

    async def send_message(self, subject, message_body, timeout=5.0):
        """Send a message to NATS."""
        if not self.is_connected or not self.nc.is_connected:
            logger.error("Cannot send message: Not connected to NATS")
            return False
        
        try:
            # Create message payload
            payload = {
                "body": message_body,
                "sender": self.client_id
            }
            
            # Send message
            await asyncio.wait_for(
                self.nc.publish(subject, json.dumps(payload).encode()),
                timeout=timeout
            )
            
            logger.info(f"Message sent to '{subject}': {message_body}")
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout sending message to '{subject}'")
            return False
        except Exception as e:
            logger.error(f"Error sending message to '{subject}': {e}")
            return False

    def get_connection_status(self):
        """Get current connection status."""
        return self.is_connected and self.nc.is_connected