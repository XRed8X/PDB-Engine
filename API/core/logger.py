import logging
from core.settings import settings

def get_logger(name: str = "PDB Engine Backend") -> logging.Logger:
    """ Configure and return a logger instance """
    # Create logger
    logger = logging.getLogger(name)
    # Avoid adding multiple handlers if logger is already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), getattr(logging, logging.INFO)))
    return logger

logger = get_logger()