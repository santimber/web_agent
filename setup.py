#!/usr/bin/env python3
"""
Setup script for GAIA benchmark LangGraph project.
Installs dependencies and sets up Playwright browser binaries.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True,
                                check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def main():
    print("Setting up GAIA benchmark LangGraph project...")

    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        sys.exit(1)

    # Install Playwright browser binaries
    if not run_command("playwright install", "Installing Playwright browser binaries"):
        print("Warning: Playwright browser installation failed. You may need to run 'playwright install' manually.")

    print("\n🎉 Setup complete!")
    print("You can now run your LangGraph agent with: python agent.py")


if __name__ == "__main__":
    main()
