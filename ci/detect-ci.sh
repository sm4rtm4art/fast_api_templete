#!/bin/bash
# This script detects which CI platform is being used and exports variables accordingly

# Create CI directory if it doesn't exist
mkdir -p $(dirname "$0")

# Detect CI platform
if [ -n "$GITHUB_ACTIONS" ]; then
    echo "GitHub Actions detected"
    export CI_PLATFORM="github"
    export CI_COMMIT_SHA="$GITHUB_SHA"
    export CI_REPOSITORY="$GITHUB_REPOSITORY"
    export CI_REF_NAME="${GITHUB_REF_NAME:-${GITHUB_REF#refs/*/}}"
    export CI_CACHE_DIR="/tmp/.uv-cache"
elif [ -n "$GITLAB_CI" ]; then
    echo "GitLab CI detected"
    export CI_PLATFORM="gitlab"
    export CI_COMMIT_SHA="$CI_COMMIT_SHA"
    export CI_REPOSITORY="$CI_PROJECT_PATH"
    export CI_REF_NAME="$CI_COMMIT_REF_NAME"
    export CI_CACHE_DIR="/tmp/.uv-cache"
else
    echo "No CI platform detected, assuming local development"
    export CI_PLATFORM="local"
    export CI_CACHE_DIR="$HOME/.cache/uv"
fi

echo "CI_PLATFORM=$CI_PLATFORM"
echo "CI_COMMIT_SHA=$CI_COMMIT_SHA"
echo "CI_REPOSITORY=$CI_REPOSITORY"
echo "CI_REF_NAME=$CI_REF_NAME"
echo "CI_CACHE_DIR=$CI_CACHE_DIR"

# Set up UV cache environment variable
export UV_CACHE_DIR="$CI_CACHE_DIR"

# Output values to be used in other scripts
echo "CI_PLATFORM=$CI_PLATFORM" > $(dirname "$0")/ci-env.sh
echo "CI_COMMIT_SHA=$CI_COMMIT_SHA" >> $(dirname "$0")/ci-env.sh
echo "CI_REPOSITORY=$CI_REPOSITORY" >> $(dirname "$0")/ci-env.sh
echo "CI_REF_NAME=$CI_REF_NAME" >> $(dirname "$0")/ci-env.sh
echo "UV_CACHE_DIR=$CI_CACHE_DIR" >> $(dirname "$0")/ci-env.sh
