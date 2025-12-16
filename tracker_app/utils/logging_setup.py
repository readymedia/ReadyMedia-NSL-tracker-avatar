import sys
from loguru import logger
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: Path = None):
    """Setup loguru logging"""
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stderr, 
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # File handler
    if log_file:
        logger.add(
            log_file,
            rotation="10 MB",
            level="DEBUG"
        )
