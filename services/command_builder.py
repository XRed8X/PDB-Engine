"""
Service responsible for securely building PDB Engine command-line invocations.
"""

from pathlib import Path
from typing import List, Union, Dict
from core import settings, Commands, Flags, build_command, CommandSecurityValidator, SecurityError
from models.models import ProteinDesignRequest


class PDBCommandBuilder:
    """Builds secure commands for executing PDB Engine."""

    @staticmethod
    def build_secure_command(input_pdb_path: Path, options: Union[ProteinDesignRequest, Dict]) -> List[str]:
        """Build secure command for executing PDB Engine."""

        # Validate command
        if not Commands.is_valid_command(Commands.PROTEIN_DESIGN):
            raise SecurityError(f"Invalid command: {Commands.PROTEIN_DESIGN}")
        
        # Handle both dict and ProteinDesignRequest types
        if isinstance(options, dict):
            ppint = options.get('ppint', False)
            interface_only = options.get('interface_only', False)
        else:
            # ProteinDesignRequest object
            ppint = options.ppint
            interface_only = options.interface_only

        # Build flag list
        flags = []
        if ppint:
            flags.append(Flags.PPINT)
        if interface_only:
            flags.append(Flags.INTERFACE_ONLY)

        # Validate all flags
        for flag in flags:
            if not Flags.is_valid_flag(flag):
                raise SecurityError(f"Invalid flag: {flag}")

        # Build command
        command_args = build_command(
            Commands.PROTEIN_DESIGN_COMMAND,
            str(input_pdb_path.absolute()),
            flags
        )

        # Security validation
        CommandSecurityValidator.validate_command_structure(command_args)

        # Full command
        full_command = [str(settings.PDBENGINE_BINARY_PATH)] + command_args

        print(f"Built secure command: {' '.join(full_command)}")
        return full_command
