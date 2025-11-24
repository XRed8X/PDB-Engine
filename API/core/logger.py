import logging
from core.settings import settings

def _resolve_log_level(level) -> int:
    if isinstance(level, str):
        return getattr(logging, level.upper(), logging.INFO)
    elif isinstance(level, int):
        return level
    return logging.INFO

def get_logger(name: str = "PDB Engine Backend") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(_resolve_log_level(settings.LOG_LEVEL))
    return logger

logger = get_logger()
preprocessing_logger = logging.getLogger("Preprocessing")
preprocessing_logger.setLevel(_resolve_log_level(settings.PREPROCESSING_LOG_LEVEL))