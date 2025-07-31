#!/usr/bin/env python3
"""
EIPAS User Interaction Logger Hook - Comprehensive user decision and approval tracking
Logs all user interactions, decisions, and approval patterns for workflow optimization
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
        
        # Extract user interaction information
        tool_name = hook_data.get('tool', {}).get('name', 'unknown')
        session_id = hook_data.get('session_id', 'default')
        user_prompt = hook_data.get('prompt', '')
        
        # Initialize database connection
        db_path = Path('.claude-agentflow/database/memory.db')
        if not db_path.exists():
            return
            
        with sqlite3.connect(db_path) as conn:
            # Setup user interaction tables
            setup_interaction_tables(conn)
            
            # Analyze user interaction patterns
            interaction_data = analyze_user_interaction(user_prompt, tool_name)
            
            if interaction_data:
                # Log user interaction
                log_user_interaction(conn, session_id, interaction_data)
                
                # Analyze interaction patterns
                analyze_interaction_patterns(conn, session_id, interaction_data)
        
        sys.exit(0)
        
    except Exception:
        # Silent failure per Claude Code hook specifications
        sys.exit(0)

def setup_interaction_tables(conn):
    """Setup database tables for user interaction tracking"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_interactions (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            interaction_type TEXT,
            interaction_data TEXT,
            user_decision TEXT,
            confidence_level REAL,
            response_time_estimate REAL,
            context_data TEXT,
            timestamp DATETIME
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interaction_patterns (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            pattern_type TEXT,
            pattern_data TEXT,
            frequency_count INTEGER,
            last_occurrence DATETIME,
            trend_analysis TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            preference_type TEXT,
            preference_value TEXT,
            confidence_score REAL,
            learned_from TEXT,
            updated_at DATETIME
        )
    """)

def analyze_user_interaction(user_prompt, tool_name):
    """Analyze the user interaction to extract decision and approval patterns"""
    prompt_lower = user_prompt.lower()
    
    # Decision indicators
    decision_patterns = {
        'approval': ['yes', 'y', 'approve', 'proceed', 'continue', 'go ahead', 'ok', 'sure'],
        'rejection': ['no', 'n', 'reject', 'stop', 'cancel', 'abort', 'skip'],
        'modification': ['change', 'modify', 'adjust', 'update', 'revise', 'edit'],
        'clarification': ['what', 'how', 'why', 'explain', 'clarify', 'help', 'more info'],
        'iteration': ['iterate', 'improve', 'refine', 'retry', 'again', 'better']
    }
    
    interaction_data = {
        'tool_context': tool_name,
        'prompt_length': len(user_prompt),
        'interaction_timestamp': datetime.now().isoformat()
    }
    
    # Detect decision type
    for decision_type, patterns in decision_patterns.items():
        if any(pattern in prompt_lower for pattern in patterns):
            interaction_data['decision_type'] = decision_type
            interaction_data['decision_confidence'] = calculate_decision_confidence(prompt_lower, patterns)
            break
    
    # Analyze interaction complexity
    interaction_data['complexity'] = analyze_interaction_complexity(user_prompt)
    
    # Detect EIPAS-specific interactions
    eipas_context = detect_eipas_context(prompt_lower)
    if eipas_context:
        interaction_data.update(eipas_context)
    
    return interaction_data

def calculate_decision_confidence(prompt_lower, matching_patterns):
    """Calculate confidence level for detected decision"""
    matches = sum(1 for pattern in matching_patterns if pattern in prompt_lower)
    total_words = len(prompt_lower.split())
    
    # Higher matches and shorter prompts indicate higher confidence
    confidence = min(1.0, (matches * 10) / max(total_words, 1))
    return round(confidence, 2)

def analyze_interaction_complexity(user_prompt):
    """Analyze the complexity of user interaction"""
    complexity_indicators = {
        'simple': ['yes', 'no', 'ok', 'sure', 'y', 'n'],
        'medium': ['because', 'however', 'but', 'also', 'additionally'],
        'complex': ['furthermore', 'nevertheless', 'consequently', 'specifically', 'alternatively']
    }
    
    prompt_lower = user_prompt.lower()
    word_count = len(user_prompt.split())
    
    if word_count <= 5 and any(word in prompt_lower for word in complexity_indicators['simple']):
        return 'simple'
    elif word_count <= 20 and any(word in prompt_lower for word in complexity_indicators['medium']):
        return 'medium'
    elif word_count > 20 or any(word in prompt_lower for word in complexity_indicators['complex']):
        return 'complex'
    else:
        return 'medium'

def detect_eipas_context(prompt_lower):
    """Detect EIPAS-specific interaction context"""
    eipas_patterns = {
        'workflow_control': ['eipas', '/eipas', 'workflow', 'phase'],
        'agent_interaction': ['ceo', 'cto', 'cfo', 'analyst', 'agent'],
        'quality_feedback': ['score', 'quality', 'threshold', 'rating'],
        'iteration_control': ['iterate', 'improve', 'next iteration', 'cycle']
    }
    
    context = {}
    for context_type, patterns in eipas_patterns.items():
        if any(pattern in prompt_lower for pattern in patterns):
            context['eipas_context'] = context_type
            break
    
    # Detect phase references
    import re
    phase_matches = re.findall(r'phase\s*(\d+)', prompt_lower)
    if phase_matches:
        context['phase_reference'] = f"phase{phase_matches[0]}"
    
    return context

def log_user_interaction(conn, session_id, interaction_data):
    """Log the user interaction to the database"""
    interaction_id = str(uuid.uuid4())
    
    # Extract key fields
    interaction_type = interaction_data.get('decision_type', 'general')
    user_decision = interaction_data.get('decision_type', 'unknown')
    confidence_level = interaction_data.get('decision_confidence', 0.0)
    
    # Estimate response time (would be more accurate with actual timing)
    complexity = interaction_data.get('complexity', 'medium')
    response_time_estimates = {'simple': 2.0, 'medium': 5.0, 'complex': 10.0}
    response_time_estimate = response_time_estimates.get(complexity, 5.0)
    
    context_data = json.dumps({
        'tool_context': interaction_data.get('tool_context'),
        'prompt_length': interaction_data.get('prompt_length'),
        'complexity': complexity,
        'eipas_context': interaction_data.get('eipas_context'),
        'phase_reference': interaction_data.get('phase_reference')
    })
    
    conn.execute("""
        INSERT INTO user_interactions 
        (id, session_id, interaction_type, interaction_data, user_decision, 
         confidence_level, response_time_estimate, context_data, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (interaction_id, session_id, interaction_type, json.dumps(interaction_data),
          user_decision, confidence_level, response_time_estimate, context_data,
          datetime.now().isoformat()))

