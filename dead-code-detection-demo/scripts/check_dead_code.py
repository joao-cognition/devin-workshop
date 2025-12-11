#!/usr/bin/env python3
"""
Script to check Supabase for tombstones that were never triggered.

This identifies confirmed dead code that can be safely removed.

Usage:
    python scripts/check_dead_code.py --project my-project --days 7
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: supabase-py not installed. Install with: pip install supabase")


def get_supabase_client() -> "Client":
    """Get Supabase client from environment variables."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY environment variables required")
        sys.exit(1)
    
    return create_client(url, key)


def check_dead_code(
    client: "Client",
    project_name: str,
    days: int,
) -> list[dict]:
    """
    Find tombstones that have never been triggered.
    
    Returns list of dead code candidates.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all active tombstones registered before the cutoff
    tombstones_response = client.table("tombstones").select("*").eq(
        "project_name", project_name
    ).eq(
        "status", "active"
    ).lt(
        "registered_at", cutoff_date.isoformat()
    ).execute()
    
    tombstones = tombstones_response.data
    
    if not tombstones:
        return []
    
    # Get tombstone IDs that have events
    tombstone_ids = [t["tombstone_id"] for t in tombstones]
    
    events_response = client.table("tombstone_events").select(
        "tombstone_id"
    ).in_(
        "tombstone_id", tombstone_ids
    ).execute()
    
    triggered_ids = set(e["tombstone_id"] for e in events_response.data)
    
    # Filter to only tombstones with no events
    dead_code = [t for t in tombstones if t["tombstone_id"] not in triggered_ids]
    
    return dead_code


def main():
    parser = argparse.ArgumentParser(
        description="Check for confirmed dead code (tombstones never triggered)"
    )
    parser.add_argument(
        "--project",
        type=str,
        required=True,
        help="Project name to check",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Minimum days since tombstone was registered",
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["text", "json", "csv"],
        default="text",
        help="Output format",
    )
    
    args = parser.parse_args()
    
    if not SUPABASE_AVAILABLE:
        print("Error: supabase-py is required. Install with: pip install supabase")
        sys.exit(1)
    
    print(f"Checking for dead code in project: {args.project}")
    print(f"Monitoring period: {args.days} days")
    print()
    
    client = get_supabase_client()
    dead_code = check_dead_code(client, args.project, args.days)
    
    if not dead_code:
        print("No confirmed dead code found!")
        print()
        print("This could mean:")
        print("- All tombstoned code was actually used")
        print("- The monitoring period hasn't passed yet")
        print("- No tombstones have been registered")
        sys.exit(0)
    
    print(f"Found {len(dead_code)} confirmed dead code locations:")
    print()
    
    if args.output == "json":
        import json
        print(json.dumps(dead_code, indent=2, default=str))
    elif args.output == "csv":
        print("tombstone_id,function_name,file_path,line_number,reason,registered_at")
        for item in dead_code:
            print(f"{item['tombstone_id']},{item['function_name']},{item['file_path']},{item['line_number']},{item['reason']},{item['registered_at']}")
    else:
        for i, item in enumerate(dead_code, 1):
            print(f"{i}. {item['function_name']}")
            print(f"   File: {item['file_path']}:{item['line_number']}")
            print(f"   Reason: {item['reason']}")
            print(f"   Registered: {item['registered_at']}")
            print()
    
    print()
    print("Next steps:")
    print("1. Review each function to confirm it's safe to remove")
    print("2. Run remove_dead_code.py to automatically remove the code")
    print("3. Create a PR with the changes")


if __name__ == "__main__":
    main()
