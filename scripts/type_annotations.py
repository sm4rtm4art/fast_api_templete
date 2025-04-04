#!/usr/bin/env python
"""
Type Annotations Helper Script

This script helps address mypy errors by adding appropriate return type
annotations to functions in the codebase. It scans Python files for functions
without type annotations and attempts to infer the appropriate return type.

Usage:
    python scripts/type_annotations.py [file_paths...]

Examples:
    # Process all Python files in the fast_api_template directory
    python scripts/type_annotations.py

    # Process specific files
    python scripts/type_annotations.py fast_api_template/app.py \
        fast_api_template/security.py

Notes:
    - This script modifies files in-place, so make sure to back up or
      commit your code before running
    - It's a helper tool - you should review the changes afterward and
      adjust as needed
"""

import os
import re
import sys
from collections.abc import Generator
from pathlib import Path


def add_types_to_file(file_path: str) -> None:
    """Add type annotations to functions in a file."""
    content = Path(file_path).read_text()
    modified = False

    # Pattern for functions without return type annotations
    func_pattern = r"(async\s+)?def\s+([a-zA-Z0-9_]+)\s*\((.*?)\):"

    # Find all function definitions
    matches = re.finditer(func_pattern, content, re.DOTALL)

    for match in matches:
        is_async = match.group(1) is not None
        func_name = match.group(2)
        params = match.group(3)
        full_match = match.group(0)

        # Skip functions that already have type annotations
        if "->" in full_match:
            continue

        # Determine appropriate return type
        return_type = infer_return_type(content, match.span()[1], func_name, file_path)

        # Build new function signature
        if is_async:
            new_sig = f"async def {func_name}({params}) -> {return_type}:"
        else:
            new_sig = f"def {func_name}({params}) -> {return_type}:"

        # Replace the function signature in the content
        content = content.replace(full_match, new_sig)
        modified = True

    if modified:
        Path(file_path).write_text(content)
        print(f"Added type annotations to {file_path}")


def infer_return_type(content: str, func_end: int, func_name: str, file_path: str) -> str:
    """Infer the return type of a function based on its code and context."""

    # Analyze the function body to infer return type
    func_lines = content[func_end:].split("\n")

    # Check for explicit return statements
    return_lines: list[str] = []
    indentation = 0
    in_function = True

    for i, line in enumerate(func_lines):
        if i == 0:  # First line after function definition
            indentation = len(line) - len(line.lstrip())
            continue

        if line.strip() and len(line) - len(line.lstrip()) <= indentation:
            in_function = False  # We've exited the function
            break

        if in_function and "return" in line and not line.strip().startswith("#"):
            return_lines.append(line.strip())

    # FastAPI specific patterns
    if "app.py" in file_path and func_name == "on_startup":
        return "None"

    if any(decorator in file_path for decorator in ["routes/", "app.py"]) and any(
        api_func in func_name for api_func in ["create", "update", "delete", "list", "query", "get", "health_check"]
    ):
        return "dict | list | None"

    # General patterns
    if not return_lines:
        return "None"  # No return statements found

    if any("None" in line or line.strip() == "return" for line in return_lines):
        return "None"

    if any("True" in line or "False" in line for line in return_lines):
        return "bool"

    return "Any"  # Default to Any for unknown return types


def find_python_files(directory: str, exclude: list[str] | None = None) -> Generator[str, None, None]:
    """Find all Python files in the given directory, excluding patterns."""
    exclude = exclude or []
    for root, _, files in os.walk(directory):
        if any(excl in root for excl in exclude):
            continue

        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)


if __name__ == "__main__":
    # Process files provided as arguments, or scan the directory
    if len(sys.argv) > 1:
        for file_path in sys.argv[1:]:
            if file_path.endswith(".py"):
                add_types_to_file(file_path)
    else:
        print("Scanning fast_api_template directory for Python files...")
        for file_path in find_python_files("fast_api_template", exclude=["__pycache__"]):
            add_types_to_file(file_path)

    print("Done. Please review the changes and run mypy to check for remaining issues.")
