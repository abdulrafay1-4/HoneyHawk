#!/usr/bin/env python3
"""
HoneyHawk Setup Script
Quick setup for new installations
"""

import os
import shutil
import sys
from pathlib import Path


def setup_honeyhawk():
    """Set up HoneyHawk for first use"""
    print("HoneyHawk Setup")
    print("=" * 30)
    
    project_root = Path(__file__).parent
    
    # Check if config exists
    config_file = project_root / "config" / "config.yaml"
    config_example = project_root / "config" / "config.yaml.example"
    
    if not config_file.exists() and config_example.exists():
        print("Creating configuration file...")
        shutil.copy(config_example, config_file)
        print(f"Created {config_file}")
        print("Edit config/config.yaml to customize settings")
    elif config_file.exists():
        print("Configuration file already exists")
    else:
        print("Configuration template not found!")
        return False
    
    # Create necessary directories
    directories = [
        project_root / "logs",
        project_root / "tokens",
        project_root / "exports"
    ]
    
    print("\nCreating directories...")
    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"Created {directory.name}/")
    
    # Check dependencies
    print("\nChecking dependencies...")
    try:
        import watchdog
        import yaml
        import requests
        print("All dependencies installed")
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\nSetup Complete!")
    print("\nNext steps:")
    print("1. Review and edit config/config.yaml")
    print("2. Run: python main.py generate")
    print("3. Run: python main.py")
    print("\nFor help: python cli.py --help")
    
    return True


def main():
    """Main setup function"""
    if "--check" in sys.argv:
        # Just check if setup is complete
        config_exists = Path("config/config.yaml").exists()
        deps_ok = True
        try:
            import watchdog, yaml, requests
        except ImportError:
            deps_ok = False
        
        if config_exists and deps_ok:
            print("HoneyHawk is ready to use")
            return True
        else:
            print("Setup incomplete")
            return False
    else:
        return setup_honeyhawk()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
