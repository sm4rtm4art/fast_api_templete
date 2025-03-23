#!/usr/bin/env python
"""
Dependency Security Check

This script scans project dependencies from pyproject.toml for security
vulnerabilities using the safety library.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def ensure_dependencies():
    """Ensure required packages are installed."""
    required_packages = ["tomli", "safety"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"{package} not found. Adding to project...")
            # Add to pyproject.toml AND install in current environment
            subprocess.check_call(["uv", "add", "--optional", "security", package])
            try:
                __import__(package)
            except ImportError:
                print(f"Failed to import {package}. Please install manually.")
                sys.exit(1)


def extract_dependencies_from_pyproject():
    """Extract dependencies from pyproject.toml into a requirements format."""
    import tomli

    try:
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            print("pyproject.toml not found!")
            sys.exit(1)

        with open(pyproject_path, "rb") as f:
            pyproject_data = tomli.load(f)

        # Get main dependencies
        deps = pyproject_data.get("project", {})
        dependencies = deps.get("dependencies", [])

        # Get optional dependencies
        optional_deps = []
        opt_deps_dict = deps.get("optional-dependencies", {})
        for group, group_deps in opt_deps_dict.items():
            optional_deps.extend(group_deps)

        # Combine all dependencies
        all_deps = dependencies + optional_deps

        # Filter out complex dependencies (those with extras)
        simple_deps = []
        for dep in all_deps:
            # Handle dependencies like 'package[extra]>=1.0.0'
            if "[" in dep and "]" in dep:
                package = dep.split("[")[0]
                version = dep.split("]")[-1]
                simple_deps.append(f"{package}{version}")
            else:
                simple_deps.append(dep)

        return simple_deps
    except Exception as e:
        print(f"Error extracting dependencies: {e}")
        sys.exit(1)


def run_safety_check(dependencies):
    """Run safety check on the given dependencies."""
    # Create a temporary requirements file
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as temp:
        for dep in dependencies:
            temp.write(f"{dep}\n")
        temp_path = temp.name

    print(f"Checking {len(dependencies)} dependencies for vulnerabilities...")

    try:
        # Run safety check on the temporary requirements file
        cmd = ["safety", "check", "--file", temp_path, "--json"]

        # Add ignores for common false positives
        ignores = ["62044", "51457"]
        for ignore_id in ignores:
            cmd.extend(["--ignore", ignore_id])

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse and display results
        if result.returncode == 0:
            print("No security vulnerabilities found!")
            return 0
        else:
            try:
                # Try to parse JSON output
                vulnerabilities = json.loads(result.stdout)
                print(f"Found {len(vulnerabilities)} security vulnerabilities:")
                for vuln in vulnerabilities:
                    package = vuln.get("package_name")
                    version = vuln.get("vulnerable_spec")
                    advisory = vuln.get("advisory")
                    print(f"- {package} {version}: {advisory}")
            except json.JSONDecodeError:
                # Fall back to raw output
                print("Security vulnerabilities found:")
                print(result.stdout)
            return 1
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        return 1
    finally:
        # Clean up the temporary file
        Path(temp_path).unlink(missing_ok=True)


def main():
    """Main function to check dependencies."""
    ensure_dependencies()
    dependencies = extract_dependencies_from_pyproject()
    return run_safety_check(dependencies)


if __name__ == "__main__":
    sys.exit(main())
