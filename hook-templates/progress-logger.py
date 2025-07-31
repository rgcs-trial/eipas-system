#!/usr/bin/env python3
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
        db_path = Path('.claude-agentflow/database/memory.db')
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