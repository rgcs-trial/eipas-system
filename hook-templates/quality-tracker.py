#!/usr/bin/env python3
"""
EIPAS Quality Tracker Hook - Advanced quality score tracking and alerts
Monitors quality gates, thresholds, and provides intelligent quality analysis
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
        
        # Extract quality-related information
        tool_name = hook_data.get('tool', {}).get('name', 'unknown')
        session_id = hook_data.get('session_id', 'default')
        user_prompt = hook_data.get('prompt', '')
        
        # Initialize database connection
        db_path = Path('.claude-agentflow/database/memory.db')
        if not db_path.exists():
            return
            
        with sqlite3.connect(db_path) as conn:
            # Create quality tracking table if not exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_tracking (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    phase TEXT,
                    agent_name TEXT,
                    quality_score REAL,
                    threshold REAL,
                    status TEXT,
                    quality_factors TEXT,
                    timestamp DATETIME
                )
            """)
            
            # Analyze quality context from prompt
            quality_context = analyze_quality_context(user_prompt)
            
            if quality_context:
                # Track quality metrics
                track_quality_metrics(conn, session_id, quality_context, tool_name)
                
                # Check for quality alerts
                check_quality_alerts(conn, session_id, quality_context)
        
        sys.exit(0)
        
    except Exception:
        # Silent failure per Claude Code hook specifications
        sys.exit(0)

def analyze_quality_context(user_prompt):
    """Analyze user prompt for quality-related context"""
    prompt_lower = user_prompt.lower()
    
    quality_indicators = {
        'score': ['score', 'rating', 'quality', 'threshold'],
        'phase': ['phase 1', 'phase 2', 'phase 3', 'phase 4', 'phase 5'],
        'agent': ['ceo', 'cto', 'cfo', 'analyst', 'developer', 'qa'],
        'quality_type': ['technical', 'business', 'market', 'financial', 'operational']
    }
    
    context = {}
    
    # Extract quality scores or ratings
    if any(indicator in prompt_lower for indicator in quality_indicators['score']):
        context['quality_focus'] = True
        
        # Try to extract numeric scores
        import re
        scores = re.findall(r'(\d+(?:\.\d+)?)\s*%?', user_prompt)
        if scores:
            context['scores'] = [float(score) for score in scores]
    
    # Identify phase context
    for phase in quality_indicators['phase']:
        if phase in prompt_lower:
            context['phase'] = phase.replace(' ', '')
            break
    
    # Identify agent context
    for agent in quality_indicators['agent']:
        if agent in prompt_lower:
            context['agent'] = agent
            break
    
    return context if context else None

def track_quality_metrics(conn, session_id, quality_context, tool_name):
    """Track quality metrics and scores"""
    tracking_id = str(uuid.uuid4())
    
    # Extract quality data
    phase = quality_context.get('phase', 'unknown')
    agent_name = quality_context.get('agent', 'unknown')
    scores = quality_context.get('scores', [0])
    quality_score = max(scores) if scores else 0
    
    # Determine threshold based on phase
    phase_thresholds = {
        'phase1': 95.0,
        'phase2': 90.0,
        'phase3': 95.0,
        'phase4': 95.0,
        'phase5': 95.0
    }
    threshold = phase_thresholds.get(phase, 90.0)
    
    # Determine status
    status = 'pass' if quality_score >= threshold else 'fail'
    
    quality_factors = json.dumps({
        'tool_used': tool_name,
        'context_type': 'user_prompt_analysis',
        'quality_focus': quality_context.get('quality_focus', False)
    })
    
    conn.execute("""
        INSERT INTO quality_tracking 
        (id, session_id, phase, agent_name, quality_score, threshold, status, quality_factors, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (tracking_id, session_id, phase, agent_name, quality_score, threshold, status, quality_factors, datetime.now().isoformat()))

def check_quality_alerts(conn, session_id, quality_context):
    """Check for quality alerts and thresholds"""
    scores = quality_context.get('scores', [])
    phase = quality_context.get('phase', 'unknown')
    
    if not scores:
        return
    
    max_score = max(scores)
    phase_thresholds = {
        'phase1': 95.0,
        'phase2': 90.0,
        'phase3': 95.0,
        'phase4': 95.0,
        'phase5': 95.0
    }
    
    threshold = phase_thresholds.get(phase, 90.0)
    
    # Generate alerts for quality issues
    if max_score < threshold:
        alert_type = 'quality_threshold_failed'
        message = f'⚠️ Quality threshold failed: {max_score:.1f}% < {threshold}% in {phase}'
    elif max_score < threshold + 5:  # Warning zone
        alert_type = 'quality_threshold_warning'
        message = f'⚡ Quality threshold warning: {max_score:.1f}% near threshold {threshold}% in {phase}'
    else:
        alert_type = 'quality_threshold_passed'
        message = f'✅ Quality threshold passed: {max_score:.1f}% > {threshold}% in {phase}'
    
    # Store alert
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quality_alerts (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            alert_type TEXT,
            message TEXT,
            phase TEXT,
            score REAL,
            threshold REAL,
            timestamp DATETIME
        )
    """)
    
    alert_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO quality_alerts (id, session_id, alert_type, message, phase, score, threshold, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (alert_id, session_id, alert_type, message, phase, max_score, threshold, datetime.now().isoformat()))

if __name__ == "__main__":
    main()