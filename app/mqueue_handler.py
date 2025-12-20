import asyncio
import json
from gpio_nats_logging import logger
from gpio_nats_settings import settings


class MessagingQueueHandler:
    """Class to handle messaging queue operations for dunebugger-starter."""

    def __init__(self, gpio_handler):
        self.mqueue_sender = None
        self.gpio_handler = gpio_handler
            
    async def process_mqueue_message(self, mqueue_message):
        """Callback method to process received messages."""
        # Parse the JSON string back into a dictionary
        try:
            data = mqueue_message.data.decode()
            message_json = json.loads(data)
        except (AttributeError, UnicodeDecodeError) as decode_error:
            logger.error(f"Failed to decode message data: {decode_error}. Raw message: {mqueue_message.data}")
            return
        except json.JSONDecodeError as json_error:
            logger.error(f"Failed to parse message as JSON: {json_error}. Raw message: {data}")
            return

        try:
            # Extract subject from message topic
            subject_parts = (mqueue_message.subject).split(".")
            if len(subject_parts) < 3:
                logger.error(f"Invalid subject format: {mqueue_message.subject}")
                return
            
            subject = subject_parts[2]  # dunebugger.starter.{subject}
            logger.debug(f"Processing message: Subject: {subject}. Body: {str(message_json)[:100]}")

            if subject in ["dunebugger_set"]:
                command = message_json["body"]
                command_reply_message = await self.process_command(command)
                return command_reply_message
            else:
                logger.warning(f"Unknown subject: {subject}. Ignoring message.")
                
        except KeyError as key_error:
            logger.error(f"KeyError: {key_error}. Message: {message_json}")
        except Exception as e:
            logger.error(f"Error processing message: {e}. Message: {message_json}")

    async def process_command(self, command):
        """Process command from message queue."""
        try:
            command_parts = command.split()
            if len(command_parts) < 1:
                return {"success": False, "message": "Empty command", "level": "error"}
            
            command_verb = command_parts[0].lower()
            command_args = command_parts[1:]
            
            if command_verb == "sw":
                return await self.handle_switch_command(command_args)
            else:
                return {"success": False, "message": f"Unknown command: {command_verb}", "level": "warning"}
                
        except Exception as e:
            logger.error(f"Command processing error: {str(e)}")
            return {"success": False, "message": f"Command processing error: {str(e)}", "level": "error"}

    async def handle_switch_command(self, command_args):
        """Handle sw <pin> <on|off> command."""
        if len(command_args) != 2:
            return {"success": False, "message": "Incorrect number of arguments for sw command. Usage: sw <pin> <on|off>", "level": "error"}
        
        if not command_args[0].isdigit():
            return {"success": False, "message": "Invalid GPIO number", "level": "error"}
        
        if command_args[1] not in ["on", "off"]:
            return {"success": False, "message": "Invalid action for sw command, must be 'on' or 'off'", "level": "error"}
        
        gpio_pin = int(command_args[0])
        action = command_args[1]
        
        try:
            # Warning: on GPIO the action is inverted: on = 0, off = 1 (following dunebugger pattern)
            gpio_value = 0 if action == "on" else 1
            result = self.gpio_handler.set_gpio_output(gpio_pin, gpio_value)
            
            if result is None:
                logger.info(f"GPIO {gpio_pin} set to {action}")
                return {"success": True, "message": f"GPIO {gpio_pin} set to {action}", "level": "info"}
            else:
                logger.error(f"Failed to set GPIO {gpio_pin}: {result}")
                return {"success": False, "message": result, "level": "error"}
                
        except Exception as e:
            logger.error(f"Error setting GPIO: {e}")
            return {"success": False, "message": f"Error setting GPIO: {e}", "level": "error"}

    def set_mqueue_sender(self, mqueue_sender):
        """Set the message queue sender for replies."""
        self.mqueue_sender = mqueue_sender

    async def dispatch_message(self, message_body, subject, recipient, reply_subject=None):
        """Send message via NATS if available."""
        # Only send message if mqueue_sender is available (NATS is enabled)
        if self.mqueue_sender is None:
            logger.debug(f"NATS disabled - not sending message. Subject: {subject}, Recipient: {recipient}")
            return
            
        message = {
            "body": message_body,
            "subject": subject,
            "source": getattr(settings, 'clientId', 'dunebugger-starter'),
        }
        await self.mqueue_sender.send(message, recipient, reply_subject)