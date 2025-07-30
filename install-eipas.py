#!/usr/bin/env python3
"""
EIPAS Installation Entry Point
Simplified entry point for the modular installer
"""
import sys
import subprocess
from pathlib import Path

def main():
    """Run the modular EIPAS installer"""
    installer_path = Path(__file__).parent / "installer" / "main.py"
    
    if not installer_path.exists():
        print("❌ Installer modules not found. Please ensure installer/ directory exists.")
        sys.exit(1)
    
    try:
        # Run the modular installer
        result = subprocess.run([sys.executable, str(installer_path)], check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("❌ Installation cancelled by user")
        sys.exit(1)

if __name__ == "__main__":
    main()