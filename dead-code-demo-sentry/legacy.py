"""
Legacy module containing old code paths.

Some of these functions are still in use, others may be dead code.
This module is a candidate for tombstone analysis.
"""

from datetime import datetime
from typing import Any
import hashlib


# ============================================
# ACTIVELY USED FUNCTIONS
# ============================================

def validate_data(data: dict) -> bool:
    """Validate that data has required fields."""
    required = ["id", "name"]
    return all(field in data for field in required)


def generate_report(users: list[dict]) -> dict:
    """Generate a simple report from user data."""
    return {
        "title": "User Report",
        "count": len(users),
        "generated_at": datetime.now().isoformat(),
    }


# ============================================
# LEGACY FUNCTIONS - Candidates for tombstoning
# These may or may not be used in production
# ============================================

def process_user_auth(credentials: dict) -> dict:
    """
    Legacy authentication handler.
    TODO: Remove - replaced by OAuth2 flow in auth_service.py
    """
    username = credentials.get("username", "")
    password = credentials.get("password", "")
    
    # Old MD5-based auth (insecure, deprecated)
    password_hash = hashlib.md5(password.encode()).hexdigest()
    
    return {
        "authenticated": True,
        "user": username,
        "method": "legacy_md5",
    }


def old_export_to_csv(data: list[dict], filename: str) -> bool:
    """
    Old CSV export function.
    Deprecated: Use the new export_service module instead.
    """
    try:
        lines = []
        if data:
            headers = list(data[0].keys())
            lines.append(",".join(headers))
            for row in data:
                values = [str(row.get(h, "")) for h in headers]
                lines.append(",".join(values))
        
        with open(filename, "w") as f:
            f.write("\n".join(lines))
        return True
    except Exception:
        return False


def legacy_format_date(date_str: str) -> str:
    """
    Old date formatting function.
    Note: This was used before we standardized on ISO format.
    """
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%m/%d/%Y")
    except ValueError:
        return date_str


def debug_print_request(request_data: dict) -> None:
    """
    Debug function for printing request data.
    FIXME: Remove before production - only for debugging.
    """
    print("=" * 50)
    print("DEBUG REQUEST DATA:")
    for key, value in request_data.items():
        print(f"  {key}: {value}")
    print("=" * 50)


def calculate_legacy_checksum(data: bytes) -> str:
    """
    Calculate checksum using old algorithm.
    Deprecated: Use SHA256 from crypto_utils instead.
    """
    return hashlib.md5(data).hexdigest()


class LegacyUserSession:
    """
    Old session management class.
    Replaced by Redis-based sessions in session_service.py
    """
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.created_at = datetime.now()
        self.data: dict[str, Any] = {}
    
    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
    
    def get(self, key: str) -> Any:
        return self.data.get(key)
    
    def is_expired(self, max_age_hours: int = 24) -> bool:
        age = datetime.now() - self.created_at
        return age.total_seconds() > max_age_hours * 3600
