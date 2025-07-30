#!/usr/bin/env python3
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