#!/usr/bin/env bash

# Project initialization script for FastAPI Template
# Sets up a new project with UV and proper configuration

# Extract repository information
repo_urlname=$(basename -s .git `git config --get remote.origin.url`)
repo_name=$(basename -s .git `git config --get remote.origin.url` | tr '-' '_' | tr '[:upper:]' '[:lower:]')
repo_owner=$(git config --get remote.origin.url | awk -F ':' '{print $2}' | awk -F '/' '{print $1}')

echo "Initializing project: ${repo_name}"
echo "Owner: ${repo_owner}"

# Run rename if the workflow file exists
if [ -f ".github/workflows/rename_project.yml" ]; then
    echo "Running project renaming..."
    .github/rename_project.sh -a "${repo_owner}" -n "${repo_name}" -u "${repo_urlname}"
fi

# Set up UV virtual environment
echo "Setting up UV environment..."
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev,test,lint]"

echo "✅ Project initialized successfully!"
echo "To activate the environment: source .venv/bin/activate"
