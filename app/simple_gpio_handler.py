import asyncio
from gpio_nats_logging import logger
from gpio_nats_settings import settings

if settings.ON_RASPBERRY_PI and settings.gpioEnabled:
    import RPi.GPIO as GPIO
else:
    # Mock GPIO for testing on non-Raspberry Pi systems
    class MockGPIO:
        BCM = "BCM"
        IN = "IN"
        PUD_UP = "PUD_UP"
        PUD_DOWN = "PUD_DOWN"
        RISING = "RISING"
        FALLING = "FALLING"
        BOTH = "BOTH"
        
        @staticmethod
        def setmode(mode):
            logger.debug(f"Mock GPIO: Set mode to {mode}")
        
        @staticmethod
        def setup(pin, direction, pull_up_down=None):
            logger.debug(f"Mock GPIO: Setup pin {pin} as {direction} with pull {pull_up_down}")
        
        @staticmethod
        def add_event_detect(pin, edge, callback=None, bouncetime=None):
            logger.debug(f"Mock GPIO: Added event detect on pin {pin} for {edge} edge")
        
        @staticmethod
        def remove_event_detect(pin):
            logger.debug(f"Mock GPIO: Removed event detect on pin {pin}")
        
        @staticmethod
        def cleanup():
            logger.debug("Mock GPIO: Cleanup called")
    
    GPIO = MockGPIO()


class SimpleGPIOHandler:
    """Simple GPIO handler for detecting input changes."""
    
    def __init__(self, callback_function=None):
        self.gpio_pin = getattr(settings, 'gpioPin', 21)  # Default to pin 21

        self.edge_detection = 'RISING'
        self.bounce_time = int(getattr(settings, 'bouncingThreshold', 200) * 1000)  # Convert to milliseconds
        self.callback_function = callback_function
        
        # Initialize GPIO
        self._setup_gpio()
        
    def _setup_gpio(self):
        """Setup GPIO configuration."""
        try:
            GPIO.setmode(GPIO.BCM)
            
            # Configure pull up/down
            pull = GPIO.PUD_DOWN
            
            # Setup pin
            GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down=pull)
            
            # Configure edge detection
            edge = GPIO.RISING
            
            # Add event detection
            GPIO.add_event_detect(
                self.gpio_pin,
                edge,
                callback=self._gpio_callback,
                #bouncetime=self.bounce_time
            )
            
            logger.info(f"GPIO pin {self.gpio_pin} configured for RISING edge detection")
            logger.info(f"Pull resistor: DOWN, Bounce time: {self.bounce_time}ms")
            
        except Exception as e:
            logger.error(f"Error setting up GPIO: {e}")
    
    def _gpio_callback(self, channel):
        """GPIO interrupt callback."""
        logger.info(f"GPIO event detected on pin {channel}")
        
        if self.callback_function:
            try:
                # Create an event loop if one doesn't exist
                loop = None
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        raise RuntimeError("Event loop is closed")
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Run the callback
                if asyncio.iscoroutinefunction(self.callback_function):
                    if loop.is_running():
                        # If loop is already running, schedule the callback
                        asyncio.create_task(self.callback_function(channel))
                    else:
                        # Run the callback in the event loop
                        loop.run_until_complete(self.callback_function(channel))
                else:
                    # Call synchronous function
                    self.callback_function(channel)
                    
            except Exception as e:
                logger.error(f"Error in GPIO callback: {e}")
    
    def set_callback(self, callback_function):
        """Set or change the callback function."""
        self.callback_function = callback_function
        logger.info("GPIO callback function updated")
    
    def cleanup(self):
        """Cleanup GPIO resources."""
        try:
            GPIO.remove_event_detect(self.gpio_pin)
            GPIO.cleanup()
            logger.info("GPIO cleanup completed")
        except Exception as e:
            logger.error(f"Error during GPIO cleanup: {e}")