#!/usr/bin/env python3
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
        db_path = Path('.claude-agentflow/database/memory.db')
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