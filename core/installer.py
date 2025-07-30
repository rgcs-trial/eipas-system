"""
EIPAS Core Installer
Orchestrates all installation components
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

from .settings import SettingsInstaller
from .agents import AgentInstaller
from .commands import CommandInstaller
from .hooks import HookInstaller
from .database import DatabaseInstaller
from .github import GitHubInstaller

class EIPASInstaller:
    """Main EIPAS installation orchestrator"""
    
    def __init__(self, workspace_mode=False):
        # Support custom workspace location via EIPAS_WORKSPACE
        workspace_env = os.getenv('EIPAS_WORKSPACE')
        if workspace_env and workspace_mode:
            self.project_root = Path(workspace_env).expanduser()
        else:
            self.project_root = Path.cwd()
        
        self.claude_dir = self.project_root / ".claude"
        self.backup_dir = self.project_root / ".claude-backup"
        self.workspace_mode = workspace_mode
        
    def install(self):
        """Execute complete EIPAS installation"""
        if not self.workspace_mode:
            print("🔍 Validating environment...")
            self._validate_environment()
        
        print("💾 Backing up existing configuration...")
        self._backup_existing()
        
        print("🔧 Installing EIPAS core components...")
        self._install_core_components()
        
        if not self.workspace_mode:
            print("⚡ Installing enhanced features...")
            self._install_enhanced_features()
        
        print("✅ EIPAS Installation Complete!")
    
    def _validate_environment(self):
        """Validate installation environment"""
        # Check Claude Code
        try:
            subprocess.run(['claude', '--version'], capture_output=True, check=True)
            print("  ✅ Claude Code found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise Exception("Claude Code not found. Please install first.")
        
        # Check Python
        if not (3, 8) <= sys.version_info[:2]:
            raise Exception("Python 3.8+ required")
        print("  ✅ Python 3.8+ available")
        
        # Check Git
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                          capture_output=True, check=True)
            print("  ✅ Git repository detected")
        except subprocess.CalledProcessError:
            print("  ⚠️  No git repository - will initialize")
        
        # Check write permissions
        if not os.access(self.project_root, os.W_OK):
            raise Exception("No write permissions in project directory")
        print("  ✅ Write permissions confirmed")
    
    def _backup_existing(self):
        """Backup existing Claude configuration"""
        if self.claude_dir.exists():
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            shutil.move(self.claude_dir, self.backup_dir)
            print(f"  ✅ Backed up existing config to {self.backup_dir}")
        else:
            print("  ✅ No existing configuration to backup")
    
    def _install_core_components(self):
        """Install core EIPAS components"""
        # Create directory structure
        self.claude_dir.mkdir(exist_ok=True)
        (self.claude_dir / "agents").mkdir(exist_ok=True)
        (self.claude_dir / "commands").mkdir(exist_ok=True)
        (self.claude_dir / "hooks").mkdir(exist_ok=True)
        (self.claude_dir / "tasks").mkdir(exist_ok=True)
        
        # Create phase directories for workspace mode
        if self.workspace_mode:
            for phase in ['phase1', 'phase2', 'phase3', 'phase4', 'phase5']:
                (self.project_root / phase).mkdir(exist_ok=True)
            print("  ✅ Created workspace with phase directories")
        else:
            print("  ✅ Created directory structure")
        
        # Install components
        SettingsInstaller(self.claude_dir).install()
        AgentInstaller(self.claude_dir).install()
        CommandInstaller(self.claude_dir).install()
        HookInstaller(self.claude_dir).install()
    
    def _install_enhanced_features(self):
        """Install enhanced EIPAS features"""
        DatabaseInstaller(self.claude_dir).install()
        GitHubInstaller(self.project_root).install()