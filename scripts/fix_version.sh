#!/bin/bash
# Script to ensure the VERSION file is properly formatted

# If no argument is provided, use 0.1.0 as the default version
VERSION=${1:-0.1.0}

# Detect platform and handle Windows differently if needed
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows-specific handling
    echo -n "$VERSION" > fast_api_template/VERSION
else
    # Unix-like systems (Linux, macOS)
    echo -n "$VERSION" > fast_api_template/VERSION
fi

# Verify the file was created correctly
if [ -f fast_api_template/VERSION ]; then
    echo "VERSION file updated successfully:"
    cat fast_api_template/VERSION | xxd -p
else
    echo "ERROR: Failed to create VERSION file"
    exit 1
fi
