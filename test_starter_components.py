#!/usr/bin/env python3
"""
Test script for dunebugger-starter NATS subscriber and GPIO handler
"""

import asyncio
import json
from gpio_nats_logging import logger
from starter_gpio_handler import StarterGPIOHandler
from mqueue_handler import MessagingQueueHandler


async def test_gpio_handler():
    """Test the GPIO handler functionality"""
    logger.info("Testing GPIO Handler...")
    
    try:
        gpio_handler = StarterGPIOHandler()
        
        # Test getting GPIO status
        status = gpio_handler.get_gpio_status()
        logger.info(f"GPIO Status: {len(status)} pins configured")
        for pin_status in status:
            logger.info(f"  Pin {pin_status['pin']}: {pin_status['label']} - {pin_status['mode']} - {pin_status['state']}")
        
        # Test setting GPIO (if any output pins configured)
        output_pins = [pin for pin in status if pin['mode'] == 'OUTPUT']
        if output_pins:
            test_pin = output_pins[0]['pin']
            logger.info(f"Testing GPIO output on pin {test_pin}")
            
            # Test turning ON (0 value - inverted logic)
            result = gpio_handler.set_gpio_output(test_pin, 0)
            if result is None:
                logger.info(f"Successfully set pin {test_pin} ON")
            else:
                logger.error(f"Failed to set pin {test_pin} ON: {result}")
            
            # Test turning OFF (1 value - inverted logic)
            result = gpio_handler.set_gpio_output(test_pin, 1)
            if result is None:
                logger.info(f"Successfully set pin {test_pin} OFF")
            else:
                logger.error(f"Failed to set pin {test_pin} OFF: {result}")
        else:
            logger.warning("No OUTPUT pins configured for testing")
        
        gpio_handler.cleanup_gpios()
        logger.info("GPIO Handler test completed")
        
    except Exception as e:
        logger.error(f"GPIO Handler test failed: {e}")


async def test_message_handler():
    """Test the message queue handler functionality"""
    logger.info("Testing Message Queue Handler...")
    
    try:
        gpio_handler = StarterGPIOHandler()
        mq_handler = MessagingQueueHandler(gpio_handler)
        
        # Create mock message for testing
        class MockMessage:
            def __init__(self, subject, data):
                self.subject = subject
                self.data = data.encode()
        
        # Test valid sw command
        message_data = json.dumps({"body": "sw 5 on"})
        mock_message = MockMessage("dunebugger.starter.dunebugger_set", message_data)
        
        logger.info("Testing valid sw command: 'sw 5 on'")
        await mq_handler.process_mqueue_message(mock_message)
        
        # Test invalid command
        message_data = json.dumps({"body": "invalid_command"})
        mock_message = MockMessage("dunebugger.starter.dunebugger_set", message_data)
        
        logger.info("Testing invalid command")
        await mq_handler.process_mqueue_message(mock_message)
        
        # Test invalid GPIO number
        message_data = json.dumps({"body": "sw abc on"})
        mock_message = MockMessage("dunebugger.starter.dunebugger_set", message_data)
        
        logger.info("Testing invalid GPIO number")
        await mq_handler.process_mqueue_message(mock_message)
        
        gpio_handler.cleanup_gpios()
        logger.info("Message Queue Handler test completed")
        
    except Exception as e:
        logger.error(f"Message Queue Handler test failed: {e}")


async def main():
    """Main test function"""
    logger.info("Starting dunebugger-starter tests...")
    
    await test_gpio_handler()
    print("-" * 50)
    await test_message_handler()
    
    logger.info("All tests completed")


if __name__ == "__main__":
    asyncio.run(main())