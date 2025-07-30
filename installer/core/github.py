"""
EIPAS GitHub Integration Setup
Configures GitHub integration and automatic commits
"""
import subprocess
from pathlib import Path

class GitHubInstaller:
    """Sets up GitHub integration"""
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
    
    def install(self):
        """Setup GitHub integration and automatic commits"""
        print("  Setting up GitHub integration...")
        
        # Check if we're in a git repository
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                          capture_output=True, text=True, check=True)
            print("    ✅ Git repository detected")
        except subprocess.CalledProcessError:
            print("    ⚠️  Not in a git repository - initializing...")
            subprocess.run(['git', 'init'], check=True)
            print("    ✅ Git repository initialized")
        
        # Create .gitignore if it doesn't exist
        gitignore_path = self.project_root / '.gitignore'
        if not gitignore_path.exists():
            gitignore_content = """# EIPAS System
.claude/tasks/memory.db
.claude/tasks/error.log
*.pyc
__pycache__/
.env
.DS_Store
"""
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            print("    ✅ Created .gitignore")
        
        # Set up git user if not configured
        try:
            subprocess.run(['git', 'config', 'user.name'], 
                          capture_output=True, check=True)
        except subprocess.CalledProcessError:
            subprocess.run(['git', 'config', 'user.name', 'EIPAS System'], check=True)
            subprocess.run(['git', 'config', 'user.email', 'eipas@enterprise.local'], check=True)
            print("    ✅ Configured git user")
        
        print("  ✅ GitHub integration ready")