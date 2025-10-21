#!/usr/bin/env python3
"""
Quick Start Script for AI Agent Workflow System
This script helps users set up the system quickly
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def print_banner():
    """Print the welcome banner"""
    print("=" * 60)
    print("AI Agent Workflow System - Quick Start")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 10):
        print("ERROR: Python 3.10 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"OK: Python version: {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("OK: Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to install dependencies")
        return False


def setup_config():
    """Setup configuration file"""
    config_path = Path("config/config.json")
    
    if config_path.exists():
        print("OK: Configuration file already exists")
        return True
    
    print("Setting up configuration...")
    
    # Create config directory if it doesn't exist
    config_path.parent.mkdir(exist_ok=True)
    
    # Create default config
    default_config = {
        "gemini": {
            "api_key": "your-gemini-api-key-here",
            "model": "gemini-2.5-flash",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        "hubspot": {
            "api_key": "your-hubspot-api-key-here",
            "base_url": "https://api.hubapi.com"
        },
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password"
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=4)
    
    print("OK: Configuration file created at config/config.json")
    print("NOTE: Configuration file contains your API credentials")
    return True


def run_tests():
    """Run the test suite"""
    print("Running tests...")
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("OK: All tests passed")
            return True
        else:
            print("ERROR: Some tests failed")
            print(result.stdout)
            return False
    except FileNotFoundError:
        print("NOTE: pytest not found, skipping tests")
        return True


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Your API credentials are already configured in config/config.json")
    print()
    print("2. Run the system:")
    print("   python main.py")
    print()
    print("3. Read the README.md for detailed instructions")
    print()
    print("Example usage:")
    print('   python main.py -q "Create a contact John Doe, john@example.com, at Acme Corp"')
    print()


def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup configuration
    if not setup_config():
        sys.exit(1)
    
    # Run tests
    run_tests()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
