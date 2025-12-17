# Quick Configuration Guide

## To set up for a remote IP address (e.g., 192.168.1.100):

1. Edit `app/config/gpio-nats.conf`
2. Change the natsServer line:
   ```ini
   [NATS]
   natsServer = nats://192.168.1.100:4222
   ```

## Common customizations:

### Different GPIO pin:
```ini
[GPIO]
gpioPin = 24
```

### Different message:
```ini
[NATS]
natsMessage = trigger
```

### Different subject:
```ini
[NATS]
natsSubject = your.custom.topic
```

### Enable debug mode:
```ini
[General]
debugMode = True
```

## To run:
```bash
cd app
python3 main.py
```