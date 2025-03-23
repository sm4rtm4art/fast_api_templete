# CI/CD Configuration

This directory contains configuration files for Continuous Integration and Continuous Deployment (CI/CD) pipelines.

## Files

- `gitlab-ci.yml`: Configuration for GitLab CI/CD pipelines. Defines the build, test, and deployment stages.

## Usage

These files are automatically used by the respective CI/CD platforms when code is pushed to the repository. No manual action is required.

## Extending

To add support for additional CI/CD platforms:

1. Add the appropriate configuration file to this directory
2. Document the new file in this README
3. Make sure that any references in the scripts (e.g., in `../scripts/detect_ci.sh`) are updated accordingly

## Best Practices

- Keep CI/CD configurations organized in this directory rather than cluttering the root directory
- Ensure consistency across different CI platforms if multiple are used
- Use variables for reusable values to avoid duplication
- Include appropriate caching strategies to speed up builds
