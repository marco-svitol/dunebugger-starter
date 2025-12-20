import configparser
from ast import literal_eval
from os import path
import re
import atexit
from gpio_nats_logging import logger
from gpio_nats_settings import settings

if getattr(settings, 'ON_RASPBERRY_PI', False):
    import RPi.GPIO as GPIO  # type: ignore
else:
    # Mock GPIO for testing on non-Raspberry Pi systems
    class MockGPIO:
        BCM = "BCM"
        IN = "IN"
        OUT = "OUT"
        HIGH = 1
        LOW = 0
        PUD_UP = "PUD_UP"
        PUD_DOWN = "PUD_DOWN"
        
        @staticmethod
        def setmode(mode):
            logger.debug(f"Mock GPIO: Set mode to {mode}")
        
        @staticmethod
        def setup(pins, direction, initial=None):
            if isinstance(pins, (list, tuple)):
                for pin in pins:
                    logger.debug(f"Mock GPIO: Setup pin {pin} as {direction} with initial {initial}")
            else:
                logger.debug(f"Mock GPIO: Setup pin {pins} as {direction} with initial {initial}")
        
        @staticmethod
        def output(pin, value):
            logger.debug(f"Mock GPIO: Set pin {pin} to {value}")
        
        @staticmethod
        def input(pin):
            # Return mock value - LOW for outputs
            return 0
            
        @staticmethod
        def gpio_function(pin):
            # Mock function - return OUT for configured pins
            return MockGPIO.OUT
            
        @staticmethod
        def setwarnings(mode):
            logger.debug(f"Mock GPIO: Set warnings to {mode}")
        
        @staticmethod
        def cleanup():
            logger.debug("Mock GPIO: Cleanup called")
    
    GPIO = MockGPIO()


