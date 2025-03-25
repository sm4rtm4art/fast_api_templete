#!/usr/bin/env python
"""
Script to clean up unused imports in Python files.
Run this on any files that still have unused imports after running fix-linting.sh.
"""

import re
import sys
from pathlib import Path


def remove_unused_imports(file_path: str) -> None:
    """Remove imports marked as unused by Ruff."""
    content = Path(file_path).read_text()

    # Find import lines
    import_pattern = r"from\s+[\w.]+\s+import\s+.*|import\s+.*"
    import_lines = re.findall(import_pattern, content)

    # Check for unused imports (List, Dict, Union, Optional, etc.)
    modified = False
    for old_import in import_lines:
        # Replace deprecated typing imports
        new_import = old_import
        replacements = [
            (r"from\s+typing\s+import\s+(\w+,\s*)*List(,\s*\w+)*", lambda m: m.group(0).replace("List", "list")),
            (r"from\s+typing\s+import\s+(\w+,\s*)*Dict(,\s*\w+)*", lambda m: m.group(0).replace("Dict", "dict")),
            (r"from\s+typing\s+import\s+(\w+,\s*)*Union(,\s*\w+)*", lambda m: m.group(0).replace("Union", "")),
            (r"from\s+typing\s+import\s+(\w+,\s*)*Optional(,\s*\w+)*", lambda m: m.group(0).replace("Optional", "")),
        ]

        for pattern, replacement in replacements:
            new_import = re.sub(pattern, replacement, new_import)

        if new_import != old_import:
            content = content.replace(old_import, new_import)
            modified = True

        # Remove empty imports or imports with just commas
        empty_import_pattern = r"from\s+[\w.]+\s+import\s+,*\s*$|import\s+,*\s*$"
        content = re.sub(empty_import_pattern, "", content)

    if modified:
        Path(file_path).write_text(content)
        print(f"Updated imports in {file_path}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for file_path in sys.argv[1:]:
            remove_unused_imports(file_path)
    else:
        print("Usage: python cleanup_imports.py file1.py file2.py ...")
