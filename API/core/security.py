"""
Security validator for PDB Engine commands using core command structure.
"""
import re
from pathlib import Path
from typing import List

from core.valid_commands import CommandValidator as Commands


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
            command_args: Command arguments to validate (without binary path)
            
        Returns:
            bool: True if command structure is valid
            
        Raises:
            SecurityError: If command structure is invalid
        """
        if not command_args:
            raise SecurityError("Empty command arguments")
        
        # First argument should be a valid command
        first_arg = command_args[0]
        if not Commands.is_valid_command(first_arg):
            raise SecurityError(f"Invalid command: {first_arg}")
        
        # Validate each argument for dangerous patterns
        for arg in command_args:
            cls._validate_argument_safety(arg)
        
        # Validate argument structure
        cls._validate_argument_structure(command_args[1:])  # Skip command itself
        
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
        i = 0
        while i < len(args):
            arg = args[i]
            
            # Check if it's a PDB argument
            if arg.startswith(Arguments.PDB):
                # Extract path and validate
                pdb_path = arg[len(Arguments.PDB):]
                cls._validate_pdb_path(pdb_path)
                i += 1
                continue
            
            # Check if it's a valid flag
            if Flags.is_valid_flag(arg):
                i += 1
                continue
            
            # If we get here, it's an unrecognized argument
            raise SecurityError(f"Unrecognized argument: {arg}")
    
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