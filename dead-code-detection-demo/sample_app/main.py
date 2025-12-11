"""
Sample Application - Main Entry Point

This application demonstrates a simple task processor with some
intentionally unused code for the dead code detection demo.
"""

from datetime import datetime
from typing import Optional

from sample_app.utils import format_timestamp, validate_input
from sample_app.processors import process_task, batch_process


def main() -> None:
    """Main entry point for the application."""
    print("Starting Task Processor...")
    
    # Process some sample tasks
    tasks = [
        {"id": 1, "name": "Task A", "priority": "high"},
        {"id": 2, "name": "Task B", "priority": "medium"},
        {"id": 3, "name": "Task C", "priority": "low"},
    ]
    
    for task in tasks:
        if validate_input(task):
            result = process_task(task)
            timestamp = format_timestamp(datetime.now())
            print(f"[{timestamp}] Processed: {result}")
    
    print("Task processing complete!")


def run_batch_mode(tasks: list[dict]) -> list[dict]:
    """Run the processor in batch mode."""
    return batch_process(tasks)


if __name__ == "__main__":
    main()
