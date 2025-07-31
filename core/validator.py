"""
EIPAS Installation Validator
Validates complete installation
"""
import os
import json
import sqlite3
from pathlib import Path

class InstallationValidator:
    """Validates EIPAS installation completeness"""
    
    def __init__(self):
        self.claude_dir = Path('.claude')
    
    def validate_all(self):
        """Run all validation checks"""
        checks = [
            ("Settings Configuration", self._check_settings),
            ("Agent Installation", self._check_agents),
            ("Command Installation", self._check_commands),
            ("Hook Installation", self._check_hooks),
            ("Database Initialization", self._check_database),
        ]
        
        print("✅ Validating installation...")
        
        for check_name, check_func in checks:
            try:
                check_func()
                print(f"  ✅ {check_name}")
            except Exception as e:
                print(f"  ❌ {check_name}: {str(e)}")
                raise
    
    def _check_settings(self):
        """Check settings.json exists and has required hooks"""
        settings_file = self.claude_dir / "settings.json"
        if not settings_file.exists():
            raise Exception("settings.json not found")
        
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        required_hooks = ["PreToolUse", "PostToolUse", "UserPromptSubmit", "SubagentStop", "Stop"]
        for hook in required_hooks:
            if hook not in settings.get("hooks", {}):
                raise Exception(f"Hook {hook} not configured")
    
    def _check_agents(self):
        """Check all agents are installed"""
        agents_dir = self.claude_dir / "agents"
        if not agents_dir.exists():
            raise Exception("Agents directory not found")
        
        # Count expected agents: 10 + 4 + 5 + 4 + 4 + 6 = 33 total
        agent_files = list(agents_dir.glob("*.md"))
        if len(agent_files) < 33:
            raise Exception(f"Expected 33+ agents, found {len(agent_files)}")
    
    def _check_commands(self):
        """Check commands are installed"""
        command_file = self.claude_dir / "commands" / "eipas.md"
        if not command_file.exists():
            raise Exception("/eipas command not installed")
    
    def _check_hooks(self):
        """Check hook scripts are installed"""
        required_hooks = [
            "task-tracker.py", "progress-logger.py", "requirement-analyzer.py", 
            "hierarchy-updater.py", "github-integration.py"
        ]
        
        # Check .claude-agentflow hooks directory
        eipas_dir = Path('.claude-agentflow')
        hooks_dir = eipas_dir / "hooks"
        
        for hook in required_hooks:
            hook_file = hooks_dir / hook
            if not hook_file.exists():
                raise Exception(f"Hook script {hook} not found in .claude-agentflow/hooks/")
            
            # Check if hook is executable
            if not os.access(hook_file, os.X_OK):
                raise Exception(f"Hook script {hook} is not executable")
    
    def _check_database(self):
        """Check database is initialized"""
        eipas_dir = Path('.claude-agentflow')
        db_file = eipas_dir / "database" / "memory.db"
        if not db_file.exists():
            raise Exception("SQLite database not initialized in .claude-agentflow/database/")
        
        # Check if essential tables exist
        with sqlite3.connect(db_file) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('tasks', 'workflow_sessions', 'tool_activity')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['tasks', 'workflow_sessions', 'tool_activity']
            for table in required_tables:
                if table not in tables:
                    raise Exception(f"Required table {table} not found in database")