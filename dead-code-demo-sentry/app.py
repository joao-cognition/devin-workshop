"""
Sample Application - Main Entry Point

This is a simple task processor application with some legacy code paths
that we want to identify and clean up using tombstone tracking.
"""

from datetime import datetime
from legacy import process_user_auth, generate_report, validate_data


def main():
    """Main entry point for the application."""
    print("Starting Task Processor...")
    print(f"Time: {datetime.now().isoformat()}")
    
    # Process some sample data
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
    ]
    
    for user in users:
        if validate_data(user):
            print(f"Processing user: {user['name']}")
    
    # Generate a report
    report = generate_report(users)
    print(f"Report generated: {report['title']}")
    
    print("Task processing complete!")


def run_legacy_auth_flow():
    """
    This function demonstrates calling a legacy auth path.
    Run this to trigger a tombstone event in Sentry.
    """
    print("Running legacy auth flow...")
    result = process_user_auth({"username": "test", "password": "test123"})
    print(f"Auth result: {result}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--legacy":
        # Run with --legacy flag to trigger tombstone
        run_legacy_auth_flow()
    else:
        main()
