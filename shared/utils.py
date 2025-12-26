"""
Shared Utilities and Constants
This file contains all constants and helper functions used across the application.
"""

import os
import logging
from datetime import datetime

# ==================== NETWORK CONFIGURATION ====================

# Server Configuration
SERVER_HOST = '0.0.0.0'  # Listen on all network interfaces
SERVER_PORT = 5555       # Port number for the server
BUFFER_SIZE = 4096       # Size of data buffer for socket operations
MAX_CLIENTS = 100        # Maximum number of concurrent clients

# Connection Settings
CONNECTION_TIMEOUT = 30  # Seconds before connection timeout
RECONNECT_DELAY = 5      # Seconds to wait before reconnection attempt
MAX_RECONNECT_ATTEMPTS = 5  # Maximum reconnection attempts

# ==================== DATABASE CONFIGURATION ====================

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database path
DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'chat.db')

# ==================== MESSAGE CONFIGURATION ====================

# Message limits
MAX_MESSAGE_LENGTH = 1000  # Maximum characters in a message
MAX_USERNAME_LENGTH = 20   # Maximum characters in username
MIN_USERNAME_LENGTH = 3    # Minimum characters in username

# ==================== LOGGING CONFIGURATION ====================

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Log file path
LOG_FILE = os.path.join(LOGS_DIR, f'chat_app_{datetime.now().strftime("%Y%m%d")}.log')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # Also print to console
    ]
)

logger = logging.getLogger('ChatApp')


# ==================== HELPER FUNCTIONS ====================

def log_info(message):
    """Log an info message."""
    logger.info(message)


def log_error(message):
    """Log an error message."""
    logger.error(message)


def log_warning(message):
    """Log a warning message."""
    logger.warning(message)


def log_debug(message):
    """Log a debug message."""
    logger.debug(message)


def get_timestamp():
    """
    Get current timestamp in readable format.
    
    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_time_only():
    """
    Get current time only (no date).
    
    Returns:
        str: Formatted time (HH:MM:SS)
    """
    return datetime.now().strftime("%H:%M:%S")


def validate_username(username):
    """
    Validate username according to rules.
    
    Args:
        username (str): Username to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < MIN_USERNAME_LENGTH:
        return False, f"Username must be at least {MIN_USERNAME_LENGTH} characters"
    
    if len(username) > MAX_USERNAME_LENGTH:
        return False, f"Username must be at most {MAX_USERNAME_LENGTH} characters"
    
    if not username.isalnum() and '_' not in username:
        return False, "Username can only contain letters, numbers, and underscores"
    
    if username[0].isdigit():
        return False, "Username cannot start with a number"
    
    return True, ""


def validate_message(message_text):
    """
    Validate message text.
    
    Args:
        message_text (str): Message to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not message_text or message_text.strip() == "":
        return False, "Message cannot be empty"
    
    if len(message_text) > MAX_MESSAGE_LENGTH:
        return False, f"Message too long (max {MAX_MESSAGE_LENGTH} characters)"
    
    return True, ""


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
    
    Returns:
        str: Formatted size (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def create_directories():
    """
    Create necessary directories if they don't exist.
    """
    directories = [
        os.path.join(PROJECT_ROOT, 'database'),
        os.path.join(PROJECT_ROOT, 'logs')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    log_info("Directories created/verified")


# ==================== COLOR CODES (for terminal output) ====================

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ==================== INITIALIZATION ====================

# Create necessary directories on import
create_directories()

# Log startup
log_info("=" * 50)
log_info("Chat Application Utilities Loaded")
log_info(f"Server will run on {SERVER_HOST}:{SERVER_PORT}")
log_info(f"Database location: {DB_PATH}")
log_info(f"Log file: {LOG_FILE}")
log_info("=" * 50)
