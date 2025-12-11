#!/usr/bin/env python3
"""
Script to analyze a codebase and insert tombstones into potentially dead code.

This script:
1. Analyzes the codebase to find potential dead code
2. Adds @tombstone decorators to flagged functions
3. Registers the tombstones in Supabase for tracking

Usage:
    python scripts/analyze_and_tombstone.py --path ./sample_app --project my-project
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tombstone.analyzer import CodeAnalyzer, CodeElement


def add_tombstone_decorator(
    file_path: Path,
    element: CodeElement,
    dry_run: bool = False,
) -> bool:
    """
    Add a @tombstone decorator to a function in a file.
    
    Returns True if successful, False otherwise.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Find the line with the function definition
        line_idx = element.line_number - 1
        if line_idx >= len(lines):
            print(f"  Warning: Line {element.line_number} out of range in {file_path}")
            return False
        
        line = lines[line_idx]
        
        # Check if already has a tombstone decorator
        if line_idx > 0 and "@tombstone" in lines[line_idx - 1]:
            print(f"  Skipping {element.name}: already has tombstone decorator")
            return False
        
        # Get the indentation of the function definition
        indent = len(line) - len(line.lstrip())
        indent_str = " " * indent
        
        # Create the decorator line
        reason = element.reasons[0] if element.reasons else "Potentially unused code"
        decorator_line = f'{indent_str}@tombstone(reason="{reason}")\n'
        
        if dry_run:
            print(f"  Would add decorator before line {element.line_number}:")
            print(f"    {decorator_line.strip()}")
            return True
        
        # Insert the decorator
        lines.insert(line_idx, decorator_line)
        
        # Check if we need to add the import
        has_import = any("from tombstone import" in line or "import tombstone" in line for line in lines[:20])
        
        if not has_import:
            # Find the right place to add the import (after other imports)
            import_idx = 0
            for i, line in enumerate(lines[:30]):
                if line.startswith("import ") or line.startswith("from "):
                    import_idx = i + 1
            
            import_line = "from tombstone import tombstone\n"
            lines.insert(import_idx, import_line)
            if import_idx == 0:
                lines.insert(import_idx + 1, "\n")
        
        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        print(f"  Added tombstone decorator to {element.name}")
        return True
    
    except Exception as e:
        print(f"  Error adding decorator to {element.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Analyze codebase and add tombstone decorators to potential dead code"
    )
    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Path to the codebase to analyze",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="default",
        help="Project name for tracking",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.5,
        help="Minimum confidence threshold (0-1)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--max-changes",
        type=int,
        default=10,
        help="Maximum number of functions to tombstone",
    )
    
    args = parser.parse_args()
    
    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"Error: Path {root_path} does not exist")
        sys.exit(1)
    
    print(f"Analyzing codebase at: {root_path}")
    print(f"Project name: {args.project}")
    print(f"Minimum confidence: {args.min_confidence}")
    print(f"Dry run: {args.dry_run}")
    print()
    
    # Analyze the codebase
    analyzer = CodeAnalyzer(str(root_path))
    candidates = analyzer.get_dead_code_candidates(args.min_confidence)
    
    if not candidates:
        print("No dead code candidates found!")
        sys.exit(0)
    
    print(f"Found {len(candidates)} potential dead code candidates:")
    print()
    
    # Show candidates
    for i, element in enumerate(candidates[:args.max_changes], 1):
        print(f"{i}. {element.name}")
        print(f"   File: {element.file_path}:{element.line_number}")
        print(f"   Type: {element.element_type}")
        print(f"   Confidence: {element.confidence:.2f}")
        print(f"   Reasons: {', '.join(element.reasons)}")
        print()
    
    if args.dry_run:
        print("=== DRY RUN - No changes will be made ===")
        print()
    
    # Add tombstone decorators
    changes_made = 0
    for element in candidates[:args.max_changes]:
        # Only tombstone functions and methods, not classes
        if element.element_type in ("function", "method"):
            file_path = root_path / element.file_path
            if add_tombstone_decorator(file_path, element, args.dry_run):
                changes_made += 1
    
    print()
    print(f"{'Would make' if args.dry_run else 'Made'} {changes_made} changes")
    
    if not args.dry_run and changes_made > 0:
        print()
        print("Next steps:")
        print("1. Review the changes: git diff")
        print("2. Run your tests to ensure nothing broke")
        print("3. Deploy and monitor tombstone events in Supabase")
        print("4. After monitoring period, run check_dead_code.py to find confirmed dead code")


if __name__ == "__main__":
    main()
