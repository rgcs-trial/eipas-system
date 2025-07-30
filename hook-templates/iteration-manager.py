#!/usr/bin/env python3
"""
EIPAS Iteration Manager Hook - Manages iterative cycles for phases 4-5
Tracks iteration progress, manages cycle transitions, and coordinates improvement loops
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
        
        # Extract iteration-related information
        tool_name = hook_data.get('tool', {}).get('name', 'unknown')
        session_id = hook_data.get('session_id', 'default')
        user_prompt = hook_data.get('prompt', '')
        
        # Initialize database connection
        db_path = Path('.claude/tasks/memory.db')
        if not db_path.exists():
            return
            
        with sqlite3.connect(db_path) as conn:
            # Create iteration management tables if not exist
            setup_iteration_tables(conn)
            
            # Analyze iteration context
            iteration_context = analyze_iteration_context(user_prompt)
            
            if iteration_context:
                # Manage iteration lifecycle
                manage_iteration_lifecycle(conn, session_id, iteration_context, tool_name)
                
                # Check iteration completion criteria
                check_iteration_completion(conn, session_id, iteration_context)
        
        sys.exit(0)
        
    except Exception:
        # Silent failure per Claude Code hook specifications
        sys.exit(0)

def setup_iteration_tables(conn):
    """Setup database tables for iteration management"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS iteration_cycles (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            phase TEXT,
            iteration_number INTEGER,
            cycle_type TEXT,
            status TEXT,
            quality_score REAL,
            improvement_areas TEXT,
            started_at DATETIME,
            completed_at DATETIME
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS iteration_checkpoints (
            id TEXT PRIMARY KEY,
            cycle_id TEXT,
            checkpoint_type TEXT,
            checkpoint_data TEXT,
            quality_assessment REAL,
            recommendations TEXT,
            timestamp DATETIME,
            FOREIGN KEY (cycle_id) REFERENCES iteration_cycles (id)
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS iteration_decisions (
            id TEXT PRIMARY KEY,
            cycle_id TEXT,
            decision_type TEXT,
            decision_data TEXT,
            user_approval BOOLEAN,
            auto_decision BOOLEAN,
            reasoning TEXT,
            timestamp DATETIME,
            FOREIGN KEY (cycle_id) REFERENCES iteration_cycles (id)
        )
    """)

def analyze_iteration_context(user_prompt):
    """Analyze user prompt for iteration-related context"""
    prompt_lower = user_prompt.lower()
    
    iteration_keywords = {
        'phase_4': ['phase 4', 'implementation', 'develop', 'code', 'build'],
        'phase_5': ['phase 5', 'qa', 'test', 'quality assurance', 'validation'],
        'iteration': ['iteration', 'cycle', 'improve', 'refine', 'iterate'],
        'checkpoint': ['checkpoint', 'review', 'analyze', 'assess'],
        'completion': ['complete', 'finish', 'done', 'advance', 'next']
    }
    
    context = {}
    
    # Identify iterative phases
    if any(keyword in prompt_lower for keyword in iteration_keywords['phase_4']):
        context['phase'] = 'phase4'
        context['iterative'] = True
    elif any(keyword in prompt_lower for keyword in iteration_keywords['phase_5']):
        context['phase'] = 'phase5'
        context['iterative'] = True
    
    # Identify iteration actions
    if any(keyword in prompt_lower for keyword in iteration_keywords['iteration']):
        context['action'] = 'iteration_request'
    elif any(keyword in prompt_lower for keyword in iteration_keywords['checkpoint']):
        context['action'] = 'checkpoint_request'
    elif any(keyword in prompt_lower for keyword in iteration_keywords['completion']):
        context['action'] = 'completion_request'
    
    # Extract iteration numbers if present
    import re
    iteration_matches = re.findall(r'iteration\s*(\d+)', prompt_lower)
    if iteration_matches:
        context['iteration_number'] = int(iteration_matches[0])
    
    return context if context else None

def manage_iteration_lifecycle(conn, session_id, iteration_context, tool_name):
    """Manage the lifecycle of iteration cycles"""
    phase = iteration_context.get('phase')
    action = iteration_context.get('action')
    
    if not phase or not iteration_context.get('iterative'):
        return
    
    # Get current iteration for this phase
    current_iteration = get_current_iteration(conn, session_id, phase)
    
    if action == 'iteration_request':
        # Start new iteration or continue existing
        if not current_iteration:
            create_new_iteration(conn, session_id, phase, iteration_context)
        else:
            update_iteration_progress(conn, current_iteration['id'], tool_name)
    
    elif action == 'checkpoint_request':
        # Create checkpoint for current iteration
        if current_iteration:
            create_iteration_checkpoint(conn, current_iteration['id'], iteration_context, tool_name)
    
    elif action == 'completion_request':
        # Mark iteration as completed
        if current_iteration:
            complete_iteration(conn, current_iteration['id'], iteration_context)

def get_current_iteration(conn, session_id, phase):
    """Get the current active iteration for a phase"""
    cursor = conn.execute("""
        SELECT * FROM iteration_cycles 
        WHERE session_id = ? AND phase = ? AND status = 'active'
        ORDER BY iteration_number DESC LIMIT 1
    """, (session_id, phase))
    
    result = cursor.fetchone()
    if result:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, result))
    return None

def create_new_iteration(conn, session_id, phase, iteration_context):
    """Create a new iteration cycle"""
    # Get next iteration number
    cursor = conn.execute("""
        SELECT MAX(iteration_number) FROM iteration_cycles 
        WHERE session_id = ? AND phase = ?
    """, (session_id, phase))
    
    max_iteration = cursor.fetchone()[0] or 0
    next_iteration = max_iteration + 1
    
    cycle_id = str(uuid.uuid4())
    cycle_type = f'{phase}_iteration'
    
    conn.execute("""
        INSERT INTO iteration_cycles 
        (id, session_id, phase, iteration_number, cycle_type, status, started_at)
        VALUES (?, ?, ?, ?, ?, 'active', ?)
    """, (cycle_id, session_id, phase, next_iteration, cycle_type, datetime.now().isoformat()))

def update_iteration_progress(conn, cycle_id, tool_name):
    """Update progress for an active iteration"""
    progress_data = json.dumps({
        'tool_used': tool_name,
        'progress_update': datetime.now().isoformat()
    })
    
    # Could add more sophisticated progress tracking here
    pass

def create_iteration_checkpoint(conn, cycle_id, iteration_context, tool_name):
    """Create a checkpoint for the current iteration"""
    checkpoint_id = str(uuid.uuid4())
    checkpoint_type = 'quality_review'
    
    checkpoint_data = json.dumps({
        'tool_context': tool_name,
        'checkpoint_trigger': iteration_context.get('action'),
        'analysis_timestamp': datetime.now().isoformat()
    })
    
    conn.execute("""
        INSERT INTO iteration_checkpoints 
        (id, cycle_id, checkpoint_type, checkpoint_data, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (checkpoint_id, cycle_id, checkpoint_type, checkpoint_data, datetime.now().isoformat()))

def complete_iteration(conn, cycle_id, iteration_context):
    """Mark an iteration as completed"""
    conn.execute("""
        UPDATE iteration_cycles 
        SET status = 'completed', completed_at = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), cycle_id))

def check_iteration_completion(conn, session_id, iteration_context):
    """Check if iteration completion criteria are met"""
    phase = iteration_context.get('phase')
    if not phase:
        return
    
    # Get iteration statistics
    cursor = conn.execute("""
        SELECT 
            COUNT(*) as total_iterations,
            AVG(quality_score) as avg_quality,
            MAX(iteration_number) as latest_iteration
        FROM iteration_cycles 
        WHERE session_id = ? AND phase = ? AND status = 'completed'
    """, (session_id, phase))
    
    stats = cursor.fetchone()
    if stats and stats[0] > 0:  # Has completed iterations
        total_iterations, avg_quality, latest_iteration = stats
        
        # Check completion criteria
        max_iterations = {'phase4': 5, 'phase5': 3}.get(phase, 3)
        quality_threshold = 95.0
        
        if total_iterations >= max_iterations or (avg_quality and avg_quality >= quality_threshold):
            # Suggest phase advancement
            create_advancement_suggestion(conn, session_id, phase, stats)

def create_advancement_suggestion(conn, session_id, phase, iteration_stats):
    """Create suggestion for phase advancement"""
    suggestion_id = str(uuid.uuid4())
    
    suggestion_data = json.dumps({
        'session_id': session_id,
        'from_phase': phase,
        'to_phase': f'phase{int(phase[-1]) + 1}' if phase != 'phase5' else 'completed',
        'iteration_stats': {
            'total_iterations': iteration_stats[0],
            'avg_quality': iteration_stats[1],
            'latest_iteration': iteration_stats[2]
        },
        'recommendation': 'advance_to_next_phase'
    })
    
    conn.execute("""
        INSERT OR REPLACE INTO iteration_decisions 
        (id, cycle_id, decision_type, decision_data, auto_decision, reasoning, timestamp)
        VALUES (?, ?, 'phase_advancement', ?, TRUE, 'Iteration completion criteria met', ?)
    """, (suggestion_id, 'system', suggestion_data, datetime.now().isoformat()))

if __name__ == "__main__":
    main()