#!/usr/bin/env python
"""
Fix Imports Script

This script fixes issues with imports in Python files, particularly focusing on
adding proper imports for commonly used types like 'Any'.
"""
import os
import re
from pathlib import Path


def add_any_import(file_path: str) -> None:
    """Add or ensure the typing.Any import is correct in a file."""
    content = Path(file_path).read_text()

    # Check if the file already imports Any correctly
    any_import_pattern = r"from\s+typing\s+import\s+([^;]*?Any[^;]*?)"
    if not re.search(any_import_pattern, content):
        # If no Any import, check if there's a typing import to add to
        typing_import = re.search(r"from\s+typing\s+import\s+(.*?)$", content, re.MULTILINE)
        if typing_import:
            # Add Any to existing typing import
            old_import = typing_import.group(0)
            imports = typing_import.group(1).strip()

            if "," in imports:
                # Already has multiple imports, add Any if not present
                imports_list = [imp.strip() for imp in imports.split(",")]
                if "Any" not in imports_list:
                    imports_list.append("Any")
                    new_imports = ", ".join(imports_list)
                    new_import = f"from typing import {new_imports}"
                    content = content.replace(old_import, new_import)
            else:
                # Single import, add Any
                if imports != "Any":
                    new_import = f"from typing import {imports}, Any"
                    content = content.replace(old_import, new_import)
        else:
            # No typing import, add a new one at the top after existing imports
            import_section_end = 0
            for match in re.finditer(r"^import\s+|^from\s+", content, re.MULTILINE):
                # Find the last import statement
                line_end = content.find("\n", match.start())
                if line_end > import_section_end:
                    import_section_end = line_end

            if import_section_end > 0:
                # Add after the last import
                new_content = (
                    content[: import_section_end + 1] + "from typing import Any\n" + content[import_section_end + 1 :]
                )
                content = new_content
            else:
                # No imports, add at the top
                content = "from typing import Any\n\n" + content

    # Write the modified content back to the file
    Path(file_path).write_text(content)
    print(f"Processed {file_path}")


def find_python_files(directory: str, exclude: list[str] | None = None) -> list[str]:
    """Find all Python files in the given directory, excluding patterns."""
    exclude = exclude or []
    python_files = []

    for root, _, files in os.walk(directory):
        if any(excl in root for excl in exclude):
            continue

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def main() -> None:
    """Run the import fixer on the codebase."""
    print("Finding Python files...")
    files = find_python_files("fast_api_template", exclude=["__pycache__"])

    print(f"Processing {len(files)} files...")
    for file_path in files:
        add_any_import(file_path)

    print("Done!")


if __name__ == "__main__":
    main()
