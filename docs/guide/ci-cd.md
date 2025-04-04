# CI/CD Setup

Fast API Template supports both GitHub Actions and GitLab CI/CD out of the box.

## Common CI/CD Features

Both CI/CD pipelines provide:

1. **Environment Preparation**: Cleanup and setup of CI environment
2. **Linting & Security Checks**: Code quality and security scanning
3. **Testing**: Automated testing across platforms
4. **Docker Builds**: Building and testing Docker images
5. **Automatic Releases**: Tagged version releases to PyPI and Docker registries

## GitHub Actions Workflow

The GitHub Actions workflow is defined in `.github/workflows/` and includes:

- **main.yml**: For continuous integration on the main branch and PRs
- **release.yml**: For publishing releases when tags are pushed

### GitHub Actions Setup

No additional setup is required beyond:

1. Adding a `PYPI_API_TOKEN` secret for PyPI publishing
2. Enabling GitHub Pages if you want to publish documentation

## GitLab CI/CD Pipeline

The GitLab CI/CD pipeline is defined in `.gitlab-ci.yml` and includes stages for:

- Preparation
- Linting
- Security checks
- Testing
- Building Docker images
- Publishing releases

### GitLab CI/CD Setup

To use the GitLab CI/CD pipeline:

1. Configure a GitLab runner
2. Set up the following CI/CD variables:
   - `CI_REGISTRY_USER`: Docker registry username
   - `CI_REGISTRY_PASSWORD`: Docker registry password
   - `PYPI_API_TOKEN`: PyPI API token for publishing

## CI/CD Troubleshooting

### Common Issues

#### Version Detection Failure

If you see an error like:

```
ValueError: Error getting the version from source `regex`: unable to parse the version from the file
```

Our CI pipelines use several strategies to avoid this issue:

1. **Direct dependencies installation**: Instead of installing the project in development mode, we install all dependencies directly from PyPI, bypassing the need to parse the VERSION file.

2. **Latest UV action**: We use `astral-sh/setup-uv@v5` which provides better compatibility and features compared to earlier versions.

3. **VERSION file handling**: We ensure the VERSION file is properly formatted without trailing newlines.

4. **Helper script**: The `ci/fix-version.sh` script provides a cross-platform way to fix VERSION file issues.

If you're still encountering VERSION file issues locally:

```bash
# Run this locally to fix the VERSION file
./ci/fix-version.sh 0.1.0

# Check that it worked
cat fast_api_template/VERSION | xxd -p
```

#### Cache Issues

If the cache isn't working:

1. Verify that the cache paths are correct
2. Try clearing the cache manually in the CI/CD interface
3. Check that the cache keys are unique for each job

#### Disk Space Issues

GitHub Actions and some GitLab runners have limited disk space. If you encounter "no space left on device" errors:

1. Use the prepare job to clean up space
2. Remove unnecessary large packages
3. Prune Docker resources with `docker system prune -af`

## Cross-Platform Support

The CI/CD detection script in `ci/detect-ci.sh` automatically detects which CI platform is being used and sets appropriate environment variables. This allows you to write scripts that work on both platforms.
