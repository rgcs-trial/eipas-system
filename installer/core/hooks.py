"""
EIPAS Hook Installation
Installs hook scripts from template files with JSON I/O compliance
"""
import os
from pathlib import Path

class HookInstaller:
    """Installs EIPAS hook scripts from template library"""
    
    def __init__(self, claude_dir):
        self.claude_dir = Path(claude_dir)
        self.hooks_dir = self.claude_dir / "hooks"
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
    
    def _get_task_tracker(self):
        return '''#!/usr/bin/env python3
"""
EIPAS Task Tracker Hook - PreToolUse
Tracks all tool executions and updates task context
Compliant with Claude Code JSON I/O specifications
"""
import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

def main():
    try:
        # Read hook input via stdin (per Claude Code spec)
        hook_data = json.load(sys.stdin)
        
        # Extract tool information
        tool_name = hook_data.get('tool', {}).get('name', 'unknown')
        tool_params = json.dumps(hook_data.get('tool', {}).get('parameters', {}))
        session_id = hook_data.get('session_id', 'default')
        cwd = hook_data.get('cwd', '')
        
        # Initialize database connection
        db_path = Path('.claude/tasks/memory.db')
        if not db_path.exists():
            return
            
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT INTO tool_activity 
                (session_id, tool_name, tool_params, timestamp, cwd, task_context)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, tool_name, tool_params, datetime.now().isoformat(), cwd, ''))
        
        sys.exit(0)
        
    except Exception as e:
        # Silent failure per Claude Code hook specifications
        sys.exit(0)

if __name__ == "__main__":
    main()
'''
    
    def _get_progress_logger(self):
        return '''#!/usr/bin/env python3
"""
EIPAS Progress Logger Hook - PostToolUse
Logs progress for file modification tools
Compliant with Claude Code JSON I/O specifications
"""
import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

def main():
    try:
        # Read hook input via stdin (per Claude Code spec)
        hook_data = json.load(sys.stdin)
        
        # Extract progress information
        tool_name = hook_data.get('tool', {}).get('name', 'unknown')
        session_id = hook_data.get('session_id', 'default')
        
        # Only process file modification tools
        if tool_name not in ['Edit', 'Write', 'MultiEdit']:
            sys.exit(0)
        
        # Update task progress
        db_path = Path('.claude/tasks/memory.db')
        if not db_path.exists():
            return
            
        with sqlite3.connect(db_path) as conn:
            # Update most recent task progress
            conn.execute("""
                UPDATE tasks SET 
                    updated_at = ?,
                    status = CASE 
                        WHEN status = 'pending' THEN 'in_progress'
                        ELSE status 
                    END
                WHERE session_id = ? AND status != 'completed'
                ORDER BY created_at DESC LIMIT 1
            """, (datetime.now().isoformat(), session_id))
        
        sys.exit(0)
        
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
'''
    
    def _get_requirement_analyzer(self):
        return '''#!/usr/bin/env python3
"""
EIPAS Requirement Analyzer Hook - UserPromptSubmit
Analyzes user requirements and creates tasks
Compliant with Claude Code JSON I/O specifications
"""
import json
import sys
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime

def main():
    try:
        # Read hook input via stdin (per Claude Code spec)
        hook_data = json.load(sys.stdin)
        
        # Extract user prompt
        user_prompt = hook_data.get('prompt', '')
        session_id = hook_data.get('session_id', str(uuid.uuid4()))
        
        # Skip if prompt is empty or too short
        if len(user_prompt.strip()) < 10:
            sys.exit(0)
        
        # Initialize database connection
        db_path = Path('.claude/tasks/memory.db')
        if not db_path.exists():
            return
            
        with sqlite3.connect(db_path) as conn:
            # Create high-level task from user requirement
            task_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO tasks 
                (id, title, status, priority, session_id, created_at, updated_at)
                VALUES (?, ?, 'pending', 'high', ?, ?, ?)
            """, (task_id, user_prompt[:100], session_id, 
                  datetime.now().isoformat(), datetime.now().isoformat()))
        
        sys.exit(0)
        
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
'''
    
    def _get_hierarchy_updater(self):
        return '''#!/usr/bin/env python3
"""
EIPAS Hierarchy Updater Hook - SubagentStop  
Updates task hierarchy when subagents complete
Compliant with Claude Code JSON I/O specifications
"""
import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

def main():
    try:
        # Read hook input via stdin (per Claude Code spec)
        hook_data = json.load(sys.stdin)
        
        # Extract agent information
        agent_name = hook_data.get('agent_name', 'unknown')
        session_id = hook_data.get('session_id', 'default')
        
        # Initialize database connection
        db_path = Path('.claude/tasks/memory.db')
        if not db_path.exists():
            return
            
        with sqlite3.connect(db_path) as conn:
            # Update agent completion status
            conn.execute("""
                UPDATE tasks SET 
                    status = 'completed',
                    updated_at = ?
                WHERE session_id = ? AND title LIKE ?
            """, (datetime.now().isoformat(), session_id, f'%{agent_name}%'))
        
        sys.exit(0)
        
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
'''
    
    def _get_github_integration(self):
        return '''#!/usr/bin/env python3
"""
EIPAS GitHub Integration Hook - Stop
Handles GitHub commits and repository integration
Compliant with Claude Code JSON I/O specifications
"""
import json
import sys
import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime
import os

def main():
    try:
        # Read hook input via stdin (per Claude Code spec)
        hook_data = json.load(sys.stdin)
        
        # Extract session information
        session_id = hook_data.get('session_id', 'unknown')
        
        # Only proceed if GitHub integration is enabled
        if os.getenv('EIPAS_GITHUB_AUTO_COMMIT') != 'true':
            sys.exit(0)
        
        # Check if there are uncommitted changes
        if has_uncommitted_changes():
            create_auto_commit(session_id)
        
        sys.exit(0)
        
    except Exception:
        sys.exit(0)

def has_uncommitted_changes():
    """Check if there are uncommitted changes in the repository"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        return result.returncode == 0 and result.stdout.strip() != ''
    except:
        return False

def create_auto_commit(session_id):
    """Create an automatic commit for the session"""
    try:
        # Get session info from database
        db_path = Path('.claude/tasks/memory.db')
        if db_path.exists():
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT idea FROM workflow_sessions WHERE id = ? LIMIT 1
                """, (session_id,))
                result = cursor.fetchone()
                idea = result[0] if result else "EIPAS workflow progress"
        else:
            idea = "EIPAS workflow progress"
        
        # Create commit
        subprocess.run(['git', 'add', '.'], check=True)
        commit_message = f"EIPAS: {idea[:50]}... - Automated progress commit"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
    except subprocess.CalledProcessError:
        # Silent failure for git operations
        pass

if __name__ == "__main__":
    main()
'''