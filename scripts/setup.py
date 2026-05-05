#!/usr/bin/env python3
"""
Setup script for Krishi Saarthi development environment.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, desc):
    """Run a command and print status."""
    print(f"🔧 {desc}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {desc} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {desc} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🌾 Krishi Saarthi Development Setup")
    print("=" * 40)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False

    print(f"✅ Python {sys.version.split()[0]} detected")

    # Create virtual environment
    if not run_command("python -m venv venv", "Creating virtual environment"):
        return False

    # Activate venv and install dependencies
    activate_cmd = ".\\venv\\Scripts\\activate" if os.name == 'nt' else "source venv/bin/activate"

    pip_commands = [
        f"{activate_cmd} && python -m pip install --upgrade pip",
        f"{activate_cmd} && pip install -r requirements.txt",
    ]

    for cmd in pip_commands:
        if not run_command(cmd, "Installing Python dependencies"):
            return False

    # Setup frontend
    os.chdir("frontend")
    if not run_command("npm install", "Installing frontend dependencies"):
        return False
    os.chdir("..")

    print("\n🎉 Setup completed successfully!")
    print("\nTo start development:")
    print("1. Backend: .\\venv\\Scripts\\activate && python main.py")
    print("2. Frontend: cd frontend && npm run dev")
    print("\nMake sure Ollama is running with 'phi3:latest' model")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)