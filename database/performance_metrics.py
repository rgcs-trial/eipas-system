"""
Performance Metrics Database

Track configuration effectiveness and measure productivity improvements.
Provides comprehensive analytics on how different configurations impact development workflows.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
import statistics

@dataclass
class PerformanceRecord:
    """A performance measurement record"""
    record_id: str
    pattern_id: str
    project_id: str
    metric_type: str  # 'setup_time', 'productivity', 'error_rate', 'satisfaction'
    metric_value: float
    measurement_timestamp: str
    context: Dict
    baseline_value: Optional[float] = None

@dataclass
class ProductivityMetrics:
    """Comprehensive productivity metrics"""
    setup_time_seconds: float
    daily_commits_before: float
    daily_commits_after: float
    code_quality_score: float
    error_frequency_before: float
    error_frequency_after: float
    developer_satisfaction: float
    time_to_first_success: float
    feature_completion_rate: float

@dataclass
class PerformanceInsights:
    """Performance insights and recommendations"""
    pattern_id: str
    overall_score: float
    productivity_improvement: float
    setup_efficiency: float
    error_reduction: float
    satisfaction_rating: float
    trends: Dict[str, str]
    recommendations: List[str]
    comparable_patterns: List[str]

class PerformanceMetricsDB:
    """Database for tracking and analyzing configuration performance metrics"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path or Path.home() / '.claude' / 'performance_metrics.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._initialize_database()
        
        # Metric weights for overall scoring
        self.metric_weights = {
            'setup_time': 0.15,
            'productivity_gain': 0.25,
            'error_reduction': 0.20,
            'satisfaction': 0.25,
            'feature_velocity': 0.15
        }
    
    def _initialize_database(self):
        """Initialize SQLite database with performance tracking tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Performance records table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_records (
                        record_id TEXT PRIMARY KEY,
                        pattern_id TEXT NOT NULL,
                        project_id TEXT NOT NULL,
                        metric_type TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        baseline_value REAL,
                        measurement_timestamp TEXT NOT NULL,
                        context TEXT,  -- JSON
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Productivity sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS productivity_sessions (
                        session_id TEXT PRIMARY KEY,
                        pattern_id TEXT NOT NULL,
                        project_id TEXT NOT NULL,
                        user_id TEXT,
                        start_timestamp TEXT NOT NULL,
                        end_timestamp TEXT,
                        commits_count INTEGER DEFAULT 0,
                        lines_added INTEGER DEFAULT 0,
                        lines_removed INTEGER DEFAULT 0,
                        files_modified INTEGER DEFAULT 0,
                        errors_encountered INTEGER DEFAULT 0,
                        commands_used TEXT,  -- JSON
                        satisfaction_rating REAL,
                        session_notes TEXT
                    )
                ''')
                
                # Configuration benchmarks table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS configuration_benchmarks (
                        benchmark_id TEXT PRIMARY KEY,
                        pattern_id TEXT NOT NULL,
                        benchmark_type TEXT NOT NULL,  -- 'setup', 'daily_usage', 'feature_delivery'
                        environment_context TEXT,  -- JSON
                        execution_time_ms INTEGER,
                        memory_usage_mb REAL,
                        cpu_usage_percent REAL,
                        success_rate REAL,
                        error_count INTEGER,
                        timestamp TEXT NOT NULL
                    )
                ''')
                
                # Performance analytics cache
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_analytics (
                        pattern_id TEXT PRIMARY KEY,
                        overall_score REAL,
                        productivity_improvement REAL,
                        setup_efficiency REAL,
                        error_reduction REAL,
                        satisfaction_rating REAL,
                        trend_data TEXT,  -- JSON
                        recommendations TEXT,  -- JSON
                        last_updated TEXT
                    )
                ''')
                
                # Indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_perf_pattern ON performance_records(pattern_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_perf_timestamp ON performance_records(measurement_timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_pattern ON productivity_sessions(pattern_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_benchmark_pattern ON configuration_benchmarks(pattern_id)')
                
                conn.commit()
                self.logger.info("Performance metrics database initialized")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize performance database: {e}")
            raise
    
    def record_performance_metric(self, record: PerformanceRecord) -> bool:
        """Record a performance metric"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO performance_records 
                    (record_id, pattern_id, project_id, metric_type, metric_value, 
                     baseline_value, measurement_timestamp, context)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.record_id,
                    record.pattern_id,
                    record.project_id,
                    record.metric_type,
                    record.metric_value,
                    record.baseline_value,
                    record.measurement_timestamp,
                    json.dumps(record.context)
                ))
                
                conn.commit()
                
                # Update analytics cache
                self._update_performance_analytics(record.pattern_id)
                
                self.logger.info(f"Recorded performance metric: {record.metric_type} for {record.pattern_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to record performance metric: {e}")
            return False
    
    def start_productivity_session(self, session_id: str, pattern_id: str, 
                                 project_id: str, user_id: str = None) -> bool:
        """Start tracking a productivity session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO productivity_sessions 
                    (session_id, pattern_id, project_id, user_id, start_timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    pattern_id,
                    project_id,
                    user_id,
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                self.logger.info(f"Started productivity session: {session_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to start productivity session: {e}")
            return False
    
    def end_productivity_session(self, session_id: str, metrics: ProductivityMetrics,
                               satisfaction_rating: float = None, notes: str = None) -> bool:
        """End and record productivity session results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate derived metrics
                productivity_gain = (metrics.daily_commits_after - metrics.daily_commits_before) / max(1, metrics.daily_commits_before)
                error_reduction = (metrics.error_frequency_before - metrics.error_frequency_after) / max(1, metrics.error_frequency_before)
                
                cursor.execute('''
                    UPDATE productivity_sessions 
                    SET end_timestamp = ?, 
                        commits_count = ?,
                        errors_encountered = ?,
                        satisfaction_rating = ?,
                        session_notes = ?
                    WHERE session_id = ?
                ''', (
                    datetime.now().isoformat(),
                    int(metrics.daily_commits_after),
                    int(metrics.error_frequency_after),
                    satisfaction_rating,
                    notes,
                    session_id
                ))
                
                # Record derived metrics
                cursor.execute('SELECT pattern_id, project_id FROM productivity_sessions WHERE session_id = ?', (session_id,))
                result = cursor.fetchone()
                
                if result:
                    pattern_id, project_id = result
                    
                    # Record productivity improvement
                    self.record_performance_metric(PerformanceRecord(
                        record_id=f"{session_id}_productivity",
                        pattern_id=pattern_id,
                        project_id=project_id,
                        metric_type='productivity_gain',
                        metric_value=productivity_gain,
                        measurement_timestamp=datetime.now().isoformat(),
                        context={'session_id': session_id}
                    ))
                    
                    # Record error reduction
                    self.record_performance_metric(PerformanceRecord(
                        record_id=f"{session_id}_errors",
                        pattern_id=pattern_id,
                        project_id=project_id,
                        metric_type='error_reduction',
                        metric_value=error_reduction,
                        measurement_timestamp=datetime.now().isoformat(),
                        context={'session_id': session_id}
                    ))
                    
                    # Record satisfaction
                    if satisfaction_rating is not None:
                        self.record_performance_metric(PerformanceRecord(
                            record_id=f"{session_id}_satisfaction",
                            pattern_id=pattern_id,
                            project_id=project_id,
                            metric_type='satisfaction',
                            metric_value=satisfaction_rating,
                            measurement_timestamp=datetime.now().isoformat(),
                            context={'session_id': session_id}
                        ))
                
                conn.commit()
                self.logger.info(f"Ended productivity session: {session_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to end productivity session: {e}")
            return False
    
    def record_configuration_benchmark(self, pattern_id: str, benchmark_type: str,
                                     execution_time_ms: int, success_rate: float,
                                     environment_context: Dict = None) -> bool:
        """Record configuration benchmark results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                benchmark_id = f"{pattern_id}_{benchmark_type}_{int(datetime.now().timestamp())}"
                
                cursor.execute('''
                    INSERT INTO configuration_benchmarks
                    (benchmark_id, pattern_id, benchmark_type, environment_context,
                     execution_time_ms, success_rate, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    benchmark_id,
                    pattern_id,
                    benchmark_type,
                    json.dumps(environment_context or {}),
                    execution_time_ms,
                    success_rate,
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                self.logger.info(f"Recorded benchmark for {pattern_id}: {benchmark_type}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to record benchmark: {e}")
            return False
    
    def get_performance_insights(self, pattern_id: str) -> Optional[PerformanceInsights]:
        """Get comprehensive performance insights for a pattern"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if analytics are cached
                cursor.execute('''
                    SELECT * FROM performance_analytics WHERE pattern_id = ?
                ''', (pattern_id,))
                
                cached = cursor.fetchone()
                if cached:
                    return PerformanceInsights(
                        pattern_id=cached[0],
                        overall_score=cached[1],
                        productivity_improvement=cached[2],
                        setup_efficiency=cached[3],
                        error_reduction=cached[4],
                        satisfaction_rating=cached[5],
                        trends=json.loads(cached[6]) if cached[6] else {},
                        recommendations=json.loads(cached[7]) if cached[7] else [],
                        comparable_patterns=[]  # Would be populated from similarity analysis
                    )
                else:
                    # Generate analytics
                    self._update_performance_analytics(pattern_id)
                    return self.get_performance_insights(pattern_id)
                    
        except Exception as e:
            self.logger.error(f"Failed to get performance insights: {e}")
            return None
    
    def _update_performance_analytics(self, pattern_id: str):
        """Update performance analytics cache for a pattern"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all performance metrics for this pattern
                cursor.execute('''
                    SELECT metric_type, metric_value, measurement_timestamp
                    FROM performance_records 
                    WHERE pattern_id = ?
                    ORDER BY measurement_timestamp DESC
                ''', (pattern_id,))
                
                metrics = cursor.fetchall()
                if not metrics:
                    return
                
                # Organize metrics by type
                metric_groups = {}
                for metric_type, value, timestamp in metrics:
                    if metric_type not in metric_groups:
                        metric_groups[metric_type] = []
                    metric_groups[metric_type].append((value, timestamp))
                
                # Calculate aggregated scores
                overall_score = 0.0
                productivity_improvement = self._calculate_metric_average(metric_groups.get('productivity_gain', []))
                setup_efficiency = self._calculate_setup_efficiency(metric_groups.get('setup_time', []))
                error_reduction = self._calculate_metric_average(metric_groups.get('error_reduction', []))
                satisfaction_rating = self._calculate_metric_average(metric_groups.get('satisfaction', []))
                
                # Calculate overall score using weighted average
                scores = {
                    'productivity_gain': productivity_improvement,
                    'setup_time': setup_efficiency,
                    'error_reduction': error_reduction,
                    'satisfaction': satisfaction_rating
                }
                
                weighted_sum = 0.0
                total_weight = 0.0
                
                for metric_type, score in scores.items():
                    if score is not None and metric_type in self.metric_weights:
                        weight = self.metric_weights[metric_type]
                        weighted_sum += score * weight
                        total_weight += weight
                
                overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
                
                # Calculate trends
                trends = self._calculate_trends(metric_groups)
                
                # Generate recommendations
                recommendations = self._generate_recommendations(scores, trends)
                
                # Store analytics
                cursor.execute('''
                    INSERT OR REPLACE INTO performance_analytics
                    (pattern_id, overall_score, productivity_improvement, setup_efficiency,
                     error_reduction, satisfaction_rating, trend_data, recommendations, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern_id,
                    overall_score,
                    productivity_improvement or 0.0,
                    setup_efficiency or 0.0,
                    error_reduction or 0.0,
                    satisfaction_rating or 0.0,
                    json.dumps(trends),
                    json.dumps(recommendations),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to update performance analytics: {e}")
    
    def _calculate_metric_average(self, metric_data: List[Tuple[float, str]]) -> Optional[float]:
        """Calculate average of metric values"""
        if not metric_data:
            return None
        
        values = [value for value, _ in metric_data]
        return statistics.mean(values)
    
    def _calculate_setup_efficiency(self, setup_times: List[Tuple[float, str]]) -> Optional[float]:
        """Calculate setup efficiency score (lower time = higher efficiency)"""
        if not setup_times:
            return None
        
        times = [time for time, _ in setup_times]
        avg_time = statistics.mean(times)
        
        # Convert to efficiency score (0-1, where 1 is very efficient)
        # Assuming 60 seconds is baseline, 30 seconds is excellent
        efficiency = max(0.0, min(1.0, (120 - avg_time) / 90))
        return efficiency
    
    def _calculate_trends(self, metric_groups: Dict[str, List[Tuple[float, str]]]) -> Dict[str, str]:
        """Calculate trend direction for each metric"""
        trends = {}
        
        for metric_type, data in metric_groups.items():
            if len(data) < 3:
                trends[metric_type] = 'insufficient_data'
                continue
            
            # Sort by timestamp
            sorted_data = sorted(data, key=lambda x: x[1])
            
            # Split into two halves
            split_point = len(sorted_data) // 2
            early_values = [value for value, _ in sorted_data[:split_point]]
            recent_values = [value for value, _ in sorted_data[split_point:]]
            
            early_avg = statistics.mean(early_values)
            recent_avg = statistics.mean(recent_values)
            
            change_percent = (recent_avg - early_avg) / max(abs(early_avg), 0.001)
            
            if change_percent > 0.1:
                trends[metric_type] = 'improving'
            elif change_percent < -0.1:
                trends[metric_type] = 'declining'
            else:
                trends[metric_type] = 'stable'
        
        return trends
    
    def _generate_recommendations(self, scores: Dict[str, Optional[float]], 
                                trends: Dict[str, str]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Setup efficiency recommendations
        setup_score = scores.get('setup_time', 0)
        if setup_score is not None and setup_score < 0.7:
            recommendations.append("Consider optimizing installation scripts to reduce setup time")
        
        # Productivity recommendations
        productivity_score = scores.get('productivity_gain', 0)
        if productivity_score is not None and productivity_score < 0.2:
            recommendations.append("Review agent configurations to improve development velocity")
        
        # Error reduction recommendations
        error_score = scores.get('error_reduction', 0)
        if error_score is not None and error_score < 0.5:
            recommendations.append("Add more comprehensive validation hooks to catch errors early")
        
        # Satisfaction recommendations
        satisfaction_score = scores.get('satisfaction', 0)
        if satisfaction_score is not None and satisfaction_score < 0.7:
            recommendations.append("Gather user feedback to identify pain points in the configuration")
        
        # Trend-based recommendations
        for metric, trend in trends.items():
            if trend == 'declining':
                recommendations.append(f"Investigate declining {metric} - may indicate configuration issues")
        
        return recommendations
    
    def get_comparative_analysis(self, pattern_ids: List[str]) -> Dict[str, Dict]:
        """Get comparative performance analysis between patterns"""
        try:
            analysis = {}
            
            for pattern_id in pattern_ids:
                insights = self.get_performance_insights(pattern_id)
                if insights:
                    analysis[pattern_id] = {
                        'overall_score': insights.overall_score,
                        'productivity_improvement': insights.productivity_improvement,
                        'setup_efficiency': insights.setup_efficiency,
                        'error_reduction': insights.error_reduction,
                        'satisfaction_rating': insights.satisfaction_rating
                    }
            
            # Add rankings
            if len(analysis) > 1:
                for metric in ['overall_score', 'productivity_improvement', 'setup_efficiency', 
                              'error_reduction', 'satisfaction_rating']:
                    ranked = sorted(analysis.items(), 
                                  key=lambda x: x[1].get(metric, 0), reverse=True)
                    
                    for i, (pattern_id, data) in enumerate(ranked):
                        analysis[pattern_id][f'{metric}_rank'] = i + 1
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get comparative analysis: {e}")
            return {}
    
    def export_performance_data(self, export_path: Path, 
                              date_range: Optional[Tuple[str, str]] = None) -> bool:
        """Export performance data to JSON file"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with optional date filtering
                base_query = '''
                    SELECT * FROM performance_records
                '''
                params = []
                
                if date_range:
                    base_query += ' WHERE measurement_timestamp BETWEEN ? AND ?'
                    params.extend(date_range)
                
                base_query += ' ORDER BY measurement_timestamp DESC'
                
                cursor.execute(base_query, params)
                records = cursor.fetchall()
                
                # Get analytics data
                cursor.execute('SELECT * FROM performance_analytics')
                analytics = cursor.fetchall()
                
                export_data = {
                    'performance_records': [
                        {
                            'record_id': row[0],
                            'pattern_id': row[1],
                            'project_id': row[2],
                            'metric_type': row[3],
                            'metric_value': row[4],
                            'baseline_value': row[5],
                            'measurement_timestamp': row[6],
                            'context': json.loads(row[7]) if row[7] else {}
                        }
                        for row in records
                    ],
                    'analytics': [
                        {
                            'pattern_id': row[0],
                            'overall_score': row[1],
                            'productivity_improvement': row[2],
                            'setup_efficiency': row[3],
                            'error_reduction': row[4],
                            'satisfaction_rating': row[5],
                            'trends': json.loads(row[6]) if row[6] else {},
                            'recommendations': json.loads(row[7]) if row[7] else []
                        }
                        for row in analytics
                    ],
                    'exported_at': datetime.now().isoformat(),
                    'date_range': date_range
                }
                
                with open(export_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                self.logger.info(f"Exported performance data to {export_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to export performance data: {e}")
            return False