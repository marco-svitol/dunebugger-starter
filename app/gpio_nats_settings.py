from os import path
import configparser
try:
    from dotenv import load_dotenv
    dotenv_available = True
except ImportError:
    dotenv_available = False
from gpio_nats_logging import logger
from utils import is_raspberry_pi


class GPIONATSSettings:
    """Configuration settings for dunebugger-starter."""
    
    def __init__(self):
        if dotenv_available:
            load_dotenv()
        self.config = configparser.ConfigParser()
        # Set optionxform to lambda x: x to preserve case
        self.config.optionxform = lambda x: x
        
        # Configuration file path
        self.config_file = path.join(path.dirname(path.abspath(__file__)), "config/dunebugger-starter.conf")
        
        # Load configuration
        self.load_configuration()
        
        # Check if we're on Raspberry Pi
        self.ON_RASPBERRY_PI = is_raspberry_pi()
        logger.info(f"Running on Raspberry Pi: {self.ON_RASPBERRY_PI}")

    def load_configuration(self):
        """Load configuration from config file."""
        try:
            self.config.read(self.config_file)
            
            # Load General settings
            if self.config.has_section("General"):
                for option in self.config.options("General"):
                    value = self.config.get("General", option)
                    setattr(self, option, self.validate_option(option, value))
                    logger.debug(f"Setting {option}: {value}")
            
            # Load NATS settings
            if self.config.has_section("NATS"):
                for option in self.config.options("NATS"):
                    value = self.config.get("NATS", option)
                    setattr(self, option, self.validate_option(option, value))
                    logger.debug(f"Setting {option}: {value}")
            
            # Load GPIO settings
            if self.config.has_section("GPIO"):
                for option in self.config.options("GPIO"):
                    value = self.config.get("GPIO", option)
                    setattr(self, option, self.validate_option(option, value))
                    logger.debug(f"Setting {option}: {value}")
                    
            logger.info("Configuration loaded successfully")
        except configparser.Error as e:
            logger.error(f"Error reading configuration file {self.config_file}: {e}")
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_file}")

    def validate_option(self, option, value):
        """Validate and convert configuration options."""
        # Boolean options
        boolean_options = ['gpioEnabled', 'natsEnabled', 'debugMode']
        if option in boolean_options:
            return value.lower() in ['true', '1', 'yes', 'on']
        
        # Integer options
        integer_options = ['gpioPin', 'natsPort', 'natsTimeout', 'natsMaxRetries', 'natsRetryDelay']
        if option in integer_options:
            try:
                return int(value)
            except ValueError:
                logger.error(f"Invalid integer value for {option}: {value}")
                return 0
        
        # Float options
        float_options = ['bouncingThreshold']
        if option in float_options:
            try:
                return float(value)
            except ValueError:
                logger.error(f"Invalid float value for {option}: {value}")
                return 0.0
        
        # Return as string for all other options
        return value


# Create global settings instance
settings = GPIONATSSettings()