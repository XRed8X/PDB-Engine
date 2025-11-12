# Base command for all commands except help
CMD_BASE = "--command="

# Help command
HELP = "--help"

class Commands:
    """Available commands for the PDB Engine API"""
    PROTEIN_DESIGN_COMMAND = "ProteinDesign"
    
    PROTEIN_DESIGN = f"{CMD_BASE}{PROTEIN_DESIGN_COMMAND}"
    
    @classmethod
    def command_list(cls):
        """Returns a list of all available commands"""
        return [cls.PROTEIN_DESIGN]
    
    @classmethod
    def is_valid_command(cls, command: str) -> bool:
        """Check if the provided command is valid"""
        return command in cls.command_list()

class Arguments:
    """Arguments that require a value, for example the route of input file"""
    PDB = "--pdb="
    
    @staticmethod
    def format(argument: str, value: str) -> str:
        """Format an argument with its value"""
        return f"{argument}{value}"
    
class Flags:
    """Flags that do not require a value"""
    PPINT = "--ppint"
    INTERFACE_ONLY = "--interface_only"
    
    @classmethod
    def flag_list(cls):
        """Returns a list of all available flags"""
        return [cls.PPINT, cls.INTERFACE_ONLY]
    
    @classmethod
    def is_valid_flag(cls, flag: str) -> bool:
        """Check if the provided flag is valid"""
        return flag in cls.flag_list()

def get_command_base(command: str) -> str:
    """Get the full base command string"""
    return f"{CMD_BASE}{command}"

def build_command(
    command: str,
    pdb_path: str,
    flags: list = None
) -> list:
    """Build the full command with arguments and flags"""
    args = [get_command_base(command), Arguments.format(Arguments.PDB, pdb_path)]
    if flags:
        args.extend(flag for flag in flags if Flags.is_valid_flag(flag))
    return args

def build_help_command() -> list:
    """Build the help command"""
    return [HELP]