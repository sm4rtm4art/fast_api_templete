# Utility Scripts

This directory contains utility scripts for development, testing, and CI/CD processes.

## Scripts

- `detect_ci.sh`: Detects the current CI environment and sets up appropriate variables. Used by CI/CD pipelines.
- `fix_linting.sh`: Automatically fixes common linting issues across the codebase.
- `fix_version.sh`: Manages and updates version strings consistently across the project.
- `type_annotations.py`: Adds missing type annotations to functions in the codebase to fix common mypy errors.

## Usage

### `detect_ci.sh`

```bash
source scripts/detect_ci.sh
```

Detects if running in a CI environment and sets appropriate environment variables.

### `fix_linting.sh`

```bash
./scripts/fix_linting.sh
```

Automatically fixes common linting issues in the codebase.

### `fix_version.sh`

```bash
./scripts/fix_version.sh <new_version>
```

Updates the version number across the project.

### `type_annotations.py`

```bash
python scripts/type_annotations.py [file_paths...]
```

Adds type annotations to functions in the specified files. If no files are provided, it scans the entire project.

## Development

When adding new scripts:

1. Use a clear, descriptive name with snake_case
2. Add appropriate documentation at the top of the script
3. Update this README with details on the new script
4. Make the script executable with `chmod +x scripts/new_script.sh`
