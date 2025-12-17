import os
import subprocess


def is_raspberry_pi():
    """Check if the current system is a Raspberry Pi."""
    try:
        with open("/proc/device-tree/model") as model_file:
            model = model_file.read()
            if "Raspberry Pi" in model:
                return True
            else:
                return False
    except Exception:
        return False


def validate_path(path):
    """Validate if a path exists."""
    if os.path.exists(path):
        return True
    else:
        return False