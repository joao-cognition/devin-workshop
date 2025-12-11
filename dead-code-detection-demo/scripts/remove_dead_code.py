#!/usr/bin/env python3
"""
Script to remove confirmed dead code from the codebase.

This script removes functions/methods that have been confirmed as dead code
(tombstones that were never triggered during the monitoring period).

Usage:
    python scripts/remove_dead_code.py --path ./sample_app --input dead_code.json
"""

import argparse
import ast
import json
import os
import sys
from pathlib import Path
from typing import Optional


class FunctionRemover(ast.NodeTransformer):
    """AST transformer that removes specified functions."""
    
    def __init__(self, functions_to_remove: set[str]):
        self.functions_to_remove = functions_to_remove
        self.removed = []
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Optional[ast.FunctionDef]:
        if node.name in self.functions_to_remove:
            self.removed.append(node.name)
            return None  # Remove the node
        return node
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Optional[ast.AsyncFunctionDef]:
        if node.name in self.functions_to_remove:
            self.removed.append(node.name)
            return None
        return node


def remove_functions_from_file(
    file_path: Path,
    function_names: list[str],
    dry_run: bool = False,
) -> list[str]:
    """
    Remove specified functions from a Python file.
    
    Returns list of functions that were removed.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        
        # Parse the AST
        tree = ast.parse(source)
        
        # Remove functions
        remover = FunctionRemover(set(function_names))
        new_tree = remover.visit(tree)
        
        if not remover.removed:
            return []
        
        if dry_run:
            print(f"  Would remove from {file_path}: {', '.join(remover.removed)}")
            return remover.removed
        
        # Convert back to source code
        # Note: ast.unparse requires Python 3.9+
        try:
            new_source = ast.unparse(new_tree)
        except AttributeError:
            # Fallback for older Python versions
            print(f"  Warning: ast.unparse not available, using line-based removal")
            new_source = remove_functions_by_line(source, file_path, function_names)
        
        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_source)
        
        print(f"  Removed from {file_path}: {', '.join(remover.removed)}")
        return remover.removed
    
    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return []


def remove_functions_by_line(
    source: str,
    file_path: Path,
    function_names: list[str],
) -> str:
    """
    Fallback method to remove functions by finding their line ranges.
    """
    lines = source.split("\n")
    tree = ast.parse(source)
    
    # Find line ranges for functions to remove
    ranges_to_remove = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in function_names:
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                
                # Include decorators
                if node.decorator_list:
                    start_line = node.decorator_list[0].lineno - 1
                
                ranges_to_remove.append((start_line, end_line))
    
    # Sort ranges in reverse order to remove from bottom to top
    ranges_to_remove.sort(reverse=True)
    
    # Remove the lines
    for start, end in ranges_to_remove:
        del lines[start:end]
    
    return "\n".join(lines)


def remove_tombstone_imports(file_path: Path) -> bool:
    """Remove tombstone imports if no more @tombstone decorators exist."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if there are still tombstone decorators
        if "@tombstone" in content:
            return False
        
        # Remove tombstone imports
        lines = content.split("\n")
        new_lines = [
            line for line in lines
            if "from tombstone import" not in line and "import tombstone" not in line
        ]
        
        if len(new_lines) < len(lines):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines))
            return True
        
        return False
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Remove confirmed dead code from the codebase"
    )
    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Path to the codebase",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="JSON file with dead code list (from check_dead_code.py --output json)",
    )
    parser.add_argument(
        "--functions",
        type=str,
        nargs="+",
        help="Specific function names to remove (alternative to --input)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    
    args = parser.parse_args()
    
    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"Error: Path {root_path} does not exist")
        sys.exit(1)
    
    # Get list of functions to remove
    dead_code_items = []
    
    if args.input:
        with open(args.input, "r") as f:
            dead_code_items = json.load(f)
    elif args.functions:
        # Create simple items from function names
        dead_code_items = [{"function_name": fn, "file_path": None} for fn in args.functions]
    else:
        print("Error: Either --input or --functions is required")
        sys.exit(1)
    
    print(f"Removing dead code from: {root_path}")
    print(f"Functions to remove: {len(dead_code_items)}")
    print(f"Dry run: {args.dry_run}")
    print()
    
    # Group by file
    by_file: dict[str, list[str]] = {}
    for item in dead_code_items:
        file_path = item.get("file_path")
        function_name = item["function_name"]
        
        # Handle method names (Class.method -> method)
        if "." in function_name:
            function_name = function_name.split(".")[-1]
        
        if file_path:
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(function_name)
        else:
            # If no file path, we need to search
            for py_file in root_path.rglob("*.py"):
                rel_path = str(py_file.relative_to(root_path))
                if rel_path not in by_file:
                    by_file[rel_path] = []
                by_file[rel_path].append(function_name)
    
    # Remove functions from each file
    total_removed = 0
    for file_path, functions in by_file.items():
        full_path = root_path / file_path
        if full_path.exists():
            removed = remove_functions_from_file(full_path, functions, args.dry_run)
            total_removed += len(removed)
            
            # Clean up tombstone imports if needed
            if removed and not args.dry_run:
                if remove_tombstone_imports(full_path):
                    print(f"  Cleaned up tombstone imports in {file_path}")
    
    print()
    print(f"{'Would remove' if args.dry_run else 'Removed'} {total_removed} functions")
    
    if not args.dry_run and total_removed > 0:
        print()
        print("Next steps:")
        print("1. Review the changes: git diff")
        print("2. Run your tests to ensure nothing broke")
        print("3. Commit and create a PR")


if __name__ == "__main__":
    main()
