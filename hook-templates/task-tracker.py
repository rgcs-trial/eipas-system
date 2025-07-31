#!/usr/bin/env python3
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
            # Use existing tool_activity table from database schema
            conn.execute("""
                INSERT INTO tool_activity 
                (session_id, tool_name, tool_params, timestamp, cwd, task_context)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, tool_name, tool_params, datetime.now().isoformat(), cwd, ''))
            conn.commit()
        
        sys.exit(0)
        
    except Exception as e:
        # Silent failure per Claude Code hook specifications
        sys.exit(0)

if __name__ == "__main__":
    main()