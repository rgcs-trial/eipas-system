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
    
    def __init__(self, workspace_name):
        # Create workspace inside EIPAS_WORKSPACE directory
        workspace_base = Path(os.getenv('EIPAS_WORKSPACE')).expanduser()
        self.project_root = workspace_base / workspace_name
        
        # Check if workspace already exists
        if self.project_root.exists():
            print(f"❌ Workspace '{workspace_name}' already exists at {self.project_root}")
            sys.exit(1)
        
        # Create workspace directory
        self.project_root.mkdir(parents=True, exist_ok=True)
        
        self.claude_dir = self.project_root / ".claude"
        self.backup_dir = self.project_root / ".claude-backup"
        
    def install(self):
        """Execute complete EIPAS installation"""
        print("💾 Backing up existing configuration...")
        self._backup_existing()
        
        print("🔧 Installing EIPAS core components...")
        self._install_core_components()
        
        print("⚡ Installing enhanced features...")
        self._install_enhanced_features()
        
        print("✅ EIPAS Installation Complete!")
    
    
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
        # Create Claude Code standard directories
        self.claude_dir.mkdir(exist_ok=True)
        (self.claude_dir / "agents").mkdir(exist_ok=True)
        (self.claude_dir / "commands").mkdir(exist_ok=True)
        
        # Create consolidated EIPAS directory structure
        self.eipas_dir = self.project_root / ".claude-agentflow"
        self.eipas_dir.mkdir(exist_ok=True)
        (self.eipas_dir / "config").mkdir(exist_ok=True)
        (self.eipas_dir / "hooks").mkdir(exist_ok=True)
        (self.eipas_dir / "database").mkdir(exist_ok=True)
        (self.eipas_dir / "workspace").mkdir(exist_ok=True)
        
        # Create single workspace phase structure (eliminates duplication)
        workspace_dir = self.eipas_dir / "workspace"
        for phase in ['phase1', 'phase2', 'phase3', 'phase4', 'phase5']:
            (workspace_dir / phase).mkdir(exist_ok=True)
        print("  ✅ Created consolidated .claude-agentflow structure with single workspace")
        
        # Install components
        SettingsInstaller(self.claude_dir).install()
        AgentInstaller(self.claude_dir).install()
        CommandInstaller(self.claude_dir).install()
        HookInstaller(self.eipas_dir).install()
    
    def _install_enhanced_features(self):
        """Install enhanced EIPAS features"""
        DatabaseInstaller(self.eipas_dir).install()
        GitHubInstaller(self.project_root).install()