class StarterGPIOHandler:
    """GPIO handler for dunebugger-starter that manages output pins based on gpio.conf"""

    def __init__(self):
        # Load GPIO configuration from gpio.conf
        self.GPIOMap = {}
        self.channelsSetup = {}
        self.channels = {}
        self.logicalChannels = {}
        self.configured_pins = set()  # Track which pins are configured
        
        self.load_gpio_configuration()
        self.GPIO = GPIO
        
        # Initialize GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # Setup pins according to configuration
        for channel, config in self.channelsSetup.items():
            pin_setup, initial_state = config
            pins = self.channels[channel]
            
            if pin_setup == "OUT" and (initial_state == "HIGH" or initial_state == "LOW"):
                initial_value = GPIO.HIGH if initial_state == "HIGH" else GPIO.LOW
                for pin in pins:
                    GPIO.setup(pin, GPIO.OUT, initial=initial_value)
                    self.configured_pins.add(pin)
                    logger.debug(f"Configured GPIO {pin} as OUTPUT with initial {initial_state}")
            elif pin_setup == "IN" and (initial_state == "DOWN" or initial_state == "UP"):
                pull_up_down = GPIO.PUD_UP if initial_state == "UP" else GPIO.PUD_DOWN
                for pin in pins:
                    GPIO.setup(pin, GPIO.IN, pull_up_down=pull_up_down)
                    self.configured_pins.add(pin)
                    logger.debug(f"Configured GPIO {pin} as INPUT with pull {initial_state}")

        atexit.register(self.cleanup_gpios)
        logger.info(f"GPIO handler initialized with {len(self.configured_pins)} configured pins")

    def load_gpio_configuration(self):
        """Load GPIO configuration from gpio.conf file."""
        config = configparser.ConfigParser()
        # Set optionxform to lambda x: x to preserve case
        config.optionxform = lambda x: x
        try:
            gpio_config_path = path.join(path.dirname(path.abspath(__file__)), "config/gpio.conf")
            config.read(gpio_config_path)

            # Load Channels Setup
            try:
                for channelSetup, values in config.items("ChannelsSetup"):
                    channelSetupValues = values.split(", ")
                    self.channelsSetup[channelSetup] = channelSetupValues
            except (configparser.Error, ValueError) as e:
                logger.error(f"Error reading channel setup configuration: {e}")

            # Load Channels
            try:
                for physicalChannel, values in config.items("Channels"):
                    # Convert the values to tuple if there is more than one element
                    channel_values = literal_eval(values)
                    if isinstance(channel_values, tuple):
                        self.channels[physicalChannel] = channel_values
                    else:
                        self.channels[physicalChannel] = (channel_values,)
            except (configparser.Error, ValueError) as e:
                logger.error(f"Error reading channel configuration: {e}")

            # Load GPIOMapPhysical
            try:
                for logicalChannel, values in config.items("LogicalChannels"):
                    channel, index = self.__extract_variable_info(values)
                    if channel in self.channels and index < len(self.channels[channel]):
                        self.logicalChannels[logicalChannel] = self.channels[channel][index]
            except (configparser.Error, ValueError) as e:
                logger.error(f"Error reading LogicalChannels configuration: {e}")

            # Load GPIOMap
            try:
                for GPIOMap, values in config.items("GPIOMaps"):
                    logicalChannel, index = self.__extract_variable_info(values)
                    if logicalChannel in self.logicalChannels:
                        self.GPIOMap[GPIOMap] = self.logicalChannels[logicalChannel]
            except (configparser.Error, ValueError) as e:
                logger.error(f"Error reading GPIOMaps configuration: {e}")

        except Exception as e:
            logger.error(f"Error loading GPIO configuration: {e}")

    def __extract_variable_info(self, expression):
        """Extract variable information from expressions like 'var[0]'"""
        match = re.match(r'^(\w+)\[(\d+)\]$', expression)
        if match:
            return match.group(1), int(match.group(2))
        else:
            return expression, 0

    def set_gpio_output(self, gpio_pin, value):
        """Set GPIO pin output value."""
        # Check if pin is configured
        if gpio_pin not in self.configured_pins:
            return f"GPIO pin {gpio_pin} is not configured in gpio.conf"
        
        # Check if pin is configured as output
        try:
            gpio_mode = self.GPIO.gpio_function(gpio_pin)
            if gpio_mode != self.GPIO.OUT and getattr(settings, 'ON_RASPBERRY_PI', False):
                return f"GPIO pin {gpio_pin} is not configured as OUTPUT"
        except Exception as e:
            logger.warning(f"Could not check GPIO mode for pin {gpio_pin}: {e}")
        
        try:
            GPIO.output(gpio_pin, value)
            logger.debug(f"Set GPIO {gpio_pin} to {value}")
            return None  # Success
        except Exception as e:
            error_msg = f"Error setting GPIO {gpio_pin}: {e}"
            logger.error(error_msg)
            return error_msg

    def get_gpio_label(self, gpio_pin):
        """Get the label for a GPIO pin from the configuration."""
        for label, pin in self.GPIOMap.items():
            if pin == gpio_pin:
                return label
        return f"GPIO_{gpio_pin}"

    def get_gpio_status(self):
        """Get status of all configured GPIO pins."""
        gpio_status = []
        
        for gpio_pin in sorted(self.configured_pins):
            mode = "UNKNOWN"
            state = "UNKNOWN"
            switchstate = "UNKNOWN"
            label = self.get_gpio_label(gpio_pin)
            
            # Determine mode
            try:
                if self.GPIO.gpio_function(gpio_pin) == self.GPIO.IN:
                    mode = "INPUT"
                elif self.GPIO.gpio_function(gpio_pin) == self.GPIO.OUT:
                    mode = "OUTPUT"
            except Exception:
                mode = "ERROR"
            
            # Read state
            if mode == "INPUT" or mode == "OUTPUT":
                try:
                    state = "HIGH" if self.GPIO.input(gpio_pin) == 1 else "LOW"
                    # For switch state, invert the logic (following dunebugger pattern)
                    switchstate = "OFF" if self.GPIO.input(gpio_pin) == 1 else "ON"
                except Exception:
                    state = "ERROR"
                    switchstate = "ERROR"
            
            gpio_status.append({
                "pin": gpio_pin, 
                "label": label, 
                "mode": mode, 
                "state": state, 
                "switch": switchstate
            })
        
        return gpio_status

    def cleanup_gpios(self):
        """Cleanup GPIO resources."""
        logger.debug("Cleaning up GPIOs")
        try:
            GPIO.cleanup()
        except Exception as e:
            logger.error(f"Error during GPIO cleanup: {e}")