import sys
import os
from loguru import logger
from datetime import datetime

# Remove default logger
logger.remove()

# Add structured JSON logging to stdout
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO",
    serialize=True,
    backtrace=True,
    diagnose=True
)

# Add file logging for errors
logger.add(
    "logs/error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="ERROR",
    rotation="10 MB",
    retention="30 days",
    serialize=True,
    backtrace=True,
    diagnose=True
)

# Add file logging for all levels
logger.add(
    "logs/app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="DEBUG",
    rotation="50 MB",
    retention="7 days",
    serialize=True
)

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Custom logger for API requests
api_logger = logger.bind(name="api")
db_logger = logger.bind(name="database")
auth_logger = logger.bind(name="auth") 