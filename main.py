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
from utils.display import display_banner

def main():
    """Main installer entry point"""
    display_banner()
    
    # Always check for EIPAS_WORKSPACE environment variable
    if not os.getenv('EIPAS_WORKSPACE'):
        print("❌ EIPAS_WORKSPACE environment variable required")
        print("Set it: export EIPAS_WORKSPACE=/path/to/workspaces")
        sys.exit(1)
    
    try:
        # Ask for workspace name
        workspace_name = input("Enter workspace name: ").strip()
        if not workspace_name:
            print("❌ Workspace name required")
            sys.exit(1)
        
        # Initialize installer with workspace name
        installer = EIPASInstaller(workspace_name)
        
        # Run complete installation
        installer.install()
        
    except FileNotFoundError as e:
        print(f"❌ Installation failed - File not found: {str(e)}")
        sys.exit(1)
    except PermissionError as e:
        print(f"❌ Installation failed - Permission denied: {str(e)}")
        sys.exit(1)
    except OSError as e:
        print(f"❌ Installation failed - System error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Installation failed - Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()