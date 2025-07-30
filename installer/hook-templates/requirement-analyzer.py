#!/usr/bin/env python3
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