def analyze_interaction_patterns(conn, session_id, interaction_data):
    """Analyze patterns in user interactions for learning and optimization"""
    decision_type = interaction_data.get('decision_type')
    eipas_context = interaction_data.get('eipas_context')
    
    if decision_type:
        # Update decision pattern frequency
        update_pattern_frequency(conn, session_id, f'decision_{decision_type}')
    
    if eipas_context:
        # Update EIPAS context patterns
        update_pattern_frequency(conn, session_id, f'eipas_{eipas_context}')
    
    # Learn user preferences
    learn_user_preferences(conn, session_id, interaction_data)

def update_pattern_frequency(conn, session_id, pattern_type):
    """Update the frequency count for interaction patterns"""
    # Check if pattern exists
    cursor = conn.execute("""
        SELECT id, frequency_count FROM interaction_patterns 
        WHERE session_id = ? AND pattern_type = ?
    """, (session_id, pattern_type))
    
    result = cursor.fetchone()
    
    if result:
        # Update existing pattern
        pattern_id, current_count = result
        conn.execute("""
            UPDATE interaction_patterns 
            SET frequency_count = ?, last_occurrence = ?
            WHERE id = ?
        """, (current_count + 1, datetime.now().isoformat(), pattern_id))
    else:
        # Create new pattern
        pattern_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO interaction_patterns 
            (id, session_id, pattern_type, pattern_data, frequency_count, last_occurrence)
            VALUES (?, ?, ?, '{}', 1, ?)
        """, (pattern_id, session_id, pattern_type, datetime.now().isoformat()))

def learn_user_preferences(conn, session_id, interaction_data):
    """Learn and update user preferences based on interaction patterns"""
    decision_type = interaction_data.get('decision_type')
    complexity = interaction_data.get('complexity')
    eipas_context = interaction_data.get('eipas_context')
    
    preferences_to_learn = []
    
    # Learn decision preferences
    if decision_type in ['approval', 'rejection']:
        preferences_to_learn.append({
            'type': 'decision_tendency',
            'value': decision_type,
            'confidence': interaction_data.get('decision_confidence', 0.5)
        })
    
    # Learn interaction complexity preferences
    if complexity:
        preferences_to_learn.append({
            'type': 'interaction_complexity_preference',
            'value': complexity,
            'confidence': 0.7
        })
    
    # Learn EIPAS workflow preferences
    if eipas_context:
        preferences_to_learn.append({
            'type': f'eipas_{eipas_context}_preference',
            'value': decision_type or 'neutral',
            'confidence': interaction_data.get('decision_confidence', 0.5)
        })
    
    # Store learned preferences
    for preference in preferences_to_learn:
        preference_id = str(uuid.uuid4())
        conn.execute("""
            INSERT OR REPLACE INTO user_preferences 
            (id, session_id, preference_type, preference_value, confidence_score, learned_from, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (preference_id, session_id, preference['type'], preference['value'],
              preference['confidence'], 'interaction_analysis', datetime.now().isoformat()))

if __name__ == "__main__":
    main()