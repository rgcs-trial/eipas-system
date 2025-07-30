"""
Metrics Collector

Advanced metrics collection system for tracking productivity, performance,
and usage patterns across Claude Code configurations and user interactions.
"""

import json
import time
import sqlite3
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import logging
import threading
import statistics
import hashlib
import psutil
import os

class MetricType(Enum):
    """Types of metrics collected"""
    PRODUCTIVITY = "productivity"
    PERFORMANCE = "performance"
    USAGE = "usage"
    QUALITY = "quality"
    COLLABORATION = "collaboration"
    EFFICIENCY = "efficiency"
    SATISFACTION = "satisfaction"
    SYSTEM = "system"

class MetricGranularity(Enum):
    """Metric aggregation levels"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

@dataclass
class MetricPoint:
    """Individual metric data point"""
    metric_id: str
    timestamp: datetime
    metric_type: MetricType
    category: str
    value: float
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class ProductivityMetrics:
    """Productivity-specific metrics"""
    lines_of_code_written: int = 0
    files_modified: int = 0
    commits_made: int = 0
    issues_resolved: int = 0
    code_reviews_completed: int = 0
    tests_written: int = 0
    documentation_updated: int = 0
    bugs_fixed: int = 0
    features_implemented: int = 0
    refactoring_tasks: int = 0

@dataclass
class PerformanceMetrics:
    """Performance-specific metrics"""
    setup_time_seconds: float = 0.0
    response_time_ms: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    disk_io_mb: float = 0.0
    network_io_mb: float = 0.0
    error_rate: float = 0.0
    success_rate: float = 0.0
    throughput_ops_per_second: float = 0.0
    latency_p99_ms: float = 0.0

@dataclass
class UsageMetrics:
    """Usage pattern metrics"""
    session_duration_minutes: float = 0.0
    commands_executed: int = 0
    tools_used: Set[str] = field(default_factory=set)
    agents_invoked: int = 0
    hooks_triggered: int = 0
    errors_encountered: int = 0
    help_requests: int = 0
    feature_usage: Dict[str, int] = field(default_factory=dict)
    workflow_patterns: List[str] = field(default_factory=list)

@dataclass
class QualityMetrics:
    """Code and process quality metrics"""
    test_coverage_percent: float = 0.0
    linting_score: float = 0.0
    complexity_score: float = 0.0
    maintainability_index: float = 0.0
    security_score: float = 0.0
    documentation_coverage: float = 0.0
    code_duplication_percent: float = 0.0
    technical_debt_hours: float = 0.0
    bug_density: float = 0.0
    review_approval_rate: float = 0.0

class MetricsCollector:
    """Advanced metrics collection and aggregation system"""
    
    def __init__(self, db_path: str = "~/.claude/eipas-system/analytics/metrics.db"):
        self.logger = logging.getLogger(__name__)
        
        # Database setup
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Session tracking
        self.current_session_id = self._generate_session_id()
        self.session_start_time = datetime.now()
        
        # Performance monitoring
        self.process = psutil.Process()
        self._last_cpu_time = self.process.cpu_times()
        self._last_io_counters = self.process.io_counters() if hasattr(self.process, 'io_counters') else None
        
        # Metric buffers for batch processing
        self._metric_buffer: List[MetricPoint] = []
        self._buffer_size = 100
        self._last_flush_time = datetime.now()
        
        # Initialize database
        self._init_database()
        
        # Start background collection
        self._start_background_collection()
    
    def _init_database(self):
        """Initialize metrics database schema"""
        with sqlite3.connect(str(self.db_path)) as conn:
            # Raw metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    tags TEXT,
                    metadata TEXT,
                    session_id TEXT,
                    user_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Aggregated metrics by hour
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics_hourly (
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    avg_value REAL,
                    min_value REAL,
                    max_value REAL,
                    sum_value REAL,
                    count_value INTEGER,
                    std_dev REAL,
                    PRIMARY KEY (timestamp, metric_type, category)
                )
            """)
            
            # Daily summaries
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_summaries (
                    date TEXT PRIMARY KEY,
                    productivity_score REAL,
                    performance_score REAL,
                    quality_score REAL,
                    usage_score REAL,
                    satisfaction_score REAL,
                    total_session_time REAL,
                    total_actions INTEGER,
                    efficiency_rating REAL,
                    improvement_suggestions TEXT
                )
            """)
            
            # User sessions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_minutes REAL,
                    actions_count INTEGER DEFAULT 0,
                    productivity_score REAL,
                    satisfaction_rating INTEGER,
                    notes TEXT
                )
            """)
            
            # Productivity tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS productivity_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    impact_score REAL,
                    automated BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_session ON metrics(session_id)")
    
    def _start_background_collection(self):
        """Start background metric collection thread"""
        def collect_system_metrics():
            while True:
                try:
                    self.collect_system_metrics()
                    time.sleep(30)  # Collect every 30 seconds
                except Exception as e:
                    self.logger.error(f"Error in background collection: {e}")
                    time.sleep(60)  # Wait longer on error
        
        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()
    
    def record_metric(self, metric_id: str, value: float, metric_type: MetricType,
                     category: str, unit: str = "", tags: Optional[Dict[str, str]] = None,
                     metadata: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None):
        """Record a single metric point"""
        
        metric_point = MetricPoint(
            metric_id=metric_id,
            timestamp=datetime.now(),
            metric_type=metric_type,
            category=category,
            value=value,
            unit=unit,
            tags=tags or {},
            metadata=metadata or {},
            session_id=self.current_session_id,
            user_id=user_id
        )
        
        with self._lock:
            self._metric_buffer.append(metric_point)
            
            # Flush buffer if full or time-based
            if (len(self._metric_buffer) >= self._buffer_size or 
                datetime.now() - self._last_flush_time > timedelta(minutes=1)):
                self._flush_buffer()
    
    def record_productivity_event(self, event_type: str, event_data: Dict[str, Any],
                                impact_score: float = 1.0, automated: bool = False):
        """Record a productivity-related event"""
        
        self.record_metric(
            metric_id=f"productivity.{event_type}",
            value=impact_score,
            metric_type=MetricType.PRODUCTIVITY,
            category=event_type,
            unit="score",
            metadata=event_data
        )
        
        # Store in productivity events table
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT INTO productivity_events 
                (timestamp, session_id, event_type, event_data, impact_score, automated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                self.current_session_id,
                event_type,
                json.dumps(event_data),
                impact_score,
                automated
            ))
    
    def record_performance_metrics(self, setup_time: Optional[float] = None,
                                 response_time: Optional[float] = None,
                                 error_rate: Optional[float] = None):
        """Record performance metrics"""
        
        if setup_time is not None:
            self.record_metric("performance.setup_time", setup_time, 
                             MetricType.PERFORMANCE, "latency", "seconds")
        
        if response_time is not None:
            self.record_metric("performance.response_time", response_time,
                             MetricType.PERFORMANCE, "latency", "milliseconds")
        
        if error_rate is not None:
            self.record_metric("performance.error_rate", error_rate,
                             MetricType.PERFORMANCE, "reliability", "percentage")
    
    def record_usage_metrics(self, command_executed: str, tool_used: str,
                           duration_ms: float, success: bool = True):
        """Record usage pattern metrics"""
        
        # Record command execution
        self.record_metric("usage.command_executed", 1.0,
                         MetricType.USAGE, "commands", "count",
                         tags={"command": command_executed, "success": str(success)})
        
        # Record tool usage
        self.record_metric("usage.tool_used", 1.0,
                         MetricType.USAGE, "tools", "count",
                         tags={"tool": tool_used})
        
        # Record execution duration
        self.record_metric("usage.execution_duration", duration_ms,
                         MetricType.USAGE, "timing", "milliseconds",
                         tags={"command": command_executed})
    
    def record_quality_metrics(self, test_coverage: Optional[float] = None,
                             linting_score: Optional[float] = None,
                             complexity_score: Optional[float] = None):
        """Record code quality metrics"""
        
        if test_coverage is not None:
            self.record_metric("quality.test_coverage", test_coverage,
                             MetricType.QUALITY, "testing", "percentage")
        
        if linting_score is not None:
            self.record_metric("quality.linting_score", linting_score,
                             MetricType.QUALITY, "code_style", "score")
        
        if complexity_score is not None:
            self.record_metric("quality.complexity_score", complexity_score,
                             MetricType.QUALITY, "complexity", "score")
    
    def collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = self.process.cpu_percent()
            self.record_metric("system.cpu_usage", cpu_percent,
                             MetricType.SYSTEM, "resources", "percentage")
            
            # Memory usage
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            self.record_metric("system.memory_usage", memory_mb,
                             MetricType.SYSTEM, "resources", "megabytes")
            
            # I/O metrics
            if hasattr(self.process, 'io_counters'):
                io_counters = self.process.io_counters()
                if self._last_io_counters:
                    read_bytes = io_counters.read_bytes - self._last_io_counters.read_bytes
                    write_bytes = io_counters.write_bytes - self._last_io_counters.write_bytes
                    
                    self.record_metric("system.disk_read", read_bytes / (1024 * 1024),
                                     MetricType.SYSTEM, "io", "megabytes")
                    self.record_metric("system.disk_write", write_bytes / (1024 * 1024),
                                     MetricType.SYSTEM, "io", "megabytes")
                
                self._last_io_counters = io_counters
            
            # Thread count
            thread_count = self.process.num_threads()
            self.record_metric("system.thread_count", thread_count,
                             MetricType.SYSTEM, "concurrency", "count")
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def start_session(self, user_id: Optional[str] = None):
        """Start a new user session"""
        self.current_session_id = self._generate_session_id()
        self.session_start_time = datetime.now()
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT INTO user_sessions (session_id, user_id, start_time)
                VALUES (?, ?, ?)
            """, (self.current_session_id, user_id, self.session_start_time.isoformat()))
        
        self.logger.info(f"Started metrics session: {self.current_session_id}")
    
    def end_session(self, satisfaction_rating: Optional[int] = None, notes: Optional[str] = None):
        """End the current user session"""
        end_time = datetime.now()
        duration = (end_time - self.session_start_time).total_seconds() / 60.0  # minutes
        
        # Calculate session productivity score
        productivity_score = self._calculate_session_productivity()
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                UPDATE user_sessions 
                SET end_time = ?, duration_minutes = ?, productivity_score = ?,
                    satisfaction_rating = ?, notes = ?
                WHERE session_id = ?
            """, (
                end_time.isoformat(),
                duration,
                productivity_score,
                satisfaction_rating,
                notes,
                self.current_session_id
            ))
        
        # Record session summary metrics
        self.record_metric("session.duration", duration,
                         MetricType.PRODUCTIVITY, "time", "minutes")
        self.record_metric("session.productivity_score", productivity_score,
                         MetricType.PRODUCTIVITY, "score", "rating")
        
        if satisfaction_rating:
            self.record_metric("session.satisfaction", satisfaction_rating,
                             MetricType.SATISFACTION, "rating", "scale_1_10")
        
        self.logger.info(f"Ended session {self.current_session_id}: {duration:.1f}min, score: {productivity_score:.2f}")
    
    def get_productivity_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get productivity summary for specified period"""
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        summary = {
            "period_days": days,
            "total_sessions": 0,
            "total_time_hours": 0.0,
            "avg_session_duration": 0.0,
            "productivity_trend": [],
            "top_activities": [],
            "efficiency_metrics": {},
            "quality_improvements": {},
            "recommendations": []
        }
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                
                # Session statistics
                cursor = conn.execute("""
                    SELECT COUNT(*) as session_count, 
                           AVG(duration_minutes) as avg_duration,
                           SUM(duration_minutes) as total_duration,
                           AVG(productivity_score) as avg_productivity
                    FROM user_sessions 
                    WHERE start_time >= ?
                """, (cutoff_date,))
                
                session_stats = cursor.fetchone()
                if session_stats:
                    summary["total_sessions"] = session_stats["session_count"]
                    summary["total_time_hours"] = (session_stats["total_duration"] or 0.0) / 60.0
                    summary["avg_session_duration"] = session_stats["avg_duration"] or 0.0
                    summary["avg_productivity_score"] = session_stats["avg_productivity"] or 0.0
                
                # Productivity events
                cursor = conn.execute("""
                    SELECT event_type, COUNT(*) as count, AVG(impact_score) as avg_impact
                    FROM productivity_events 
                    WHERE timestamp >= ?
                    GROUP BY event_type
                    ORDER BY count DESC
                    LIMIT 10
                """, (cutoff_date,))
                
                summary["top_activities"] = [
                    {
                        "activity": row["event_type"],
                        "count": row["count"],
                        "avg_impact": row["avg_impact"]
                    }
                    for row in cursor
                ]
                
                # Daily productivity trend
                cursor = conn.execute("""
                    SELECT DATE(timestamp) as date, AVG(impact_score) as avg_score
                    FROM productivity_events 
                    WHERE timestamp >= ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """, (cutoff_date,))
                
                summary["productivity_trend"] = [
                    {"date": row["date"], "score": row["avg_score"]}
                    for row in cursor
                ]
        
        except Exception as e:
            self.logger.error(f"Error generating productivity summary: {e}")
        
        # Generate recommendations
        summary["recommendations"] = self._generate_productivity_recommendations(summary)
        
        return summary
    
    def get_performance_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance analytics for specified period"""
        
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        analytics = {
            "period_hours": hours,
            "response_times": {"avg": 0.0, "p95": 0.0, "p99": 0.0},
            "error_rates": {"overall": 0.0, "by_category": {}},
            "resource_usage": {"cpu_avg": 0.0, "memory_avg": 0.0},
            "throughput": {"commands_per_hour": 0.0},
            "bottlenecks": [],
            "performance_trends": []
        }
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                # Response time statistics
                cursor = conn.execute("""
                    SELECT AVG(value) as avg_response, 
                           MIN(value) as min_response,
                           MAX(value) as max_response
                    FROM metrics 
                    WHERE metric_id = 'performance.response_time' 
                    AND timestamp >= ?
                """, (cutoff_time,))
                
                response_stats = cursor.fetchone()
                if response_stats and response_stats[0]:
                    analytics["response_times"]["avg"] = response_stats[0]
                    analytics["response_times"]["min"] = response_stats[1]
                    analytics["response_times"]["max"] = response_stats[2]
                
                # Calculate percentiles (simplified)
                cursor = conn.execute("""
                    SELECT value FROM metrics 
                    WHERE metric_id = 'performance.response_time' 
                    AND timestamp >= ?
                    ORDER BY value
                """, (cutoff_time,))
                
                response_times = [row[0] for row in cursor]
                if response_times:
                    p95_index = int(len(response_times) * 0.95)
                    p99_index = int(len(response_times) * 0.99)
                    analytics["response_times"]["p95"] = response_times[min(p95_index, len(response_times)-1)]
                    analytics["response_times"]["p99"] = response_times[min(p99_index, len(response_times)-1)]
                
                # Resource usage
                cursor = conn.execute("""
                    SELECT metric_id, AVG(value) as avg_value
                    FROM metrics 
                    WHERE metric_id IN ('system.cpu_usage', 'system.memory_usage')
                    AND timestamp >= ?
                    GROUP BY metric_id
                """, (cutoff_time,))
                
                for row in cursor:
                    if row[0] == 'system.cpu_usage':
                        analytics["resource_usage"]["cpu_avg"] = row[1]
                    elif row[0] == 'system.memory_usage':
                        analytics["resource_usage"]["memory_avg"] = row[1]
                
                # Throughput calculation
                cursor = conn.execute("""
                    SELECT COUNT(*) as command_count
                    FROM metrics 
                    WHERE metric_id = 'usage.command_executed'
                    AND timestamp >= ?
                """, (cutoff_time,))
                
                command_count = cursor.fetchone()[0]
                analytics["throughput"]["commands_per_hour"] = command_count / hours if hours > 0 else 0
        
        except Exception as e:
            self.logger.error(f"Error generating performance analytics: {e}")
        
        # Identify bottlenecks
        analytics["bottlenecks"] = self._identify_performance_bottlenecks(analytics)
        
        return analytics
    
    def get_usage_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze usage patterns and trends"""
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        patterns = {
            "period_days": days,
            "most_used_tools": [],
            "command_frequency": {},
            "peak_hours": [],
            "workflow_patterns": [],
            "feature_adoption": {},
            "user_efficiency": {}
        }
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                
                # Most used tools
                cursor = conn.execute("""
                    SELECT JSON_EXTRACT(tags, '$.tool') as tool, COUNT(*) as usage_count
                    FROM metrics 
                    WHERE metric_id = 'usage.tool_used'
                    AND timestamp >= ?
                    AND JSON_EXTRACT(tags, '$.tool') IS NOT NULL
                    GROUP BY tool
                    ORDER BY usage_count DESC
                    LIMIT 10
                """, (cutoff_date,))
                
                patterns["most_used_tools"] = [
                    {"tool": row["tool"], "count": row["usage_count"]}
                    for row in cursor if row["tool"]
                ]
                
                # Command frequency
                cursor = conn.execute("""
                    SELECT JSON_EXTRACT(tags, '$.command') as command, COUNT(*) as frequency
                    FROM metrics 
                    WHERE metric_id = 'usage.command_executed'
                    AND timestamp >= ?
                    AND JSON_EXTRACT(tags, '$.command') IS NOT NULL
                    GROUP BY command
                    ORDER BY frequency DESC
                    LIMIT 15
                """, (cutoff_date,))
                
                patterns["command_frequency"] = {
                    row["command"]: row["frequency"]
                    for row in cursor if row["command"]
                }
                
                # Peak usage hours
                cursor = conn.execute("""
                    SELECT strftime('%H', timestamp) as hour, COUNT(*) as activity
                    FROM metrics 
                    WHERE timestamp >= ?
                    GROUP BY hour
                    ORDER BY activity DESC
                    LIMIT 5
                """, (cutoff_date,))
                
                patterns["peak_hours"] = [
                    {"hour": int(row["hour"]), "activity": row["activity"]}
                    for row in cursor
                ]
        
        except Exception as e:
            self.logger.error(f"Error analyzing usage patterns: {e}")
        
        return patterns
    
    def _flush_buffer(self):
        """Flush metric buffer to database"""
        if not self._metric_buffer:
            return
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                for metric in self._metric_buffer:
                    conn.execute("""
                        INSERT INTO metrics 
                        (metric_id, timestamp, metric_type, category, value, unit,
                         tags, metadata, session_id, user_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        metric.metric_id,
                        metric.timestamp.isoformat(),
                        metric.metric_type.value,
                        metric.category,
                        metric.value,
                        metric.unit,
                        json.dumps(metric.tags),
                        json.dumps(metric.metadata),
                        metric.session_id,
                        metric.user_id
                    ))
            
            self._metric_buffer.clear()
            self._last_flush_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error flushing metrics buffer: {e}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(f"{timestamp}{os.getpid()}".encode()).hexdigest()[:8]
        return f"session_{timestamp}_{random_part}"
    
    def _calculate_session_productivity(self) -> float:
        """Calculate productivity score for current session"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute("""
                    SELECT AVG(impact_score) as avg_impact, COUNT(*) as event_count
                    FROM productivity_events 
                    WHERE session_id = ?
                """, (self.current_session_id,))
                
                result = cursor.fetchone()
                if result and result[0]:
                    # Base score on average impact and activity level
                    avg_impact = result[0]
                    event_count = result[1]
                    
                    # Normalize activity level (1-10 events = 0.5-1.0 multiplier)
                    activity_multiplier = min(1.0, 0.5 + (event_count / 20.0))
                    
                    return min(10.0, avg_impact * activity_multiplier * 2.0)  # Scale to 0-10
                
        except Exception as e:
            self.logger.error(f"Error calculating session productivity: {e}")
        
        return 5.0  # Default neutral score
    
    def _generate_productivity_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate productivity improvement recommendations"""
        recommendations = []
        
        # Session duration recommendations
        avg_duration = summary.get("avg_session_duration", 0)
        if avg_duration < 30:
            recommendations.append("Consider longer focused work sessions for better productivity")
        elif avg_duration > 180:
            recommendations.append("Take breaks during long sessions to maintain focus")
        
        # Activity level recommendations
        total_sessions = summary.get("total_sessions", 0)
        if total_sessions < 3:
            recommendations.append("More consistent daily usage could improve workflow efficiency")
        
        # Productivity trend analysis
        trend = summary.get("productivity_trend", [])
        if len(trend) >= 2:
            recent_scores = [t["score"] for t in trend[-3:]]
            if recent_scores and statistics.mean(recent_scores) < 2.0:
                recommendations.append("Recent productivity scores are low - consider reviewing workflow")
        
        # Top activities insights
        top_activities = summary.get("top_activities", [])
        if top_activities:
            most_common = top_activities[0]["activity"]
            recommendations.append(f"'{most_common}' is your most frequent activity - consider optimizing this workflow")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _identify_performance_bottlenecks(self, analytics: Dict[str, Any]) -> List[str]:
        """Identify performance bottlenecks from analytics"""
        bottlenecks = []
        
        # Response time analysis
        response_times = analytics.get("response_times", {})
        avg_response = response_times.get("avg", 0)
        p99_response = response_times.get("p99", 0)
        
        if avg_response > 1000:  # > 1 second
            bottlenecks.append(f"High average response time: {avg_response:.0f}ms")
        
        if p99_response > 5000:  # > 5 seconds
            bottlenecks.append(f"Very high P99 response time: {p99_response:.0f}ms")
        
        # Resource usage analysis
        resource_usage = analytics.get("resource_usage", {})
        cpu_avg = resource_usage.get("cpu_avg", 0)
        memory_avg = resource_usage.get("memory_avg", 0)
        
        if cpu_avg > 80:
            bottlenecks.append(f"High CPU usage: {cpu_avg:.1f}%")
        
        if memory_avg > 1000:  # > 1GB
            bottlenecks.append(f"High memory usage: {memory_avg:.0f}MB")
        
        # Throughput analysis
        throughput = analytics.get("throughput", {})
        commands_per_hour = throughput.get("commands_per_hour", 0)
        
        if commands_per_hour > 0 and avg_response > 0:
            theoretical_max = 3600000 / avg_response  # Commands per hour at avg response time
            if commands_per_hour < theoretical_max * 0.1:  # Less than 10% of theoretical max
                bottlenecks.append("Low throughput relative to response times")
        
        return bottlenecks
    
    def aggregate_hourly_metrics(self):
        """Aggregate raw metrics into hourly summaries"""
        try:
            current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
            cutoff_time = (current_hour - timedelta(hours=2)).isoformat()
            
            with sqlite3.connect(str(self.db_path)) as conn:
                # Get metrics that need aggregation
                cursor = conn.execute("""
                    SELECT 
                        strftime('%Y-%m-%d %H:00:00', timestamp) as hour_bucket,
                        metric_type,
                        category,
                        AVG(value) as avg_value,
                        MIN(value) as min_value,
                        MAX(value) as max_value,
                        SUM(value) as sum_value,
                        COUNT(*) as count_value
                    FROM metrics 
                    WHERE timestamp >= ?
                    GROUP BY hour_bucket, metric_type, category
                """, (cutoff_time,))
                
                # Insert/update hourly aggregations
                for row in cursor:
                    conn.execute("""
                        INSERT OR REPLACE INTO metrics_hourly
                        (timestamp, metric_type, category, avg_value, min_value, 
                         max_value, sum_value, count_value)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, row)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error aggregating hourly metrics: {e}")
    
    def cleanup_old_metrics(self, days_to_keep: int = 90):
        """Clean up old raw metrics (keep aggregated data)"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            with sqlite3.connect(str(self.db_path)) as conn:
                # Delete old raw metrics
                cursor = conn.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff_date,))
                deleted_count = cursor.rowcount
                
                # Delete old productivity events
                conn.execute("DELETE FROM productivity_events WHERE timestamp < ?", (cutoff_date,))
                
                conn.commit()
                
                self.logger.info(f"Cleaned up {deleted_count} old metric records")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old metrics: {e}")
    
    def export_metrics(self, start_date: datetime, end_date: datetime, 
                      format: str = "json") -> str:
        """Export metrics for analysis or backup"""
        
        metrics_data = []
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT * FROM metrics 
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp
                """, (start_date.isoformat(), end_date.isoformat()))
                
                for row in cursor:
                    metric_dict = dict(row)
                    # Parse JSON fields
                    if metric_dict['tags']:
                        metric_dict['tags'] = json.loads(metric_dict['tags'])
                    if metric_dict['metadata']:
                        metric_dict['metadata'] = json.loads(metric_dict['metadata'])
                    
                    metrics_data.append(metric_dict)
        
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return "{}"
        
        if format == "json":
            return json.dumps(metrics_data, indent=2, default=str)
        elif format == "csv":
            # Simplified CSV export
            import io
            import csv
            
            output = io.StringIO()
            if metrics_data:
                fieldnames = ['timestamp', 'metric_id', 'metric_type', 'category', 'value', 'unit']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for metric in metrics_data:
                    writer.writerow({k: metric.get(k, '') for k in fieldnames})
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            # Flush any remaining metrics
            if hasattr(self, '_metric_buffer'):
                self._flush_buffer()
        except:
            pass