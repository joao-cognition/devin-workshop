"""
Code Analyzer - Identifies potentially unused code in a Python codebase.

This module provides static analysis to find functions, classes, and methods
that may be dead code candidates for tombstone insertion.
"""

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class CodeElement:
    """Represents a code element (function, class, method) in the codebase."""
    name: str
    element_type: str  # "function", "class", "method"
    file_path: str
    line_number: int
    docstring: Optional[str] = None
    is_private: bool = False
    is_dunder: bool = False
    references_count: int = 0
    confidence: float = 0.0  # 0-1, how confident we are this is dead code
    reasons: list[str] = field(default_factory=list)


class CodeAnalyzer:
    """
    Analyzes Python code to identify potentially unused code.
    
    Uses heuristics like:
    - Functions with "deprecated", "legacy", "old" in name or docstring
    - Functions with no references in the codebase
    - Functions marked with TODO/FIXME comments about removal
    - Private functions that aren't called internally
    """
    
    DEAD_CODE_KEYWORDS = [
        "deprecated", "legacy", "old", "unused", "obsolete",
        "todo: remove", "fixme: remove", "to be removed",
        "no longer used", "not used", "dead code",
    ]
    
    def __init__(self, root_path: str, exclude_patterns: list[str] = None):
        """
        Initialize the analyzer.
        
        Args:
            root_path: Root directory of the codebase to analyze
            exclude_patterns: List of glob patterns to exclude
        """
        self.root_path = Path(root_path)
        self.exclude_patterns = exclude_patterns or [
            "__pycache__", ".git", ".venv", "venv", "node_modules",
            "*.pyc", "test_*", "*_test.py", "tests/",
        ]
        self.elements: list[CodeElement] = []
        self.references: dict[str, set[str]] = {}  # name -> set of files referencing it
    
    def analyze(self) -> list[CodeElement]:
        """
        Analyze the codebase and return potentially dead code elements.
        
        Returns:
            List of CodeElement objects sorted by confidence (highest first)
        """
        self.elements = []
        self.references = {}
        
        # First pass: collect all code elements
        for py_file in self._get_python_files():
            self._analyze_file(py_file)
        
        # Second pass: find references
        for py_file in self._get_python_files():
            self._find_references(py_file)
        
        # Calculate confidence scores
        for element in self.elements:
            self._calculate_confidence(element)
        
        # Sort by confidence (highest first)
        self.elements.sort(key=lambda e: e.confidence, reverse=True)
        
        return self.elements
    
    def get_dead_code_candidates(self, min_confidence: float = 0.5) -> list[CodeElement]:
        """
        Get elements that are likely dead code.
        
        Args:
            min_confidence: Minimum confidence threshold (0-1)
        
        Returns:
            List of CodeElement objects above the confidence threshold
        """
        if not self.elements:
            self.analyze()
        
        return [e for e in self.elements if e.confidence >= min_confidence]
    
    def _get_python_files(self) -> list[Path]:
        """Get all Python files in the codebase, excluding patterns."""
        files = []
        for py_file in self.root_path.rglob("*.py"):
            rel_path = str(py_file.relative_to(self.root_path))
            
            # Check exclusion patterns
            excluded = False
            for pattern in self.exclude_patterns:
                if pattern in rel_path:
                    excluded = True
                    break
            
            if not excluded:
                files.append(py_file)
        
        return files
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file for code elements."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            
            tree = ast.parse(source)
            rel_path = str(file_path.relative_to(self.root_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    element = self._create_element_from_function(node, rel_path)
                    self.elements.append(element)
                elif isinstance(node, ast.ClassDef):
                    element = self._create_element_from_class(node, rel_path)
                    self.elements.append(element)
                    
                    # Also analyze methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method = self._create_element_from_function(
                                item, rel_path, class_name=node.name
                            )
                            self.elements.append(method)
        
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"Warning: Could not parse {file_path}: {e}")
    
    def _create_element_from_function(
        self, 
        node: ast.FunctionDef, 
        file_path: str,
        class_name: Optional[str] = None,
    ) -> CodeElement:
        """Create a CodeElement from a function AST node."""
        name = f"{class_name}.{node.name}" if class_name else node.name
        element_type = "method" if class_name else "function"
        
        docstring = ast.get_docstring(node)
        is_private = node.name.startswith("_") and not node.name.startswith("__")
        is_dunder = node.name.startswith("__") and node.name.endswith("__")
        
        return CodeElement(
            name=name,
            element_type=element_type,
            file_path=file_path,
            line_number=node.lineno,
            docstring=docstring,
            is_private=is_private,
            is_dunder=is_dunder,
        )
    
    def _create_element_from_class(
        self, 
        node: ast.ClassDef, 
        file_path: str,
    ) -> CodeElement:
        """Create a CodeElement from a class AST node."""
        docstring = ast.get_docstring(node)
        is_private = node.name.startswith("_") and not node.name.startswith("__")
        
        return CodeElement(
            name=node.name,
            element_type="class",
            file_path=file_path,
            line_number=node.lineno,
            docstring=docstring,
            is_private=is_private,
        )
    
    def _find_references(self, file_path: Path) -> None:
        """Find references to known elements in a file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            
            rel_path = str(file_path.relative_to(self.root_path))
            
            for element in self.elements:
                # Simple name matching (could be improved with proper scope analysis)
                base_name = element.name.split(".")[-1]
                if base_name in source:
                    if element.name not in self.references:
                        self.references[element.name] = set()
                    self.references[element.name].add(rel_path)
        
        except (UnicodeDecodeError,) as e:
            print(f"Warning: Could not read {file_path}: {e}")
    
    def _calculate_confidence(self, element: CodeElement) -> None:
        """Calculate the confidence score that an element is dead code."""
        score = 0.0
        reasons = []
        
        # Skip dunder methods (usually framework hooks)
        if element.is_dunder:
            element.confidence = 0.0
            element.reasons = ["Dunder method - likely framework hook"]
            return
        
        # Check for dead code keywords in name
        name_lower = element.name.lower()
        for keyword in self.DEAD_CODE_KEYWORDS:
            if keyword in name_lower:
                score += 0.3
                reasons.append(f"Name contains '{keyword}'")
                break
        
        # Check for dead code keywords in docstring
        if element.docstring:
            doc_lower = element.docstring.lower()
            for keyword in self.DEAD_CODE_KEYWORDS:
                if keyword in doc_lower:
                    score += 0.4
                    reasons.append(f"Docstring mentions '{keyword}'")
                    break
        
        # Check reference count
        refs = self.references.get(element.name, set())
        element.references_count = len(refs)
        
        if len(refs) == 0:
            score += 0.3
            reasons.append("No references found in codebase")
        elif len(refs) == 1 and element.file_path in refs:
            score += 0.2
            reasons.append("Only referenced in its own file")
        
        # Private functions with no internal references
        if element.is_private and len(refs) <= 1:
            score += 0.2
            reasons.append("Private function with limited references")
        
        # Cap at 1.0
        element.confidence = min(score, 1.0)
        element.reasons = reasons


def analyze_codebase(root_path: str, min_confidence: float = 0.5) -> list[CodeElement]:
    """
    Convenience function to analyze a codebase for dead code.
    
    Args:
        root_path: Root directory of the codebase
        min_confidence: Minimum confidence threshold
    
    Returns:
        List of potential dead code elements
    """
    analyzer = CodeAnalyzer(root_path)
    return analyzer.get_dead_code_candidates(min_confidence)
