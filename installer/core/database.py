"""
EIPAS Database Installation
Installs comprehensive SQLite database schema
"""
import sqlite3
from pathlib import Path

class DatabaseInstaller:
    """Installs EIPAS database schema"""
    
    def __init__(self, claude_dir):
        self.claude_dir = Path(claude_dir)
        self.tasks_dir = self.claude_dir / "tasks"
        self.db_path = self.tasks_dir / "memory.db"
    
    def install(self):
        """Install comprehensive SQLite database"""
        self.tasks_dir.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Core tables from user specification
            conn.executescript("""
                -- Tasks (from specification)
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    parent_id TEXT,
                    status TEXT CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked')),
                    priority TEXT CHECK (priority IN ('low', 'medium', 'high', 'critical')),
                    eipas_phase TEXT CHECK (eipas_phase IN ('phase1', 'phase2', 'phase3', 'phase4', 'phase5')),
                    implementation_locked BOOLEAN DEFAULT FALSE,
                    session_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                -- Task Dependencies (from specification)
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    task_id TEXT REFERENCES tasks(id),
                    depends_on_id TEXT REFERENCES tasks(id),
                    PRIMARY KEY (task_id, depends_on_id)
                );

                -- Tool Activity Tracking (from specification)
                CREATE TABLE IF NOT EXISTS tool_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    tool_name TEXT,
                    tool_params TEXT,
                    timestamp DATETIME,
                    cwd TEXT,
                    task_context TEXT
                );

                -- Enhanced tables for iterative workflow
                CREATE TABLE IF NOT EXISTS workflow_sessions (
                    id TEXT PRIMARY KEY,
                    idea TEXT NOT NULL,
                    status TEXT CHECK (status IN ('active', 'completed', 'failed', 'paused')),
                    current_phase TEXT CHECK (current_phase IN ('phase1', 'phase2', 'phase3', 'phase4', 'phase5')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS iterations (
                    id INTEGER PRIMARY KEY,
                    task_id TEXT REFERENCES tasks(id),
                    iteration_number INTEGER,
                    phase TEXT CHECK (phase IN ('phase4', 'phase5')),
                    bugs_found INTEGER DEFAULT 0,
                    bugs_fixed INTEGER DEFAULT 0,
                    quality_score REAL,
                    checkpoint_results TEXT,
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME
                );

                CREATE TABLE IF NOT EXISTS checkpoints (
                    id INTEGER PRIMARY KEY,
                    task_id TEXT REFERENCES tasks(id),
                    iteration_id INTEGER REFERENCES iterations(id),
                    checkpoint_type TEXT CHECK (checkpoint_type IN ('code_quality', 'test_coverage', 'bug_detection', 'performance', 'security')),
                    status TEXT CHECK (status IN ('passed', 'failed', 'warning')),
                    score REAL,
                    details TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS github_commits (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT,
                    commit_hash TEXT,
                    commit_message TEXT,
                    files_changed TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS phase_completions (
                    session_id TEXT,
                    phase TEXT,
                    completion_rate REAL,
                    timestamp DATETIME,
                    PRIMARY KEY (session_id, phase)
                );

                CREATE TABLE IF NOT EXISTS agent_executions (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT,
                    agent_name TEXT,
                    phase TEXT,
                    status TEXT CHECK (status IN ('running', 'completed', 'failed')),
                    score REAL,
                    results TEXT,
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME
                );

                -- Performance indexes
                CREATE INDEX IF NOT EXISTS idx_tasks_session_phase ON tasks(session_id, eipas_phase);
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
                CREATE INDEX IF NOT EXISTS idx_tool_activity_session ON tool_activity(session_id);
                CREATE INDEX IF NOT EXISTS idx_workflow_sessions_status ON workflow_sessions(status);
                CREATE INDEX IF NOT EXISTS idx_agent_executions_session ON agent_executions(session_id);
            """)
            
            conn.commit()
        
        print("  ✅ Initialized comprehensive SQLite database with EIPAS schema")