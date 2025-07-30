"""
EIPAS Command Installation
Installs Claude Code slash commands from template files
"""
from pathlib import Path

class CommandInstaller:
    """Installs EIPAS slash commands from template library"""
    
    def __init__(self, claude_dir):
        self.claude_dir = Path(claude_dir)
        self.commands_dir = self.claude_dir / "commands"
        self.installer_dir = Path(__file__).parent.parent
        self.templates_dir = self.installer_dir / "command-templates"
    
    def install(self):
        """Install all EIPAS commands from template files"""
        self.commands_dir.mkdir(exist_ok=True)
        
        total_commands = 0
        
        # Install all .md files from command templates
        for template_file in self.templates_dir.glob("*.md"):
            with open(template_file, 'r') as f:
                content = f.read()
            
            # Copy to commands directory
            command_file = self.commands_dir / template_file.name
            with open(command_file, 'w') as f:
                f.write(content)
            
            total_commands += 1
            print(f"  ✅ Installed /{template_file.stem} command")
        
        if total_commands == 0:
            print(f"    ⚠️  No command templates found in {self.templates_dir}")
            print(f"    📁 Create .md files in command-templates/ directory")