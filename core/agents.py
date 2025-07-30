"""
EIPAS Agent Installation
Installs all specialized agents from template files
"""
from pathlib import Path

class AgentInstaller:
    """Installs all EIPAS agents from template library"""
    
    def __init__(self, claude_dir):
        self.claude_dir = Path(claude_dir)
        self.agents_dir = self.claude_dir / "agents"
        self.installer_dir = Path(__file__).parent.parent
        self.templates_dir = self.installer_dir / "agent-templates"
    
    def install(self):
        """Install all specialized agents from template files"""
        phase_dirs = {
            "phase1": "CXO evaluation agents",
            "phase2": "business analysis agents", 
            "phase3": "product & architecture agents",
            "phase4": "implementation agents",
            "phase5": "QA specialist agents",
            "meta": "workflow management agents"
        }
        
        total_agents = 0
        phase_counts = {}
        
        for phase_dir, description in phase_dirs.items():
            phase_path = self.templates_dir / phase_dir
            if not phase_path.exists():
                print(f"    ⚠️  {phase_dir} templates not found, skipping...")
                continue
            
            # Install all .md files from this phase
            count = 0
            for template_file in phase_path.glob("*.md"):
                with open(template_file, 'r') as f:
                    content = f.read()
                
                # Copy to agents directory
                agent_file = self.agents_dir / template_file.name
                with open(agent_file, 'w') as f:
                    f.write(content)
                
                count += 1
            
            if count > 0:
                phase_counts[description] = count
                total_agents += count
        
        print(f"  ✅ Installed {total_agents} specialized agents from template library")
        for description, count in phase_counts.items():
            print(f"    • {count} {description}")
        
        if total_agents == 0:
            print(f"    ⚠️  No agent templates found in {self.templates_dir}")
            print(f"    📁 Create .md files in agent-templates/ subdirectories")