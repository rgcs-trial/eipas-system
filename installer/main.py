#!/usr/bin/env python3
"""
EIPAS Modular Installer - Main Entry Point
Ultra-scale Enterprise Idea-to-Product Automation System
"""
import os
import sys
from pathlib import Path

# Add installer modules to path
sys.path.insert(0, str(Path(__file__).parent))

from core.installer import EIPASInstaller
from core.validator import InstallationValidator
from utils.display import display_banner, display_success

def main():
    """Main installer entry point"""
    display_banner()
    
    try:
        # Initialize installer
        installer = EIPASInstaller()
        
        # Run complete installation
        installer.install()
        
        # Validate installation
        validator = InstallationValidator()
        validator.validate_all()
        
        # Display success message
        display_success()
        
    except Exception as e:
        print(f"❌ Installation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()