"""
User-friendly error messages and helper functions.
"""

ERROR_MESSAGES = {
    "file_too_large": "The uploaded file is too large. Maximum size allowed is {max_size}MB.",
    "invalid_file_type": "Invalid file type. Only {allowed_types} files are allowed.",
    "invalid_filename": "Invalid filename. Filenames cannot contain special characters or path separators.",
    "pdb_engine_not_found": "PDB Engine is not available. Please contact the administrator.",
    "pdb_engine_timeout": "PDB Engine execution timed out. Please try with a smaller protein or contact support.",
    "pdb_engine_failed": "PDB Engine execution failed. Please check your input file and try again.",
    "invalid_method": "Invalid design method specified. Available methods: {available_methods}",
    "invalid_flags": "Invalid flags specified. Please check the documentation for valid flags.",
    "job_not_found": "Job not found. Please check the job ID and try again.",
    "workspace_error": "Internal workspace error. Please try again later.",
    "security_violation": "Security violation detected. Request blocked.",
    "configuration_error": "Server configuration error. Please contact the administrator.",
    "validation_error": "Input validation failed: {details}"
}


def get_user_friendly_message(error_type: str, **kwargs) -> str:
    """
    Get a user-friendly error message.
    """
    template = ERROR_MESSAGES.get(error_type, "An unexpected error occurred. Please try again.")
    try:
        return template.format(**kwargs)
    except KeyError:
        return template
