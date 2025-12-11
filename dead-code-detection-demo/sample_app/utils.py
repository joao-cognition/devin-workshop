"""
Utility functions for the sample application.

Contains both actively used functions and intentionally unused code
for demonstration purposes.
"""

from datetime import datetime
from typing import Any, Optional
import hashlib
import json


# ============================================
# ACTIVELY USED FUNCTIONS
# ============================================

def format_timestamp(dt: datetime) -> str:
    """Format a datetime object as a readable string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def validate_input(data: dict) -> bool:
    """Validate that input data has required fields."""
    required_fields = ["id", "name"]
    return all(field in data for field in required_fields)


def sanitize_string(text: str) -> str:
    """Remove potentially dangerous characters from a string."""
    return text.replace("<", "&lt;").replace(">", "&gt;")


# ============================================
# POTENTIALLY UNUSED FUNCTIONS (Dead Code Candidates)
# ============================================

def legacy_hash_password(password: str) -> str:
    """
    Legacy password hashing function.
    Deprecated: Use modern_hash_password instead.
    """
    return hashlib.md5(password.encode()).hexdigest()


def calculate_checksum(data: bytes) -> str:
    """Calculate MD5 checksum of binary data."""
    return hashlib.md5(data).hexdigest()


def deep_merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Deep merge two dictionaries.
    Note: This was used in the old config system.
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def format_bytes(num_bytes: int) -> str:
    """Format bytes as human-readable string (KB, MB, GB)."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def retry_with_backoff(func: callable, max_retries: int = 3) -> Any:
    """
    Retry a function with exponential backoff.
    Originally used for API calls, may no longer be needed.
    """
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            time.sleep(wait_time)


def parse_legacy_config(config_str: str) -> dict:
    """
    Parse legacy INI-style configuration.
    Deprecated: Config is now in JSON format.
    """
    result = {}
    for line in config_str.strip().split("\n"):
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def generate_report_id() -> str:
    """Generate a unique report ID based on timestamp."""
    import uuid
    return f"RPT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


def convert_to_csv(data: list[dict]) -> str:
    """Convert a list of dictionaries to CSV format."""
    if not data:
        return ""
    
    headers = list(data[0].keys())
    lines = [",".join(headers)]
    
    for row in data:
        values = [str(row.get(h, "")) for h in headers]
        lines.append(",".join(values))
    
    return "\n".join(lines)


class DeprecatedLogger:
    """
    Old logging class that was replaced by the standard logging module.
    Kept for backwards compatibility but should not be used.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logs = []
    
    def log(self, message: str, level: str = "INFO") -> None:
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] [{level}] {self.name}: {message}"
        self.logs.append(entry)
        print(entry)
    
    def get_logs(self) -> list[str]:
        return self.logs.copy()
    
    def clear_logs(self) -> None:
        self.logs = []
