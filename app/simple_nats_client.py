from nats.aio.client import Client as NATS
import json
import asyncio
import socket
import time
from gpio_nats_logging import logger


class SimpleNATSClient:
    """Simplified NATS client for sending messages only."""
    
    def __init__(self, servers, client_id="dunebugger-starter", connection_timeout=10, max_retries=3, retry_delay=5):
        self.nc = NATS()
        self.servers = servers if isinstance(servers, list) else [servers]
        self.client_id = client_id
        self.is_connected = False
        self.connection_timeout = connection_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.last_connection_attempt = 0
        
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
    
    def _can_connect_to_server(self, server_url):
        """Check if we can establish a basic TCP connection to the NATS server."""
        try:
            # Parse NATS URL to get host and port
            if '://' in server_url:
                url_parts = server_url.split('://', 1)[1]
            else:
                url_parts = server_url
            
            if ':' in url_parts:
                host, port_str = url_parts.rsplit(':', 1)
                port = int(port_str)
            else:
                host = url_parts
                port = 4222  # Default NATS port
            
            # Test TCP connection with short timeout
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)  # 3 second timeout for connection check
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Connection check failed for {server_url}: {e}")
            return False

    async def connect(self):
        """Connect to NATS server with retry logic."""
        # Check if we should throttle connection attempts
        current_time = time.time()
        if current_time - self.last_connection_attempt < self.retry_delay:
            logger.debug(f"Throttling connection attempt, waiting {self.retry_delay}s between attempts")
            return False
        
        self.last_connection_attempt = current_time
        
        # Check network connectivity first
        available_servers = []
        for server in self.servers:
            if self._can_connect_to_server(server):
                available_servers.append(server)
                logger.info(f"Server {server} is reachable")
            else:
                logger.warning(f"Server {server} is not reachable")
        
        if not available_servers:
            logger.error("No NATS servers are reachable via TCP")
            self.is_connected = False
            return False
        
        # Try to connect with retries
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting NATS connection (attempt {attempt + 1}/{self.max_retries})...")
                
                await asyncio.wait_for(
                    self.nc.connect(
                        servers=available_servers,
                        name=self.client_id,
                        reconnect_time_wait=10,
                        max_reconnect_attempts=5,  # Limited attempts for initial connection
                        connect_timeout=self.connection_timeout
                    ),
                    timeout=self.connection_timeout + 5  # Add buffer to asyncio timeout
                )
                
                logger.info(f"NATS client '{self.client_id}' connected successfully")
                self.is_connected = True
                return True
                
            except asyncio.TimeoutError:
                logger.warning(f"Connection attempt {attempt + 1} timed out after {self.connection_timeout}s")
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            
            if attempt < self.max_retries - 1:
                wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                logger.info(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
        
        logger.error(f"Failed to connect to NATS after {self.max_retries} attempts")
        self.is_connected = False
        return False

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