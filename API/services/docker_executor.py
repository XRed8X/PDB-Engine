"""
Docker-based executor for PDB Engine using containerized UniDesign.
"""
import subprocess
import time
import logging
from pathlib import Path
from typing import List
from core.settings import settings
from models.models2 import PDBEngineExecutionResult

logger = logging.getLogger(__name__)


class DockerExecutor:
    """Executes PDB Engine commands using Docker container"""

    @staticmethod
    def execute(command: List[str], working_directory: Path) -> PDBEngineExecutionResult:
        """
        Execute PDB Engine command inside Docker container.
        
        Args:
            command: Command arguments (without binary path)
            working_directory: Host working directory to mount
            
        Returns:
            PDBEngineExecutionResult with execution details
        """
        logger.info(f"Executing command in Docker container")
        logger.info(f"Working directory: {working_directory}")
        logger.info(f"Command: {' '.join(command)}")

        start_time = time.time()
        
        try:
            # Build Docker command
            docker_cmd = DockerExecutor._build_docker_command(command, working_directory)
            
            logger.info(f"Docker command: {' '.join(docker_cmd)}")
            
            # Execute Docker command
            process = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=settings.PDBENGINE_TIMEOUT,
                shell=False
            )

            execution_time = time.time() - start_time
            logger.info(f"Execution completed in {execution_time:.2f} seconds")
            logger.info(f"Return code: {process.returncode}")
            logger.info(f"STDOUT: {process.stdout}")
            logger.info(f"STDERR: {process.stderr}")

            return PDBEngineExecutionResult(
                success=process.returncode == 0,
                stdout=process.stdout,
                stderr=process.stderr,
                return_code=process.returncode,
                execution_time=execution_time
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.error(f"Execution timed out after {execution_time:.2f} seconds")
            return PDBEngineExecutionResult(
                success=False,
                stdout="",
                stderr=f"Process exceeded timeout of {settings.PDBENGINE_TIMEOUT} seconds",
                return_code=-1,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Docker execution error: {e}", exc_info=True)
            return PDBEngineExecutionResult(
                success=False,
                stdout="",
                stderr=f"Docker execution error: {str(e)}",
                return_code=-2,
                execution_time=execution_time
            )

    @staticmethod
    def _build_docker_command(command: List[str], working_directory: Path) -> List[str]:
        """
        Build Docker run command with proper volume mounts and arguments.
        
        Args:
            command: PDB Engine command arguments
            working_directory: Host directory to mount
            
        Returns:
            List[str]: Complete Docker command
        """
        # Get absolute path of working directory
        host_workdir = working_directory.absolute()
        container_workdir = settings.DOCKER_CONTAINER_WORKDIR
        
        # Convert Windows paths in command arguments to container paths
        converted_command = DockerExecutor._convert_paths_to_container(
            command, host_workdir, container_workdir
        )
        
        logger.info(f"Host workdir: {host_workdir}")
        logger.info(f"Container workdir: {container_workdir}")
        logger.info(f"Converted command: {converted_command}")
        
        # Build Docker command
        docker_cmd = [
            "docker", "run",
            "--rm",  # Remove container after execution
            "-v", f"{host_workdir}:{container_workdir}",  # Mount working directory
            "-w", container_workdir,  # Set working directory inside container
            settings.DOCKER_IMAGE,  # Docker image name
        ]
        
        # Add converted PDB Engine command arguments
        docker_cmd.extend(converted_command)
        
        return docker_cmd

    @staticmethod
    def _convert_paths_to_container(
        command: List[str], 
        host_workdir: Path, 
        container_workdir: str
    ) -> List[str]:
        """
        Convert Windows paths in command arguments to container paths.
        
        Args:
            command: Original command with potential Windows paths
            host_workdir: Host working directory (absolute path)
            container_workdir: Container working directory path
            
        Returns:
            List[str]: Command with converted paths
        """
        converted = []
        host_workdir_str = str(host_workdir).lower()
        
        for arg in command:
            # Check if argument contains a path that starts with host workdir
            arg_lower = arg.lower()
            
            # Handle arguments with = (like --pdb=C:\path\file.pdb)
            if '=' in arg:
                key, value = arg.split('=', 1)
                value_path = Path(value)
                
                # Check if value is an absolute path within the working directory
                if value_path.is_absolute() and str(value_path).lower().startswith(host_workdir_str):
                    # Convert to relative path within container
                    relative_path = value_path.relative_to(host_workdir)
                    container_path = f"{container_workdir}/{relative_path.as_posix()}"
                    converted.append(f"{key}={container_path}")
                    logger.info(f"Converted path: {value} -> {container_path}")
                else:
                    converted.append(arg)
            else:
                # Handle standalone path arguments
                try:
                    arg_path = Path(arg)
                    if arg_path.is_absolute() and str(arg_path).lower().startswith(host_workdir_str):
                        relative_path = arg_path.relative_to(host_workdir)
                        container_path = f"{container_workdir}/{relative_path.as_posix()}"
                        converted.append(container_path)
                        logger.info(f"Converted path: {arg} -> {container_path}")
                    else:
                        converted.append(arg)
                except (ValueError, OSError):
                    # Not a valid path, keep as-is
                    converted.append(arg)
        
        return converted

    @staticmethod
    def check_docker_available() -> bool:
        """
        Check if Docker is available and the image exists.
        
        Returns:
            bool: True if Docker is available and image exists
        """
        try:
            # Check if Docker is running
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error("Docker is not running")
                return False
            
            # Check if image exists
            result = subprocess.run(
                ["docker", "images", "-q", settings.DOCKER_IMAGE],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if not result.stdout.strip():
                logger.error(f"Docker image '{settings.DOCKER_IMAGE}' not found")
                return False
            
            logger.info(f"Docker available with image '{settings.DOCKER_IMAGE}'")
            return True
            
        except Exception as e:
            logger.error(f"Error checking Docker availability: {e}")
            return False