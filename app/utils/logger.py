import sys
import os
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True)

log_file_path = os.path.join(os.getcwd(), "application.log")
logger.add(log_file_path, level="INFO", rotation="10 MB", retention=5, encoding="utf-8")
