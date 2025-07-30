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
    workspace_mode = len(sys.argv) > 1 and sys.argv[1] == '--workspace'
    
    if not workspace_mode:
        display_banner()
    
    try:
        # Initialize installer
        installer = EIPASInstaller(workspace_mode=workspace_mode)
        
        # Run complete installation
        installer.install()
        
        # Validate installation (skip in workspace mode)
        if not workspace_mode:
            validator = InstallationValidator()
            validator.validate_all()
            display_success()
        
    except Exception as e:
        print(f"❌ Installation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()