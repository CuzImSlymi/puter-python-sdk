#!/usr/bin/env python3
"""
Development environment setup script for Puter Python SDK.

This script sets up a complete development environment with all necessary
tools and dependencies for contributing to the project.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")


def check_git():
    """Check if git is available."""
    if not run_command("git --version", check=False):
        print("❌ Git is not installed or not in PATH")
        sys.exit(1)
    print("✅ Git is available")


def setup_virtual_environment():
    """Set up Python virtual environment."""
    venv_path = Path("venv")

    if venv_path.exists():
        print("🔄 Virtual environment already exists")
        response = input("Recreate it? (y/N): ")
        if response.lower() == "y":
            if sys.platform == "win32":
                run_command("rmdir /s /q venv")
            else:
                run_command("rm -rf venv")
        else:
            return

    print("📦 Creating virtual environment...")
    if not run_command(f"{sys.executable} -m venv venv"):
        print("❌ Failed to create virtual environment")
        sys.exit(1)

    print("✅ Virtual environment created")


def activate_venv_command():
    """Get the command to activate virtual environment."""
    if sys.platform == "win32":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"


def install_dependencies():
    """Install development dependencies."""
    print("📦 Installing dependencies...")

    # Determine pip path
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"

    # Upgrade pip first
    run_command(f"{pip_path} install --upgrade pip")

    # Install the package in development mode
    run_command(f"{pip_path} install -e .[dev]")

    # Install additional development tools
    dev_packages = [
        "pytest",
        "pytest-cov",
        "pytest-asyncio",
        "pytest-xdist",
        "black",
        "isort",
        "flake8",
        "mypy",
        "bandit",
        "safety",
        "pre-commit",
        "build",
        "twine",
    ]

    for package in dev_packages:
        if not run_command(f"{pip_path} install {package}", check=False):
            print(f"⚠️  Warning: Failed to install {package}")

    print("✅ Dependencies installed")


def setup_pre_commit():
    """Set up pre-commit hooks."""
    print("🔧 Setting up pre-commit hooks...")

    if sys.platform == "win32":
        pre_commit_path = "venv\\Scripts\\pre-commit"
    else:
        pre_commit_path = "venv/bin/pre-commit"

    if not run_command(f"{pre_commit_path} install", check=False):
        print("⚠️  Warning: Failed to set up pre-commit hooks")
        return

    print("✅ Pre-commit hooks installed")


def setup_git_config():
    """Set up git configuration for the project."""
    print("🔧 Setting up git configuration...")

    # Set up useful git aliases
    aliases = {
        "co": "checkout",
        "br": "branch",
        "ci": "commit",
        "st": "status",
        "unstage": "reset HEAD --",
        "last": "log -1 HEAD",
        "visual": "!gitk",
        "graph": "log --oneline --graph --all",
    }

    for alias, command in aliases.items():
        run_command(f'git config alias.{alias} "{command}"', check=False)

    print("✅ Git aliases configured")


def create_env_file():
    """Create a .env file template."""
    env_file = Path(".env")

    if env_file.exists():
        print("📄 .env file already exists")
        return

    env_template = """# Puter Python SDK Development Environment Variables

# Authentication (for integration tests)
# PUTER_USERNAME=your_username_here
# PUTER_PASSWORD=your_password_here

# Testing
# RUN_INTEGRATION_TESTS=1
# RUN_NETWORK_TESTS=1

# API Configuration (optional overrides)
# PUTER_API_BASE=https://api.puter.com
# PUTER_LOGIN_URL=https://puter.com/login
# PUTER_TIMEOUT=30
# PUTER_MAX_RETRIES=3

# Development
PYTHONPATH=.
"""

    with open(env_file, "w") as f:
        f.write(env_template)

    print("✅ Created .env file template")
    print("📝 Edit .env file to configure your development environment")


def run_initial_tests():
    """Run initial tests to verify setup."""
    print("🧪 Running initial tests...")

    if sys.platform == "win32":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"

    if not run_command(f"{python_path} -m pytest tests/ -v --tb=short", check=False):
        print("⚠️  Some tests failed, but setup is complete")
    else:
        print("✅ All tests passed!")


def main():
    """Main setup function."""
    print("🚀 Setting up Puter Python SDK development environment")
    print("=" * 60)

    # Check prerequisites
    check_python_version()
    check_git()

    # Setup development environment
    setup_virtual_environment()
    install_dependencies()
    setup_pre_commit()
    setup_git_config()
    create_env_file()

    print("\n" + "=" * 60)
    print("✅ Development environment setup complete!")
    print("\n📋 Next steps:")
    print(f"1. Activate virtual environment: {activate_venv_command()}")
    print("2. Edit .env file with your configuration")
    print("3. Run tests: pytest tests/")
    print("4. Start developing!")

    print("\n🔗 Useful commands:")
    print("  pytest tests/                    # Run all tests")
    print("  pytest tests/ -k test_name       # Run specific test")
    print("  black puter/                     # Format code")
    print("  flake8 puter/                    # Lint code")
    print("  pre-commit run --all-files       # Run all pre-commit hooks")
    print("  python scripts/release.py 1.0.0  # Create release")

    # Option to run initial tests
    response = input("\n🧪 Run initial tests now? (y/N): ")
    if response.lower() == "y":
        run_initial_tests()

    print("\n🎉 Happy coding!")


if __name__ == "__main__":
    main()
