#!/usr/bin/env python3
"""
EIPAS Workflow Monitor Hook - Real-time workflow status monitoring
Provides real-time notifications and status updates for workflow progress
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
        
        # Extract workflow information
        tool_name = hook_data.get('tool', {}).get('name', 'unknown')
        session_id = hook_data.get('session_id', 'default')
        user_prompt = hook_data.get('prompt', '')
        
        # Initialize database connection
        db_path = Path('.claude/tasks/memory.db')
        if not db_path.exists():
            return
            
        with sqlite3.connect(db_path) as conn:
            # Create workflow monitoring table if not exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_monitoring (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    event_type TEXT,
                    event_data TEXT,
                    timestamp DATETIME,
                    notification_sent BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Determine event type based on tool and context
            event_type = determine_event_type(tool_name, user_prompt)
            
            if event_type:
                # Log workflow event
                event_id = str(uuid.uuid4())
                event_data = json.dumps({
                    'tool': tool_name,
                    'prompt_length': len(user_prompt),
                    'context': 'workflow_monitoring'
                })
                
                conn.execute("""
                    INSERT INTO workflow_monitoring 
                    (id, session_id, event_type, event_data, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (event_id, session_id, event_type, event_data, datetime.now().isoformat()))
                
                # Generate real-time notification
                generate_notification(conn, session_id, event_type, tool_name)
        
        sys.exit(0)
        
    except Exception:
        # Silent failure per Claude Code hook specifications
        sys.exit(0)

def determine_event_type(tool_name, user_prompt):
    """Determine the type of workflow event based on tool and prompt"""
    prompt_lower = user_prompt.lower()
    
    if 'eipas' in prompt_lower or '/eipas' in prompt_lower:
        return 'workflow_start'
    elif tool_name in ['Edit', 'Write', 'MultiEdit']:
        return 'file_modification'
    elif tool_name == 'Task':
        return 'agent_execution'
    elif 'phase' in prompt_lower:
        return 'phase_transition'
    elif any(word in prompt_lower for word in ['test', 'validate', 'check']):
        return 'quality_check'
    else:
        return 'general_activity'

def generate_notification(conn, session_id, event_type, tool_name):
    """Generate real-time notification for workflow events"""
    notification_messages = {
        'workflow_start': f'🚀 EIPAS workflow started for session {session_id[:8]}...',
        'file_modification': f'📝 File modified using {tool_name}',
        'agent_execution': f'🤖 Agent execution in progress',
        'phase_transition': f'🔄 Phase transition detected',
        'quality_check': f'✅ Quality validation in progress',
        'general_activity': f'⚡ Workflow activity detected'
    }
    
    message = notification_messages.get(event_type, f'📊 Workflow event: {event_type}')
    
    # Store notification (could be enhanced to send to external systems)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            message TEXT,
            event_type TEXT,
            timestamp DATETIME,
            read_status BOOLEAN DEFAULT FALSE
        )
    """)
    
    notification_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO notifications (id, session_id, message, event_type, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (notification_id, session_id, message, event_type, datetime.now().isoformat()))

if __name__ == "__main__":
    main()