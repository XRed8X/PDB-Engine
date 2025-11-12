"""
Decorator and utilities for handling exceptions consistently.
"""

import functools
from core.logger import get_logger
from .base_exceptions import PDBEngineError
from .http_exceptions import handle_pdb_engine_error


def handle_exceptions(func):
    """
    Decorator to handle exceptions and convert them to HTTP exceptions.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger(f"pdbengine.exceptions.{func.__module__}.{func.__name__}")
        
        try:
            return await func(*args, **kwargs)
        except PDBEngineError as e:
            logger.error(f"PDB Engine error in {func.__name__}", extra={
                "error_type": type(e).__name__,
                "error_code": e.error_code,
                "error_message": e.message,
                "error_details": e.details
            })
            raise handle_pdb_engine_error(e)
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}", extra={
                "error_type": type(e).__name__,
                "error_message": str(e)
            }, exc_info=True)
            
            from .base_exceptions import PDBEngineError
            generic_error = PDBEngineError(
                message="An unexpected error occurred",
                error_code="INTERNAL_ERROR",
                details={"original_error": str(e)}
            )
            raise handle_pdb_engine_error(generic_error)
    
    return wrapper
