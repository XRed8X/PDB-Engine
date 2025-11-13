"""
Utility module for PDB filtering and cleaning operations.
Contains reusable filtering rules for ions, water, hydrogens, ligands, and protein chain selection.
"""

import logging
from typing import Optional, List, Set
from Bio.PDB import Select
from Bio.PDB.Polypeptide import is_aa

logger = logging.getLogger(__name__)


class LimpiadorPDB(Select):
    """
    PDB cleaner class that inherits from Bio.PDB.Select.
    Defines criteria for residues and atoms to keep or remove during PDB cleaning.
    """

    def __init__(self, chains_to_keep: Optional[List[str]] = None):
        """
        Initialize PDB cleaner with optional chain filtering.
        
        Args:
            chains_to_keep: List of chain IDs to maintain (None = all protein chains)
        """
        self.chains_to_keep = chains_to_keep
        self.standard_amino_acids = {
            "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS",
            "ILE", "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP",
            "TYR", "VAL"
        }
        
        # Common water molecules and ions to remove
        self.water_molecules = {"HOH", "WAT", "H2O", "TIP", "SOL"}
        self.common_ions = {
            "NA", "CL", "K", "MG", "CA", "ZN", "FE", "MN", "CU", "NI",
            "SO4", "PO4", "NO3", "CO3", "HCO3", "ACE", "NH4"
        }
        
        # Common ligands and cofactors (may need customization)
        self.common_ligands = {
            "ATP", "ADP", "AMP", "GTP", "GDP", "GMP", "NAD", "NADH", 
            "FAD", "FMN", "COA", "HEM", "HEME", "PLP", "B12", "MG"
        }
        
        logger.info(f"LimpiadorPDB initialized with chains_to_keep: {chains_to_keep}")

    def accept_residue(self, residue) -> bool:
        """
        Determine if a residue should be kept in the cleaned PDB.
        
        Args:
            residue: Bio.PDB residue object
            
        Returns:
            bool: True if residue should be kept, False otherwise
        """
        residue_name = residue.get_resname().strip()
        chain_id = residue.get_parent().id
        
        # Remove water molecules
        if residue_name in self.water_molecules:
            logger.debug(f"Removing water molecule: {residue_name} from chain {chain_id}")
            return False
        
        # Remove common ions
        if residue_name in self.common_ions:
            logger.debug(f"Removing ion: {residue_name} from chain {chain_id}")
            return False
        
        # Remove common ligands (configurable)
        if residue_name in self.common_ligands:
            logger.debug(f"Removing ligand: {residue_name} from chain {chain_id}")
            return False
        
        # Only keep standard amino acids
        if not is_aa(residue, standard=True):
            logger.debug(f"Removing non-standard residue: {residue_name} from chain {chain_id}")
            return False
            
        if residue_name not in self.standard_amino_acids:
            logger.debug(f"Removing non-standard amino acid: {residue_name} from chain {chain_id}")
            return False
        
        # Filter by chains if specified
        if self.chains_to_keep and chain_id not in self.chains_to_keep:
            logger.debug(f"Removing residue from filtered chain: {chain_id}")
            return False
        
        return True

    def accept_atom(self, atom) -> bool:
        """
        Determine if an atom should be kept in the cleaned PDB.
        
        Args:
            atom: Bio.PDB atom object
            
        Returns:
            bool: True if atom should be kept, False otherwise
        """
        # Remove hydrogen atoms
        if atom.element == "H":
            logger.debug(f"Removing hydrogen atom: {atom.get_name()}")
            return False
        
        # Could add more atom-level filtering here if needed
        # For example: remove atoms with low occupancy, high B-factors, etc.
        
        return True

    def get_filtering_summary(self) -> dict:
        """
        Get a summary of filtering criteria applied.
        
        Returns:
            dict: Summary of what will be filtered
        """
        return {
            "chains_to_keep": self.chains_to_keep,
            "removes_water": True,
            "removes_ions": True,
            "removes_ligands": True,
            "removes_hydrogens": True,
            "keeps_only_standard_aa": True,
            "water_molecules": list(self.water_molecules),
            "common_ions": list(self.common_ions),
            "common_ligands": list(self.common_ligands)
        }


class ProteinChainDetector:
    """
    Utility class for detecting and analyzing protein chains in PDB structures.
    """
    
    @staticmethod
    def get_protein_chains(structure) -> dict:
        """
        Analyze structure and return information about protein chains.
        
        Args:
            structure: Bio.PDB structure object
            
        Returns:
            dict: Chain analysis with counts and statistics
        """
        chain_info = {}
        
        for model in structure:
            for chain in model:
                chain_id = chain.id
                aa_count = 0
                total_residues = 0
                
                for residue in chain:
                    total_residues += 1
                    if is_aa(residue, standard=True):
                        aa_count += 1
                
                if aa_count > 0:  # Only include chains with amino acids
                    chain_info[chain_id] = {
                        "amino_acid_count": aa_count,
                        "total_residues": total_residues,
                        "non_protein_residues": total_residues - aa_count,
                        "is_protein_chain": aa_count >= 10  # Minimum 10 AA for protein chain
                    }
        
        logger.info(f"Detected protein chains: {list(chain_info.keys())}")
        return chain_info

    @staticmethod
    def get_longest_chain(chain_info: dict) -> Optional[str]:
        """
        Get the chain ID with the most amino acids.
        
        Args:
            chain_info: Chain information dictionary
            
        Returns:
            str: Chain ID of longest chain, or None if no chains found
        """
        if not chain_info:
            return None
            
        longest_chain = max(
            chain_info.keys(), 
            key=lambda x: chain_info[x]["amino_acid_count"]
        )
        
        logger.info(f"Longest protein chain: {longest_chain}")
        return longest_chain

    @staticmethod
    def get_protein_chains_only(chain_info: dict) -> List[str]:
        """
        Get list of chain IDs that are considered protein chains.
        
        Args:
            chain_info: Chain information dictionary
            
        Returns:
            List[str]: List of protein chain IDs
        """
        protein_chains = [
            chain_id for chain_id, info in chain_info.items() 
            if info["is_protein_chain"]
        ]
        
        logger.info(f"Protein chains identified: {protein_chains}")
        return protein_chains