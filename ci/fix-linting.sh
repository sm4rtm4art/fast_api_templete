#!/bin/bash
# Script to automatically fix linting issues in the codebase

# Check if Ruff is installed
if ! command -v ruff &> /dev/null; then
    echo "Ruff is not installed. Installing it now..."
    pip install ruff
fi

echo "Fixing linting issues in the codebase..."

# Fix common issues automatically
echo "Fixing common issues with Ruff..."
ruff check --fix fast_api_template/
ruff format --line-length 120 fast_api_template/

# Check remaining issues
echo "Remaining issues:"
ruff check fast_api_template/

echo "Done fixing linting issues. Please verify the changes and commit them."
