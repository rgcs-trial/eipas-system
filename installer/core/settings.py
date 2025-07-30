"""
EIPAS Settings Configuration
Handles Claude Code settings.json configuration
"""
import json
from pathlib import Path

class SettingsInstaller:
    """Installs Claude Code settings configuration"""
    
    def __init__(self, claude_dir):
        self.claude_dir = Path(claude_dir)
    
    def install(self):
        """Install settings.json with EIPAS configuration"""
        settings = {
            "hooks": {
                "PreToolUse": [{
                    "matcher": "*",
                    "hooks": [{
                        "type": "command",
                        "command": "python .claude/hooks/task-tracker.py"
                    }]
                }],
                "PostToolUse": [{
                    "matcher": "Edit|Write|MultiEdit",
                    "hooks": [{
                        "type": "command", 
                        "command": "python .claude/hooks/progress-logger.py"
                    }]
                }],
                "UserPromptSubmit": [{
                    "matcher": "*",
                    "hooks": [{
                        "type": "command",
                        "command": "python .claude/hooks/requirement-analyzer.py"
                    }]
                }],
                "SubagentStop": [{
                    "matcher": "*", 
                    "hooks": [{
                        "type": "command",
                        "command": "python .claude/hooks/hierarchy-updater.py"
                    }]
                }],
                "Stop": [{
                    "matcher": "*",
                    "hooks": [{
                        "type": "command",
                        "command": "python .claude/hooks/github-integration.py"
                    }]
                }]
            },
            "env": {
                "EIPAS_TASK_DB": ".claude/tasks/memory.db",
                "EIPAS_WORKSPACE": "~/.claude/eipas-system/workspace",
                "EIPAS_GITHUB_AUTO_COMMIT": "true"
            }
        }
        
        settings_file = self.claude_dir / "settings.json"
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print("  ✅ Configured Claude Code settings")