#!/usr/bin/env python3
"""
Release automation script for Puter Python SDK.

This script helps automate the release process including:
- Version validation and updating
- Changelog updates
- Git tagging
- GitHub release creation
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd, shell=True, check=check, capture_output=capture_output, text=True
    )
    if capture_output:
        return result.stdout.strip()
    return result


def get_current_version():
    """Get the current version from __init__.py."""
    init_file = Path("puter") / "__init__.py"
    with open(init_file, "r") as f:
        content = f.read()
    
    match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Could not find version in __init__.py")
    
    return match.group(1)


def update_version(new_version):
    """Update version in all relevant files."""
    files_to_update = [
        ("puter/__init__.py", r'__version__ = ["\']([^"\']+)["\']', f'__version__ = "{new_version}"'),
        ("pyproject.toml", r'version = ["\']([^"\']+)["\']', f'version = "{new_version}"'),
    ]
    
    for file_path, pattern, replacement in files_to_update:
        with open(file_path, "r") as f:
            content = f.read()
        
        if not re.search(pattern, content):
            print(f"Warning: Could not find version pattern in {file_path}")
            continue
        
        updated_content = re.sub(pattern, replacement, content)
        
        with open(file_path, "w") as f:
            f.write(updated_content)
        
        print(f"Updated version in {file_path}")


def validate_version(version):
    """Validate version format (semantic versioning)."""
    pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$"
    if not re.match(pattern, version):
        raise ValueError(f"Invalid version format: {version}")


def update_changelog(version):
    """Update CHANGELOG.md with new version."""
    changelog_path = Path("CHANGELOG.md")
    
    if not changelog_path.exists():
        print("Warning: CHANGELOG.md not found")
        return
    
    with open(changelog_path, "r") as f:
        content = f.read()
    
    # Check if version already exists in changelog
    if f"## [{version}]" in content:
        print(f"Version {version} already exists in CHANGELOG.md")
        return
    
    # Find the first unreleased section or add new entry
    date_str = datetime.now().strftime("%Y-%m-%d")
    new_section = f"## [{version}] - {date_str}\n\n### Added\n- \n\n### Changed\n- \n\n### Fixed\n- \n\n"
    
    # Insert after the first header
    lines = content.split("\n")
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith("## "):
            insert_index = i
            break
    
    lines.insert(insert_index, new_section)
    
    with open(changelog_path, "w") as f:
        f.write("\n".join(lines))
    
    print(f"Added version {version} to CHANGELOG.md")
    print("Please edit CHANGELOG.md to add your changes before continuing!")
    
    # Ask user to edit changelog
    input("Press Enter after you've updated the CHANGELOG.md...")


def check_git_status():
    """Check if git working directory is clean."""
    try:
        result = run_command("git status --porcelain")
        if result:
            print("Git working directory is not clean:")
            print(result)
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
    except subprocess.CalledProcessError:
        print("Warning: Could not check git status")


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    try:
        run_command("python -m pytest tests/ -v", capture_output=False)
        print("✅ All tests passed!")
    except subprocess.CalledProcessError:
        print("❌ Tests failed!")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)


def build_package():
    """Build the package."""
    print("Building package...")
    run_command("python -m build")
    print("✅ Package built successfully!")


def create_git_tag(version):
    """Create git tag for the release."""
    tag_name = f"v{version}"
    
    # Check if tag already exists
    try:
        run_command(f"git rev-parse {tag_name}")
        print(f"Tag {tag_name} already exists")
        response = input("Delete and recreate? (y/N): ")
        if response.lower() == 'y':
            run_command(f"git tag -d {tag_name}")
        else:
            return False
    except subprocess.CalledProcessError:
        pass  # Tag doesn't exist, which is what we want
    
    # Commit version changes
    run_command("git add .")
    try:
        run_command(f'git commit -m "chore: bump version to {version}"')
    except subprocess.CalledProcessError:
        print("No changes to commit")
    
    # Create tag
    run_command(f'git tag -a {tag_name} -m "Release {version}"')
    print(f"✅ Created tag {tag_name}")
    return True


def push_changes(version):
    """Push changes and tags to remote."""
    tag_name = f"v{version}"
    
    print("Pushing changes to remote...")
    run_command("git push origin main")
    run_command(f"git push origin {tag_name}")
    print("✅ Changes pushed to remote!")


def main():
    """Main release function."""
    parser = argparse.ArgumentParser(description="Release automation script")
    parser.add_argument("version", help="New version number (e.g., 1.0.0)")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-build", action="store_true", help="Skip building package")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    args = parser.parse_args()
    
    # Validate version
    try:
        validate_version(args.version)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    print(f"New version: {args.version}")
    
    if current_version == args.version:
        print("New version is the same as current version")
        sys.exit(1)
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        return
    
    # Check git status
    check_git_status()
    
    # Run tests
    if not args.skip_tests:
        run_tests()
    
    # Update version files
    update_version(args.version)
    
    # Update changelog
    update_changelog(args.version)
    
    # Build package
    if not args.skip_build:
        build_package()
    
    # Create git tag
    if create_git_tag(args.version):
        # Push changes
        response = input("Push changes to remote? (y/N): ")
        if response.lower() == 'y':
            push_changes(args.version)
            print(f"🎉 Release {args.version} completed!")
            print("The GitHub Actions workflow will handle PyPI publishing and GitHub release creation.")
        else:
            print("Changes committed and tagged locally. Push manually when ready.")
    
    print("Release process completed!")


if __name__ == "__main__":
    main()