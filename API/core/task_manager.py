# core/task_manager.py
"""
Simple task management for PDB Engine processing.
"""
import uuid
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    task_id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    result_path: Optional[str] = None
    error_message: Optional[str] = None
    progress: int = 0

class TaskManager:
    """Simple in-memory task manager."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        
    def create_task(self, metadata: dict) -> str:
        """Create a new task."""
        task_id = str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.tasks[task_id] = task
        return task_id
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          result_path: str = None, error_message: str = None):
        """Update task status."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            task.updated_at = datetime.now()
            if result_path:
                task.result_path = result_path
            if error_message:
                task.error_message = error_message
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)

# Global task manager instance
task_manager = TaskManager()