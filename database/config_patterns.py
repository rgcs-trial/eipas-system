"""
Configuration Patterns Database

Store and analyze successful configurations with advanced querying and learning capabilities.
Provides the foundation for intelligent pattern matching and recommendation systems.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import hashlib

@dataclass
class ConfigurationRecord:
    """A configuration usage record with success metrics"""
    record_id: str
    pattern_id: str
    project_context: Dict
    installation_timestamp: str
    success: bool
    performance_metrics: Dict
    user_feedback: Optional[Dict]
    adaptations_made: List[str]
    error_messages: List[str]
    usage_duration_days: int

@dataclass
class PatternAnalytics:
    """Analytics data for a configuration pattern"""
    pattern_id: str
    total_uses: int
    success_rate: float
    avg_setup_time: float
    avg_productivity_gain: float
    common_contexts: List[Dict]
    common_adaptations: List[str]
    trend_direction: str  # 'improving', 'declining', 'stable'
    last_updated: str

class ConfigPatternsDB:
    """Advanced database for configuration patterns and usage analytics"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path or Path.home() / '.claude' / 'config_patterns.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Configuration patterns table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS patterns (
                        pattern_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        contexts TEXT,  -- JSON
                        agents TEXT,    -- JSON
                        hooks TEXT,     -- JSON
                        commands TEXT,  -- JSON
                        settings TEXT,  -- JSON
                        tags TEXT,      -- JSON
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
                
                # Configuration usage records table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS usage_records (
                        record_id TEXT PRIMARY KEY,
                        pattern_id TEXT,
                        project_context TEXT,  -- JSON
                        installation_timestamp TEXT,
                        success BOOLEAN,
                        performance_metrics TEXT,  -- JSON
                        user_feedback TEXT,        -- JSON
                        adaptations_made TEXT,     -- JSON
                        error_messages TEXT,       -- JSON
                        usage_duration_days INTEGER,
                        FOREIGN KEY (pattern_id) REFERENCES patterns (pattern_id)
                    )
                ''')
                
                # Pattern analytics cache table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pattern_analytics (
                        pattern_id TEXT PRIMARY KEY,
                        total_uses INTEGER,
                        success_rate REAL,
                        avg_setup_time REAL,
                        avg_productivity_gain REAL,
                        common_contexts TEXT,     -- JSON
                        common_adaptations TEXT,  -- JSON
                        trend_direction TEXT,
                        last_updated TEXT,
                        FOREIGN KEY (pattern_id) REFERENCES patterns (pattern_id)
                    )
                ''')
                
                # Indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_pattern ON usage_records(pattern_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage_records(installation_timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_success ON usage_records(success)')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def store_pattern(self, pattern: Dict) -> bool:
        """Store a configuration pattern in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO patterns 
                    (pattern_id, name, description, contexts, agents, hooks, commands, settings, tags, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern['pattern_id'],
                    pattern['name'],
                    pattern['description'],
                    json.dumps(pattern.get('contexts', [])),
                    json.dumps(pattern.get('agents', [])),
                    json.dumps(pattern.get('hooks', [])),
                    json.dumps(pattern.get('commands', [])),
                    json.dumps(pattern.get('settings', {})),
                    json.dumps(pattern.get('tags', [])),
                    pattern.get('created_at', now),
                    now
                ))
                
                conn.commit()
                self.logger.info(f"Stored pattern: {pattern['name']}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store pattern: {e}")
            return False
    
    def record_usage(self, record: ConfigurationRecord) -> bool:
        """Record configuration usage with success metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO usage_records 
                    (record_id, pattern_id, project_context, installation_timestamp, success, 
                     performance_metrics, user_feedback, adaptations_made, error_messages, usage_duration_days)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.record_id,
                    record.pattern_id,
                    json.dumps(record.project_context),
                    record.installation_timestamp,
                    record.success,
                    json.dumps(record.performance_metrics),
                    json.dumps(record.user_feedback) if record.user_feedback else None,
                    json.dumps(record.adaptations_made),
                    json.dumps(record.error_messages),
                    record.usage_duration_days
                ))
                
                conn.commit()
                
                # Update analytics cache
                self._update_pattern_analytics(record.pattern_id)
                
                self.logger.info(f"Recorded usage for pattern: {record.pattern_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to record usage: {e}")
            return False
    
    def get_pattern_analytics(self, pattern_id: str) -> Optional[PatternAnalytics]:
        """Get comprehensive analytics for a configuration pattern"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM pattern_analytics WHERE pattern_id = ?
                ''', (pattern_id,))
                
                row = cursor.fetchone()
                if row:
                    return PatternAnalytics(
                        pattern_id=row[0],
                        total_uses=row[1],
                        success_rate=row[2],
                        avg_setup_time=row[3],
                        avg_productivity_gain=row[4],
                        common_contexts=json.loads(row[5]) if row[5] else [],
                        common_adaptations=json.loads(row[6]) if row[6] else [],
                        trend_direction=row[7],
                        last_updated=row[8]
                    )
                else:
                    # Generate analytics if not cached
                    self._update_pattern_analytics(pattern_id)
                    return self.get_pattern_analytics(pattern_id)
                    
        except Exception as e:
            self.logger.error(f"Failed to get pattern analytics: {e}")
            return None
    
    def _update_pattern_analytics(self, pattern_id: str):
        """Update analytics cache for a pattern"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get usage statistics
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_uses,
                        AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
                        project_context,
                        performance_metrics,
                        adaptations_made,
                        installation_timestamp
                    FROM usage_records 
                    WHERE pattern_id = ?
                ''', (pattern_id,))
                
                result = cursor.fetchone()
                if not result or result[0] == 0:
                    return
                
                total_uses = result[0]
                success_rate = result[1] or 0.0
                
                # Get detailed records for analysis
                cursor.execute('''
                    SELECT project_context, performance_metrics, adaptations_made, installation_timestamp
                    FROM usage_records 
                    WHERE pattern_id = ?
                    ORDER BY installation_timestamp DESC
                ''', (pattern_id,))
                
                records = cursor.fetchall()
                
                # Calculate averages
                setup_times = []
                productivity_gains = []
                contexts = []
                adaptations = []
                
                for record in records:
                    try:
                        context = json.loads(record[0]) if record[0] else {}
                        metrics = json.loads(record[1]) if record[1] else {}
                        adapt = json.loads(record[2]) if record[2] else []
                        
                        contexts.append(context)
                        adaptations.extend(adapt)
                        
                        if 'setup_time_seconds' in metrics:
                            setup_times.append(metrics['setup_time_seconds'])
                        if 'productivity_increase_percent' in metrics:
                            productivity_gains.append(metrics['productivity_increase_percent'])
                            
                    except json.JSONDecodeError:
                        continue
                
                avg_setup_time = sum(setup_times) / len(setup_times) if setup_times else 0.0
                avg_productivity_gain = sum(productivity_gains) / len(productivity_gains) if productivity_gains else 0.0
                
                # Analyze common contexts
                common_contexts = self._analyze_common_contexts(contexts)
                
                # Analyze common adaptations
                common_adaptations = self._analyze_common_adaptations(adaptations)
                
                # Determine trend direction
                trend_direction = self._calculate_trend_direction(records)
                
                # Store analytics
                cursor.execute('''
                    INSERT OR REPLACE INTO pattern_analytics
                    (pattern_id, total_uses, success_rate, avg_setup_time, avg_productivity_gain,
                     common_contexts, common_adaptations, trend_direction, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern_id,
                    total_uses,
                    success_rate,
                    avg_setup_time,
                    avg_productivity_gain,
                    json.dumps(common_contexts),
                    json.dumps(common_adaptations),
                    trend_direction,
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to update pattern analytics: {e}")
    
    def _analyze_common_contexts(self, contexts: List[Dict]) -> List[Dict]:
        """Analyze and return common project contexts"""
        if not contexts:
            return []
        
        # Count occurrences of context attributes
        context_counts = {}
        
        for context in contexts:
            for key, value in context.items():
                if isinstance(value, (str, int, float)):
                    context_key = f"{key}:{value}"
                    context_counts[context_key] = context_counts.get(context_key, 0) + 1
                elif isinstance(value, list):
                    for item in value:
                        context_key = f"{key}:{item}"
                        context_counts[context_key] = context_counts.get(context_key, 0) + 1
        
        # Return top contexts (>= 20% occurrence)
        total_contexts = len(contexts)
        threshold = max(1, total_contexts * 0.2)
        
        common_contexts = []
        for context_key, count in context_counts.items():
            if count >= threshold:
                key, value = context_key.split(':', 1)
                common_contexts.append({
                    'attribute': key,
                    'value': value,
                    'frequency': count / total_contexts
                })
        
        return sorted(common_contexts, key=lambda x: x['frequency'], reverse=True)[:10]
    
    def _analyze_common_adaptations(self, adaptations: List[str]) -> List[str]:
        """Analyze and return common adaptations"""
        if not adaptations:
            return []
        
        # Count adaptation occurrences
        adaptation_counts = {}
        for adaptation in adaptations:
            adaptation_counts[adaptation] = adaptation_counts.get(adaptation, 0) + 1
        
        # Return adaptations that occur in >= 10% of cases
        total_records = len(adaptations)
        threshold = max(1, total_records * 0.1)
        
        common = [adapt for adapt, count in adaptation_counts.items() if count >= threshold]
        return sorted(common, key=lambda x: adaptation_counts[x], reverse=True)[:5]
    
    def _calculate_trend_direction(self, records: List[Tuple]) -> str:
        """Calculate trend direction based on recent usage patterns"""
        if len(records) < 3:
            return 'stable'
        
        # Split into recent and older records
        sorted_records = sorted(records, key=lambda x: x[3])  # Sort by timestamp
        split_point = len(sorted_records) // 2
        
        older_records = sorted_records[:split_point]
        recent_records = sorted_records[split_point:]
        
        # Calculate success rates
        older_success = sum(1 for r in older_records if json.loads(r[1] or '{}').get('success', False)) / len(older_records)
        recent_success = sum(1 for r in recent_records if json.loads(r[1] or '{}').get('success', False)) / len(recent_records)
        
        difference = recent_success - older_success
        
        if difference > 0.1:
            return 'improving'
        elif difference < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    def get_trending_patterns(self, limit: int = 10) -> List[Dict]:
        """Get patterns that are trending up in usage and success"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT p.pattern_id, p.name, p.description, a.success_rate, a.total_uses, a.trend_direction
                    FROM patterns p
                    JOIN pattern_analytics a ON p.pattern_id = a.pattern_id
                    WHERE a.trend_direction = 'improving' OR (a.success_rate > 0.8 AND a.total_uses > 5)
                    ORDER BY a.success_rate DESC, a.total_uses DESC
                    LIMIT ?
                ''', (limit,))
                
                results = cursor.fetchall()
                
                trending = []
                for row in results:
                    trending.append({
                        'pattern_id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'success_rate': row[3],
                        'total_uses': row[4],
                        'trend_direction': row[5]
                    })
                
                return trending
                
        except Exception as e:
            self.logger.error(f"Failed to get trending patterns: {e}")
            return []
    
    def search_patterns(self, query: str, context_filter: Optional[Dict] = None, 
                       limit: int = 10) -> List[Dict]:
        """Search patterns by name, description, or context"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                base_query = '''
                    SELECT p.pattern_id, p.name, p.description, p.contexts, p.tags,
                           COALESCE(a.success_rate, 0) as success_rate,
                           COALESCE(a.total_uses, 0) as total_uses
                    FROM patterns p
                    LEFT JOIN pattern_analytics a ON p.pattern_id = a.pattern_id
                    WHERE (p.name LIKE ? OR p.description LIKE ? OR p.tags LIKE ?)
                '''
                
                params = [f'%{query}%', f'%{query}%', f'%{query}%']
                
                # Add context filtering
                if context_filter:
                    for key, value in context_filter.items():
                        base_query += ' AND p.contexts LIKE ?'
                        params.append(f'%{key}:{value}%')
                
                base_query += ' ORDER BY success_rate DESC, total_uses DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(base_query, params)
                results = cursor.fetchall()
                
                patterns = []
                for row in results:
                    patterns.append({
                        'pattern_id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'contexts': json.loads(row[3]) if row[3] else [],
                        'tags': json.loads(row[4]) if row[4] else [],
                        'success_rate': row[5],
                        'total_uses': row[6]
                    })
                
                return patterns
                
        except Exception as e:
            self.logger.error(f"Failed to search patterns: {e}")
            return []
    
    def get_pattern_recommendations(self, project_context: Dict, 
                                  intent: Dict, limit: int = 5) -> List[Dict]:
        """Get intelligent pattern recommendations based on context and intent"""
        try:
            # Generate context signature for matching
            context_signature = self._generate_context_signature(project_context, intent)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get patterns with similar contexts
                cursor.execute('''
                    SELECT p.pattern_id, p.name, p.description, p.contexts, p.tags,
                           a.success_rate, a.total_uses, a.common_contexts
                    FROM patterns p
                    LEFT JOIN pattern_analytics a ON p.pattern_id = a.pattern_id
                    WHERE a.total_uses > 0
                    ORDER BY a.success_rate DESC, a.total_uses DESC
                ''')
                
                results = cursor.fetchall()
                
                # Score patterns based on context similarity
                scored_patterns = []
                for row in results:
                    similarity_score = self._calculate_context_similarity(
                        context_signature, 
                        json.loads(row[7]) if row[7] else [],
                        json.loads(row[3]) if row[3] else []
                    )
                    
                    if similarity_score > 0.3:  # Minimum similarity threshold
                        scored_patterns.append({
                            'pattern_id': row[0],
                            'name': row[1],
                            'description': row[2],
                            'contexts': json.loads(row[3]) if row[3] else [],
                            'tags': json.loads(row[4]) if row[4] else [],
                            'success_rate': row[5] or 0,
                            'total_uses': row[6] or 0,
                            'similarity_score': similarity_score,
                            'recommendation_score': similarity_score * (row[5] or 0) + (row[6] or 0) * 0.01
                        })
                
                # Sort by recommendation score and return top matches
                scored_patterns.sort(key=lambda x: x['recommendation_score'], reverse=True)
                return scored_patterns[:limit]
                
        except Exception as e:
            self.logger.error(f"Failed to get pattern recommendations: {e}")
            return []
    
    def _generate_context_signature(self, project_context: Dict, intent: Dict) -> Dict:
        """Generate a normalized context signature for matching"""
        signature = {}
        
        # Extract key attributes
        signature['architecture'] = project_context.get('architecture_pattern', '')
        signature['languages'] = project_context.get('languages', [])
        signature['frameworks'] = project_context.get('frameworks', [])
        signature['team_size'] = project_context.get('team_size_estimate', 1)
        signature['stage'] = project_context.get('development_stage', '')
        signature['intent'] = intent.get('primary_intent', '')
        signature['domain'] = intent.get('business_domain', '')
        signature['audience'] = intent.get('target_audience', '')
        
        return signature
    
    def _calculate_context_similarity(self, context_sig: Dict, 
                                    common_contexts: List[Dict], 
                                    pattern_contexts: List[str]) -> float:
        """Calculate similarity between project context and pattern contexts"""
        similarity = 0.0
        total_weight = 0.0
        
        # Weights for different context attributes
        weights = {
            'architecture': 3.0,
            'intent': 2.5,
            'languages': 2.0,
            'frameworks': 2.0,
            'stage': 1.5,
            'domain': 1.5,
            'team_size': 1.0
        }
        
        # Check direct context matches
        for context_str in pattern_contexts:
            for key, value in context_sig.items():
                if key in weights:
                    weight = weights[key]
                    total_weight += weight
                    
                    if isinstance(value, list):
                        if any(str(v).lower() in context_str.lower() for v in value):
                            similarity += weight
                    else:
                        if str(value).lower() in context_str.lower():
                            similarity += weight
        
        # Check common contexts from analytics
        for common_ctx in common_contexts:
            attr = common_ctx.get('attribute', '')
            val = common_ctx.get('value', '')
            frequency = common_ctx.get('frequency', 0)
            
            if attr in context_sig:
                ctx_value = context_sig[attr]
                weight = weights.get(attr, 1.0) * frequency
                total_weight += weight
                
                if isinstance(ctx_value, list):
                    if any(str(v).lower() == val.lower() for v in ctx_value):
                        similarity += weight
                else:
                    if str(ctx_value).lower() == val.lower():
                        similarity += weight
        
        return similarity / max(1.0, total_weight) if total_weight > 0 else 0.0
    
    def export_patterns(self, export_path: Path) -> bool:
        """Export all patterns to JSON file"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT p.*, a.success_rate, a.total_uses
                    FROM patterns p
                    LEFT JOIN pattern_analytics a ON p.pattern_id = a.pattern_id
                ''')
                
                patterns = []
                for row in cursor.fetchall():
                    pattern = {
                        'pattern_id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'contexts': json.loads(row[3]) if row[3] else [],
                        'agents': json.loads(row[4]) if row[4] else [],
                        'hooks': json.loads(row[5]) if row[5] else [],
                        'commands': json.loads(row[6]) if row[6] else [],
                        'settings': json.loads(row[7]) if row[7] else {},
                        'tags': json.loads(row[8]) if row[8] else [],
                        'created_at': row[9],
                        'updated_at': row[10],
                        'success_rate': row[11] or 0,
                        'total_uses': row[12] or 0
                    }
                    patterns.append(pattern)
                
                export_data = {
                    'patterns': patterns,
                    'exported_at': datetime.now().isoformat(),
                    'version': '1.0'
                }
                
                with open(export_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                self.logger.info(f"Exported {len(patterns)} patterns to {export_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to export patterns: {e}")
            return False