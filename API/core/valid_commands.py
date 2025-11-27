"""
Generic command configuration for PDB Engine.
All commands handled dynamically based on pdb_options.json
"""
from core.settings import settings

# Base command prefix
CMD_BASE = "--command="

# Help command
HELP = "--help"

class CommandValidator:
    """Validates commands, arguments and flags dynamically"""
    
    # Valid commands from pdb_options.json
    VALID_COMMANDS = {
        "ComputeBinding", "ComputeEvolutionScore", "ComputeResEnergy",
        "ComputeRotEnergy", "ComputeStability", "ComputeResPairEnergy",
        "ProteinDesign", "AddPolarHydrogen", "BuildMutant", "CalcPhiPsi",
        "CalcResMinRMSD", "CheckClash0", "CheckClash1", "CheckClash2",
        "CheckResInRotLib", "CompareProtSideChain", "FindCoreRes",
        "FindIntermediateRes", "FindInterfaceRes", "FindSurfaceRes",
        "Minimize", "OptimizeHydrogen", "RepairStructure",
        "ShowResComposition", "PredPhiPsi", "PredSS", "PredSA",
        "CalcResBfactor", "OptimizeWeight", "MakeLigParamAndTopo",
        "MakeLigPoses", "AnalyzeLigPoses", "ScreenLigPoses",
        "WriteFirstLigConfAsMol2", "SelectResWithin"
    }
    
    # Valid arguments
    VALID_ARGUMENTS = {
        "pdb", "prefix", "wbind", "seq", "resfile", "resi", "resi_pair",
        "excl_resi", "rotlib", "design_chains", "ntraj", "mutant_file",
        "pdb2", "ncut_cb_core", "ppi_shell1", "ppi_shell2", "ncut_cb_surf",
        "wprof", "lig_param", "lig_topo", "init_3atoms", "lig_placing",
        "read_lig_poses", "scrn_by_orien", "scrn_by_vdw_pctl", "scrn_by_rmsd",
        "mol2", "within_residues", "within_range"
    }
    
    # Valid flags
    VALID_FLAGS = {
        "physics", "monomer", "evolution", "evo_all_terms", "seed_from_nat_seq",
        "ppint", "interface_only", "excl_cys_rots", "no_hydrogen",
        "wildtype_only", "debug", "keep_water", "dry_run", "enzyme", "protlig"
    }
    
    @classmethod
    def is_valid_command(cls, command: str) -> bool:
        """Check if the provided command is valid"""
        return command in cls.VALID_COMMANDS
    
    @classmethod
    def is_valid_argument(cls, arg: str) -> bool:
        """Check if argument is valid"""
        return arg in cls.VALID_ARGUMENTS
    
    @classmethod
    def is_valid_flag(cls, flag: str) -> bool:
        """Check if the provided flag is valid"""
        return flag in cls.VALID_FLAGS

def format_argument(argument: str, value: str) -> str:
    """Format an argument with its value"""
    return f"--{argument}={value}"

def format_flag(flag: str) -> str:
    """Format a flag"""
    return f"--{flag}"

def get_command_base(command: str) -> str:
    """Get the full base command string"""
    return f"{CMD_BASE}{command}"

def build_command_from_dict(
    command: str,
    arguments: dict = None,
    flags: list = None
) -> list:
    """
    Build command from dictionary (from UI JSON).
    
    Args:
        command: Command name
        arguments: Dictionary of argument key-value pairs
        flags: List of flag names
        
    Returns:
        List of command arguments ready for execution
    """
    # Start with base command
    # When using Docker, we don't include the binary path (it's the entrypoint)
    if settings.USE_DOCKER:
        cmd_args = [get_command_base(command)]
    else:
        cmd_args = [str(settings.PDBENGINE_BINARY_PATH), get_command_base(command)]
    
    # Add arguments dynamically
    if arguments:
        for key, value in arguments.items():
            if CommandValidator.is_valid_argument(key) and value:
                cmd_args.append(format_argument(key, str(value)))
    
    # Add flags dynamically
    if flags:
        for flag in flags:
            if CommandValidator.is_valid_flag(flag):
                cmd_args.append(format_flag(flag))
    
    return cmd_args

def build_help_command() -> list:
    """Build the help command"""
    return [HELP]