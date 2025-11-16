"""
Unified configuration system for the PDB Engine API.
Combines Pydantic validation and dotenv loading for fast, safe setup.
"""

from pathlib import Path
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

# Load environment variables manually (ensures compatibility across environments)
load_dotenv()

class Settings(BaseSettings):
    """Global configuration for PDB Engine API"""

    # ====== API Configuration ======
    API_TITLE: str = Field(default="PDB Engine API", description="API title")
    API_DESCRIPTION: str = Field(default="API para ejecutar cálculos de diseño de proteínas usando PDB Engine")
    API_VERSION: str = Field(default="2.0.0", description="API version")

    # ====== Server Configuration ======
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    # ====== PDB Engine Configuration ======
    PDBENGINE_BINARY_PATH: Path = Field(..., description="Path to the PDB Engine binary")
    PDBENGINE_TIMEOUT: int = Field(default=600, description="Timeout for PDB Engine execution (seconds)")

    # ====== Directory Configuration ======
    WORKING_DIR: Path = Field(default=Path("pdbengine_jobs"), description="Working directory for temporary jobs")
    OUTPUT_FOLDER_NAME: Path = Field(default=Path("pdbengine_files"), description="Output folder for result files")

    # ====== File & Task Configuration ======
    MAX_FILE_SIZE: int = Field(default=104857600, description="Maximum file size (bytes)")
    ALLOWED_EXTENSIONS: List[str] = Field(default=[".pdb", ".PDB"], description="Allowed file extensions")
    MAX_CONCURRENT_TASKS: int = Field(default=3, description="Maximum concurrent processing tasks")

    # ====== Debug & Logging ======
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # ====== PDB Preprocessing Configuration ======
    PREPROCESSING_ENABLED: bool = Field(default=True, description="Enable PDB preprocessing/cleaning")
    PREPROCESSING_KEEP_ALL_CHAINS_BY_DEFAULT: bool = Field(default=True, description="Keep all protein chains by default (recommended for protein-protein interfaces)")
    PREPROCESSING_LOG_LEVEL: str = Field(default="INFO", description="Logging level for preprocessing operations")
    PREPROCESSING_REMOVE_WATER: bool = Field(default=True, description="Remove water molecules during cleaning")
    PREPROCESSING_REMOVE_IONS: bool = Field(default=True, description="Remove ions during cleaning")
    PREPROCESSING_REMOVE_LIGANDS: bool = Field(default=True, description="Remove ligands during cleaning")
    PREPROCESSING_REMOVE_HYDROGENS: bool = Field(default=True, description="Remove hydrogen atoms during cleaning")

    # ====== Model Config ======
    model_config = SettingsConfigDict(
        env_file="../../.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ====== Validators ======
    @field_validator("PDBENGINE_BINARY_PATH")
    def validate_binary_path(cls, v: Path):
        if isinstance(v, str):
            v = Path(v)
        if not v.exists() or not v.is_file():
            raise ValueError(f"PDB Engine binary path invalid or missing: {v}")
        return v.resolve()

    @field_validator("WORKING_DIR", "OUTPUT_FOLDER_NAME")
    def validate_directories(cls, v: Path):
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v.resolve()

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    def parse_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",") if ext.strip()]
        return v

    # ====== Helper Properties ======
    @property
    def max_file_size_mb(self) -> float:
        """Return maximum file size in MB"""
        return self.MAX_FILE_SIZE / (1024 * 1024)

    @property
    def base_dirs(self) -> dict:
        """Return a summary of base directories"""
        return {
            "working_dir": str(self.WORKING_DIR),
            "output_dir": str(self.OUTPUT_FOLDER_NAME),
        }

# Global instance
settings = Settings()