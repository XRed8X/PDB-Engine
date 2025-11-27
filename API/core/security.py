"""
Security validator for PDB Engine commands using core command structure.
"""
import re
from pathlib import Path
from typing import List

from core.valid_commands import CommandValidator


class CommandSecurityValidator:
    """Validates PDB Engine commands against injection attacks."""
    
    # Dangerous patterns that should never appear in any argument
    DANGEROUS_PATTERNS = [
        r'[;&|`$(){}[\]<>]',  # Shell metacharacters
        r'\.\.',              # Directory traversal
        r'/bin/',             # System binaries
        r'/usr/',             # System directories
        r'sudo',              # Privilege escalation
        r'chmod',             # Permission changes
        r'rm\s+-rf',          # Destructive commands
        r'>\s*/',             # Root redirects
        r'\|\s*\w+',          # Pipe commands
        r'&&',                # Command chaining
        r'\|\|',              # Or operators
        r'nc\s+',             # Netcat
        r'wget\s+',           # Download commands
        r'curl\s+',           # Download commands
    ]
    
    @classmethod
    def validate_command_structure(cls, command_args: List[str]) -> bool:
        """
        Validates that command follows the expected structure.
        
        Args:
            command_args: Command arguments to validate (first element should be --command=CommandName)
            
        Returns:
            bool: True if command structure is valid
            
        Raises:
            SecurityError: If command structure is invalid
        """
        if not command_args:
            raise SecurityError("Empty command arguments")
        
        # First argument should be --command=CommandName
        first_arg = command_args[0]
        if not first_arg.startswith("--command="):
            raise SecurityError("First argument must be --command=CommandName")
        
        # Extract and validate command name
        command_name = first_arg.replace("--command=", "")
        if not CommandValidator.is_valid_command(command_name):
            raise SecurityError(f"Invalid command: {command_name}")
        
        # Validate each argument for dangerous patterns
        for arg in command_args:
            cls._validate_argument_safety(arg)
        
        # Validate argument structure
        cls._validate_argument_structure(command_args[1:])
        
        return True
    
    @classmethod
    def _validate_argument_safety(cls, arg: str) -> None:
        """Validate that an argument doesn't contain dangerous patterns."""
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, arg, re.IGNORECASE):
                raise SecurityError(f"Dangerous pattern detected in argument: {arg}")
    
    @classmethod
    def _validate_argument_structure(cls, args: List[str]) -> None:
        """Validate that arguments follow expected PDB Engine structure."""
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                key = key.replace('--', '')

                if not CommandValidator.is_valid_argument(key):
                    raise SecurityError(f"Unknown argument: {key}")

                if key == 'pdb' and value:
                    cls._validate_pdb_path(value)
            elif arg.startswith('--'):
                flag = arg.replace('--', '')
                if not CommandValidator.is_valid_flag(flag):
                    raise SecurityError(f"Unknown flag: {flag}")
            else:
                raise SecurityError(f"Unrecognized argument format: {arg}")
    
    @classmethod
    def _validate_pdb_path(cls, pdb_path: str) -> None:
        """Validate PDB file path for security."""
        path = Path(pdb_path)
        
        # Check for directory traversal
        if '..' in str(path):
            raise SecurityError("Directory traversal detected in PDB path")
        
        # Check file extension
        if not pdb_path.lower().endswith('.pdb'):
            raise SecurityError("Invalid file extension, only .pdb files allowed")
        
        # Check path length (prevent buffer overflow attempts)
        if len(pdb_path) > 1000:
            raise SecurityError("PDB path too long")
        
        # Check for null bytes
        if '\x00' in pdb_path:
            raise SecurityError("Null byte detected in PDB path")
    
    @classmethod
    def validate_filename(cls, filename: str) -> str:
        """
        Validates and sanitizes a filename.
        
        Args:
            filename: Original filename
            
        Returns:
            str: Sanitized filename
            
        Raises:
            SecurityError: If filename is dangerous
        """
        if not filename:
            raise SecurityError("Empty filename")
        
        # Check for dangerous patterns
        cls._validate_argument_safety(filename)
        
        # Remove or replace dangerous characters
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Ensure it ends with .pdb
        if not sanitized.lower().endswith('.pdb'):
            sanitized += '.pdb'
        
        # Limit length
        if len(sanitized) > 100:
            name, ext = sanitized.rsplit('.', 1)
            sanitized = name[:95] + '.' + ext
        
        return sanitized


class SecurityError(Exception):
    """Custom exception for security violations."""
    pass