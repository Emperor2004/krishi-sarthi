#!/usr/bin/env python3
"""
Development script for Krishi Saarthi.
Provides common development tasks.
"""
import subprocess
import sys
import os
import argparse
from pathlib import Path

def run_command(cmd, desc, cwd=None):
    """Run a command and print status."""
    print(f"🔧 {desc}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        print(f"✅ {desc} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {desc} failed: {e}")
        return False

def start_backend():
    """Start the FastAPI backend."""
    print("🚀 Starting Krishi Saarthi Backend...")
    os.chdir(".")
    run_command("python main.py", "Starting FastAPI server")

def start_frontend():
    """Start the frontend development server."""
    print("🎨 Starting Krishi Saarthi Frontend...")
    os.chdir("frontend")
    run_command("npm run dev", "Starting Vite dev server")

def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    run_command("python -m pytest tests/ -v", "Running test suite")

def lint_code():
    """Lint the codebase."""
    print("🔍 Linting code...")
    # Add linting commands here when implemented
    print("✅ Linting completed (no linter configured yet)")

def clean_data():
    """Clean all generated data files."""
    print("🧹 Cleaning data files...")
    data_files = [
        "data/users.json",
        "data/sessions.json",
        "data/inventory.json",
        "data/orders.json",
        "data/udhar_ledger.json",
        "data/pending_udhar.json",
    ]

    for file_path in data_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Removed {file_path}")

    print("✅ Data cleanup completed")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Krishi Saarthi Development Tools")
    parser.add_argument("command", choices=[
        "backend", "frontend", "test", "lint", "clean", "setup"
    ], help="Command to run")

    args = parser.parse_args()

    if args.command == "backend":
        start_backend()
    elif args.command == "frontend":
        start_frontend()
    elif args.command == "test":
        run_tests()
    elif args.command == "lint":
        lint_code()
    elif args.command == "clean":
        clean_data()
    elif args.command == "setup":
        run_command("python scripts/setup.py", "Running setup script")

if __name__ == "__main__":
    main()