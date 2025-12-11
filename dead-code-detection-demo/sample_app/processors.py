"""
Task processors for the sample application.

Contains processing logic with some unused code paths.
"""

from typing import Any, Optional
from datetime import datetime


# ============================================
# ACTIVELY USED FUNCTIONS
# ============================================

def process_task(task: dict) -> dict:
    """Process a single task and return the result."""
    return {
        "id": task["id"],
        "name": task["name"],
        "status": "completed",
        "processed_at": datetime.now().isoformat(),
    }


def batch_process(tasks: list[dict]) -> list[dict]:
    """Process multiple tasks in batch."""
    return [process_task(task) for task in tasks]


# ============================================
# POTENTIALLY UNUSED FUNCTIONS (Dead Code Candidates)
# ============================================

def process_with_priority(task: dict, priority_boost: int = 0) -> dict:
    """
    Process task with priority adjustment.
    Note: Priority system was simplified, this may be unused.
    """
    base_priority = {"high": 3, "medium": 2, "low": 1}.get(
        task.get("priority", "medium"), 2
    )
    
    return {
        **process_task(task),
        "effective_priority": base_priority + priority_boost,
    }


def async_process_task(task: dict, callback: callable = None) -> dict:
    """
    Asynchronously process a task with optional callback.
    Legacy: Was used before we switched to proper async/await.
    """
    result = process_task(task)
    if callback:
        callback(result)
    return result


def validate_task_schema(task: dict) -> tuple[bool, list[str]]:
    """
    Validate task against expected schema.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    
    if "id" not in task:
        errors.append("Missing required field: id")
    if "name" not in task:
        errors.append("Missing required field: name")
    if "priority" in task and task["priority"] not in ["high", "medium", "low"]:
        errors.append(f"Invalid priority: {task['priority']}")
    
    return len(errors) == 0, errors


def transform_legacy_task(legacy_task: dict) -> dict:
    """
    Transform old task format to new format.
    Used during migration, may no longer be needed.
    """
    return {
        "id": legacy_task.get("task_id", legacy_task.get("id")),
        "name": legacy_task.get("task_name", legacy_task.get("name", "Unnamed")),
        "priority": legacy_task.get("prio", "medium").lower(),
        "metadata": {
            "migrated": True,
            "original_format": "legacy_v1",
        },
    }


def calculate_task_metrics(tasks: list[dict]) -> dict:
    """
    Calculate metrics for a list of tasks.
    Was used for dashboard, dashboard now calculates its own metrics.
    """
    total = len(tasks)
    if total == 0:
        return {"total": 0, "by_priority": {}, "completion_rate": 0.0}
    
    by_priority = {}
    completed = 0
    
    for task in tasks:
        priority = task.get("priority", "medium")
        by_priority[priority] = by_priority.get(priority, 0) + 1
        if task.get("status") == "completed":
            completed += 1
    
    return {
        "total": total,
        "by_priority": by_priority,
        "completion_rate": completed / total,
    }


class TaskQueue:
    """
    In-memory task queue implementation.
    Replaced by Redis-based queue, but kept for testing.
    """
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.queue: list[dict] = []
    
    def enqueue(self, task: dict) -> bool:
        if len(self.queue) >= self.max_size:
            return False
        self.queue.append(task)
        return True
    
    def dequeue(self) -> Optional[dict]:
        if not self.queue:
            return None
        return self.queue.pop(0)
    
    def peek(self) -> Optional[dict]:
        if not self.queue:
            return None
        return self.queue[0]
    
    def size(self) -> int:
        return len(self.queue)
    
    def is_empty(self) -> bool:
        return len(self.queue) == 0
    
    def clear(self) -> None:
        self.queue = []


def export_tasks_to_json(tasks: list[dict], filepath: str) -> bool:
    """
    Export tasks to a JSON file.
    Note: File export was moved to a separate service.
    """
    import json
    
    try:
        with open(filepath, "w") as f:
            json.dump(tasks, f, indent=2, default=str)
        return True
    except Exception:
        return False


def import_tasks_from_json(filepath: str) -> list[dict]:
    """
    Import tasks from a JSON file.
    Note: File import was moved to a separate service.
    """
    import json
    
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return []
