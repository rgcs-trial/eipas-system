"""
EIPAS Hook Installation
Installs hook scripts from template files with JSON I/O compliance
"""
import os
from pathlib import Path

class HookInstaller:
    """Installs EIPAS hook scripts from template library"""
    
    def __init__(self, eipas_dir):
        self.eipas_dir = Path(eipas_dir)
        self.hooks_dir = self.eipas_dir / "hooks"
        self.installer_dir = Path(__file__).parent.parent
        self.templates_dir = self.installer_dir / "hook-templates"
    
    def install(self):
        """Install all hook scripts from template files"""
        self.hooks_dir.mkdir(exist_ok=True)
        
        total_hooks = 0
        
        # Install all .py files from hook templates
        for template_file in self.templates_dir.glob("*.py"):
            with open(template_file, 'r') as f:
                content = f.read()
            
            # Copy to hooks directory
            hook_file = self.hooks_dir / template_file.name
            with open(hook_file, 'w') as f:
                f.write(content)
            os.chmod(hook_file, 0o755)  # Make executable
            
            total_hooks += 1
            print(f"  ✅ Installed {template_file.name} hook")
        
        if total_hooks == 0:
            print(f"    ⚠️  No hook templates found in {self.templates_dir}")
            print(f"    📁 Create .py files in hook-templates/ directory")
        else:
            print(f"  ✅ Installed {total_hooks} hook scripts with JSON I/O compliance")
