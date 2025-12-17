import logging
import logging.config
from os import path

# Create a simple logging configuration directly in code for simplicity
def setup_logging(log_level=logging.INFO):
    """Setup logging with colored console output."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Create file handler
    log_file = path.join(path.dirname(path.abspath(__file__)), '../dunebugger-starter.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Setup root logger
    logger = logging.getLogger('dunebugger-starter')
    logger.setLevel(log_level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Create default logger instance
logger = setup_logging()