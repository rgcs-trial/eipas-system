"""
EIPAS Settings Configuration
Handles Claude Code settings.json configuration from template files
"""
import json
from pathlib import Path

class SettingsInstaller:
    """Installs Claude Code settings configuration from template library"""
    
    def __init__(self, claude_dir):
        self.claude_dir = Path(claude_dir)
        self.installer_dir = Path(__file__).parent.parent
        self.templates_dir = self.installer_dir / "settings-templates"
    
    def install(self):
        """Install settings.json from template file"""
        settings_template = self.templates_dir / "settings.json"
        
        if not settings_template.exists():
            print(f"    ⚠️  Settings template not found: {settings_template}")
            print(f"    📁 Create settings.json in settings-templates/ directory")
            return
        
        # Read settings from template
        with open(settings_template, 'r') as f:
            settings = json.load(f)
        
        # Write to Claude directory
        settings_file = self.claude_dir / "settings.json"
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print("  ✅ Configured Claude Code settings from template")