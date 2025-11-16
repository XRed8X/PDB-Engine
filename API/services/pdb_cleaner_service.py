"""
Service responsible for validating and cleaning PDB files before processing.
Contains business logic for determining when cleaning is needed and applying filters.
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from Bio.PDB import PDBParser, PDBIO, PDBExceptions
from Bio.PDB.Polypeptide import is_aa

from utils.pdb_filters import LimpiadorPDB, ProteinChainDetector
from core.settings import settings

logger = logging.getLogger(__name__)


class PDBCleanerService:
    """
    Service class for PDB validation and cleaning operations.
    Separates the policy (decide if cleaning is needed) from the action (perform cleaning).
    """

    def __init__(self):
        self.parser = PDBParser(QUIET=True)
        self.io = PDBIO()

    def validate_and_clean(self, pdb_path: str, keep_all_chains: bool = True) -> str:
        """
        Main entry point: detects if PDB needs cleaning; if not, returns original path;
        if yes, generates and returns path of cleaned file.
        
        Args:
            pdb_path: Path to input PDB file
            keep_all_chains: Whether to keep all protein chains (recommended for protein-protein interfaces)
            
        Returns:
            str: Path to cleaned file or original file if no cleaning needed
            
        Raises:
            FileNotFoundError: If input PDB file doesn't exist
            PDBException: If PDB file cannot be parsed or processed
        """
        logger.info(f"Starting PDB validation and cleaning for: {pdb_path}")
        
        # Validate input file
        if not Path(pdb_path).exists():
            raise FileNotFoundError(f"PDB file not found: {pdb_path}")
        
        # Check if cleaning is needed
        if not getattr(settings, 'PREPROCESSING_ENABLED', True):
            logger.info("PDB preprocessing is disabled in settings")
            return pdb_path
            
        try:
            needs_cleaning = self.needs_cleaning(pdb_path)
            
            if not needs_cleaning:
                logger.info("PDB file does not need cleaning, using original file")
                return pdb_path
            
            # Generate output path for cleaned file
            input_path = Path(pdb_path)
            output_dir = input_path.parent
            clean_filename = f"{input_path.stem}_cleaned.pdb"
            output_path = str(output_dir / clean_filename)
            
            # Perform cleaning
            cleaned_path = self.clean(pdb_path, output_path, 
                                    chains_to_keep=None if keep_all_chains else None)
            
            logger.info(f"PDB cleaning completed. Clean file: {cleaned_path}")
            return cleaned_path
            
        except Exception as e:
            logger.error(f"Error during PDB validation/cleaning: {e}")
            # If cleaning fails, return original file (graceful degradation)
            logger.warning("Falling back to original PDB file due to cleaning error")
            return pdb_path

    def needs_cleaning(self, pdb_path: str) -> bool:
        """
        Heuristics to determine if PDB has unwanted ions, water, ligands,
        hydrogens, non-standard residues, or non-amino acid chains.
        
        Args:
            pdb_path: Path to PDB file
            
        Returns:
            bool: True if cleaning is needed, False otherwise
        """
        logger.info(f"Analyzing PDB file for cleaning needs: {pdb_path}")
        
        try:
            structure = self.parser.get_structure("analysis", pdb_path)
            
            # Counters for analysis
            total_residues = 0
            protein_residues = 0
            water_count = 0
            ion_count = 0
            ligand_count = 0
            hydrogen_count = 0
            non_standard_aa = 0
            
            # Define sets for detection
            water_molecules = {"HOH", "WAT", "H2O", "TIP", "SOL"}
            common_ions = {
                "NA", "CL", "K", "MG", "CA", "ZN", "FE", "MN", "CU", "NI",
                "SO4", "PO4", "NO3", "CO3", "HCO3", "ACE", "NH4"
            }
            common_ligands = {
                "ATP", "ADP", "AMP", "GTP", "GDP", "GMP", "NAD", "NADH", 
                "FAD", "FMN", "COA", "HEM", "HEME", "PLP", "B12"
            }
            
            # Analyze structure
            for model in structure:
                for chain in model:
                    for residue in chain:
                        total_residues += 1
                        residue_name = residue.get_resname().strip()
                        
                        # Count different types
                        if residue_name in water_molecules:
                            water_count += 1
                        elif residue_name in common_ions:
                            ion_count += 1
                        elif residue_name in common_ligands:
                            ligand_count += 1
                        elif is_aa(residue, standard=True):
                            protein_residues += 1
                        else:
                            non_standard_aa += 1
                        
                        # Count hydrogen atoms
                        for atom in residue:
                            if atom.element == "H":
                                hydrogen_count += 1
            
            # Log analysis results
            logger.info(f"PDB Analysis Results:")
            logger.info(f"  Total residues: {total_residues}")
            logger.info(f"  Protein residues: {protein_residues}")
            logger.info(f"  Water molecules: {water_count}")
            logger.info(f"  Ions: {ion_count}")
            logger.info(f"  Ligands: {ligand_count}")
            logger.info(f"  Hydrogen atoms: {hydrogen_count}")
            logger.info(f"  Non-standard residues: {non_standard_aa}")
            
            # Determine if cleaning is needed
            cleaning_needed = (
                water_count > 0 or
                ion_count > 0 or
                ligand_count > 0 or
                hydrogen_count > 0 or
                non_standard_aa > 0
            )
            
            if cleaning_needed:
                reasons = []
                if water_count > 0:
                    reasons.append(f"{water_count} water molecules")
                if ion_count > 0:
                    reasons.append(f"{ion_count} ions")
                if ligand_count > 0:
                    reasons.append(f"{ligand_count} ligands")
                if hydrogen_count > 0:
                    reasons.append(f"{hydrogen_count} hydrogen atoms")
                if non_standard_aa > 0:
                    reasons.append(f"{non_standard_aa} non-standard residues")
                
                logger.info(f"Cleaning needed due to: {', '.join(reasons)}")
            else:
                logger.info("No cleaning needed - structure contains only standard protein residues")
            
            return cleaning_needed
            
        except Exception as e:
            logger.error(f"Error analyzing PDB file: {e}")
            # If analysis fails, assume cleaning is needed for safety
            return True

    def clean(self, pdb_path: str, output_path: str, 
              chains_to_keep: Optional[List[str]] = None) -> str:
        """
        Apply LimpiadorPDB to produce clean PDB and return output path.
        
        Args:
            pdb_path: Path to input PDB file
            output_path: Path for output cleaned PDB file
            chains_to_keep: Optional list of chain IDs to keep (None = auto-detect protein chains)
            
        Returns:
            str: Path to cleaned output file
            
        Raises:
            Exception: If cleaning process fails
        """
        logger.info(f"Starting PDB cleaning: {pdb_path} -> {output_path}")
        
        try:
            # Parse input structure
            structure = self.parser.get_structure("input", pdb_path)
            
            # Auto-detect protein chains if not specified
            if chains_to_keep is None:
                chain_detector = ProteinChainDetector()
                chain_info = chain_detector.get_protein_chains(structure)
                
                if getattr(settings, 'PREPROCESSING_KEEP_ALL_CHAINS_BY_DEFAULT', True):
                    chains_to_keep = chain_detector.get_protein_chains_only(chain_info)
                else:
                    # Keep only the longest chain
                    longest_chain = chain_detector.get_longest_chain(chain_info)
                    chains_to_keep = [longest_chain] if longest_chain else []
            
            logger.info(f"Cleaning with chains: {chains_to_keep}")
            
            # Create output directory if needed
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Apply cleaning filter
            cleaner = LimpiadorPDB(chains_to_keep=chains_to_keep)
            
            # Save cleaned structure
            self.io.set_structure(structure)
            self.io.save(output_path, select=cleaner)
            
            # Validate cleaned file
            self._validate_cleaned_file(output_path, chains_to_keep)
            
            logger.info(f"PDB cleaning completed successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to clean PDB file: {e}")
            raise Exception(f"PDB cleaning failed: {e}") from e

    def _validate_cleaned_file(self, cleaned_path: str, expected_chains: List[str]) -> None:
        """
        Validate that the cleaned file contains expected protein chains.
        
        Args:
            cleaned_path: Path to cleaned PDB file
            expected_chains: List of expected chain IDs
        """
        try:
            structure = self.parser.get_structure("validation", cleaned_path)
            chain_detector = ProteinChainDetector()
            chain_info = chain_detector.get_protein_chains(structure)
            
            found_chains = list(chain_info.keys())
            logger.info(f"Validation - Expected chains: {expected_chains}, Found: {found_chains}")
            
            if not found_chains:
                raise ValueError("Cleaned PDB file contains no protein chains")
            
            # Log summary
            total_residues = sum(info["amino_acid_count"] for info in chain_info.values())
            logger.info(f"Cleaned file validation passed: {len(found_chains)} chains, {total_residues} total residues")
            
            # Warn if interface analysis may not be possible
            if len(found_chains) == 1:
                logger.warning("Cleaned PDB has only one chain - protein-protein interface analysis may not be possible")
            else:
                logger.info(f"Cleaned PDB has {len(found_chains)} chains - suitable for interface analysis")
                
        except Exception as e:
            logger.error(f"Validation of cleaned PDB failed: {e}")
            # Don't raise exception here - just log the issue

    def get_cleaning_summary(self, original_path: str, cleaned_path: str) -> Dict[str, Any]:
        """
        Generate a summary comparing original and cleaned PDB files.
        
        Args:
            original_path: Path to original PDB file
            cleaned_path: Path to cleaned PDB file
            
        Returns:
            dict: Summary of cleaning operations performed
        """
        try:
            # Analyze original file
            orig_structure = self.parser.get_structure("original", original_path)
            orig_chains = ProteinChainDetector.get_protein_chains(orig_structure)
            
            # Analyze cleaned file  
            clean_structure = self.parser.get_structure("cleaned", cleaned_path)
            clean_chains = ProteinChainDetector.get_protein_chains(clean_structure)
            
            summary = {
                "original_file": original_path,
                "cleaned_file": cleaned_path,
                "original_chains": list(orig_chains.keys()),
                "cleaned_chains": list(clean_chains.keys()),
                "original_total_residues": sum(info["total_residues"] for info in orig_chains.values()),
                "cleaned_total_residues": sum(info["amino_acid_count"] for info in clean_chains.values()),
                "chains_removed": len(orig_chains) - len(clean_chains),
                "cleaning_applied": True
            }
            
            logger.info(f"Cleaning summary: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate cleaning summary: {e}")
            return {
                "original_file": original_path,
                "cleaned_file": cleaned_path,
                "error": str(e)
            }