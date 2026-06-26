import os
import logging
import sys

# Get the path to logs directory relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "agent.log")

# Configure logging
logger = logging.getLogger("agentic_store")
logger.setLevel(logging.INFO)

# Avoid adding duplicate handlers if they already exist
if not logger.handlers:
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File Handler
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler (stdout)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

def get_logger(name: str):
    """
    Returns a child logger of the main 'agentic_store' logger.
    """
    return logging.getLogger(f"agentic_store.{name}")
