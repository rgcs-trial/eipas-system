"""
Performance Trend Analyzer

Advanced trend analysis system for identifying performance bottlenecks,
predicting degradation, and recommending optimization strategies.
"""

import json
import math
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from enum import Enum
import logging
import statistics
from collections import defaultdict, deque
import sqlite3

from .metrics_collector import MetricsCollector, MetricType
from .analytics_engine import AnalyticsEngine, TrendAnalysis, TrendDirection

class BottleneckType(Enum):
    """Types of performance bottlenecks"""
    CPU_BOUND = "cpu_bound"
    MEMORY_BOUND = "memory_bound"
    IO_BOUND = "io_bound"
    NETWORK_BOUND = "network_bound"
    LATENCY_BOUND = "latency_bound"
    THROUGHPUT_BOUND = "throughput_bound"
    CONCURRENCY_BOUND = "concurrency_bound"
    ALGORITHM_BOUND = "algorithm_bound"

class PerformanceRegion(Enum):
    """Performance trend regions"""
    OPTIMAL = "optimal"
    ACCEPTABLE = "acceptable"
    DEGRADING = "degrading"
    CRITICAL = "critical"
    FAILING = "failing"

class TrendSeverity(Enum):
    """Severity of performance trends"""
    BENIGN = "benign"
    CONCERNING = "concerning"
    URGENT = "urgent"
    CRITICAL = "critical"

@dataclass
class PerformanceBottleneck:
    """Identified performance bottleneck"""
    bottleneck_id: str
    bottleneck_type: BottleneckType
    affected_metrics: List[str]
    severity: TrendSeverity
    confidence: float
    impact_score: float
    description: str
    root_cause_analysis: List[str]
    recommended_actions: List[str]
    estimated_impact: Dict[str, float]
    detection_time: datetime
    trend_data: Dict[str, Any]

@dataclass
class TrendForecast:
    """Performance trend forecast"""
    metric_name: str
    current_value: float
    forecast_horizon: timedelta
    predicted_trajectory: List[Tuple[datetime, float]]
    confidence_bands: List[Tuple[float, float]]
    trend_classification: str
    degradation_risk: float
    time_to_threshold: Optional[timedelta]
    recommended_interventions: List[str]

@dataclass
class PerformanceProfile:
    """Comprehensive performance profile"""
    profile_id: str
    analysis_period: timedelta
    metrics_analyzed: List[str]
    overall_health_score: float
    performance_region: PerformanceRegion
    bottlenecks: List[PerformanceBottleneck]
    trend_forecasts: List[TrendForecast]
    optimization_opportunities: List[str]
    risk_assessment: Dict[str, float]
    generated_at: datetime

@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    recommendation_id: str
    title: str
    description: str
    bottleneck_addressed: str
    optimization_type: str
    priority: str
    effort_estimate: str
    expected_improvement: Dict[str, float]
    implementation_steps: List[str]
    monitoring_metrics: List[str]
    rollback_plan: str
    success_criteria: List[str]

class TrendAnalyzer:
    """Advanced performance trend analysis engine"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 analytics_engine: Optional[AnalyticsEngine] = None,
                 db_path: str = "~/.claude/eipas-system/analytics/trends.db"):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        if metrics_collector:
            self.metrics_collector = metrics_collector
        else:
            self.metrics_collector = MetricsCollector()
        
        if analytics_engine:
            self.analytics_engine = analytics_engine
        else:
            self.analytics_engine = AnalyticsEngine(self.metrics_collector)
        
        # Database setup
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Performance thresholds and benchmarks
        self.performance_thresholds = self._initialize_thresholds()
        self.bottleneck_patterns = self._initialize_bottleneck_patterns()
        self.optimization_templates = self._initialize_optimization_templates()
        
        # Trend analysis parameters
        self.trend_window_size = 50  # Data points for trend analysis
        self.anomaly_threshold = 2.5  # Standard deviations
        self.confidence_threshold = 0.7
        self.degradation_threshold = 0.15  # 15% degradation threshold
        
        # Historical data for learning
        self.performance_history = deque(maxlen=1000)
        self.bottleneck_history = []
        
        # Initialize database
        self._init_database()
    
    def _initialize_thresholds(self) -> Dict[str, Dict]:
        """Initialize performance thresholds for different metrics"""
        return {
            'response_time_ms': {
                'optimal': 100,
                'acceptable': 300,
                'degrading': 800,
                'critical': 2000,
                'failing': 5000
            },
            'cpu_usage_percent': {
                'optimal': 30,
                'acceptable': 50,
                'degrading': 70,
                'critical': 85,
                'failing': 95
            },
            'memory_usage_mb': {
                'optimal': 256,
                'acceptable': 512,
                'degrading': 1024,
                'critical': 2048,
                'failing': 4096
            },
            'throughput_ops_per_sec': {
                'optimal': 100,
                'acceptable': 50,
                'degrading': 20,
                'critical': 10,
                'failing': 5
            },
            'error_rate_percent': {
                'optimal': 0.1,
                'acceptable': 1.0,
                'degrading': 3.0,
                'critical': 5.0,
                'failing': 10.0
            },
            'disk_io_mb_per_sec': {
                'optimal': 10,
                'acceptable': 25,
                'degrading': 50,
                'critical': 100,
                'failing': 200
            }
        }
    
    def _initialize_bottleneck_patterns(self) -> Dict[str, Dict]:
        """Initialize patterns for bottleneck detection"""
        return {
            'cpu_bottleneck': {
                'indicators': ['cpu_usage_percent', 'response_time_ms'],
                'conditions': {
                    'cpu_usage_percent': {'min': 70, 'sustained_minutes': 5},
                    'response_time_ms': {'increase_percent': 20}
                },
                'root_causes': [
                    'Inefficient algorithms or code',
                    'Excessive computational workload',
                    'Lack of caching strategies',
                    'Poor concurrency management'
                ],
                'optimizations': [
                    'Implement caching mechanisms',
                    'Optimize algorithm complexity',
                    'Add horizontal scaling',
                    'Improve concurrency handling'
                ]
            },
            'memory_bottleneck': {
                'indicators': ['memory_usage_mb', 'response_time_ms', 'error_rate_percent'],
                'conditions': {
                    'memory_usage_mb': {'min': 1024, 'growth_rate': 10},
                    'error_rate_percent': {'increase_percent': 50}
                },
                'root_causes': [
                    'Memory leaks in application',
                    'Inefficient data structures',
                    'Large object allocations',
                    'Insufficient garbage collection'
                ],
                'optimizations': [
                    'Fix memory leaks',
                    'Optimize data structures',
                    'Implement object pooling',
                    'Tune garbage collection'
                ]
            },
            'io_bottleneck': {
                'indicators': ['disk_io_mb_per_sec', 'response_time_ms'],
                'conditions': {
                    'disk_io_mb_per_sec': {'min': 50, 'sustained_minutes': 3},
                    'response_time_ms': {'correlation_with_io': 0.7}
                },
                'root_causes': [
                    'Excessive database queries',
                    'Large file operations',
                    'Inefficient disk access patterns',
                    'Storage system limitations'
                ],
                'optimizations': [
                    'Implement query optimization',
                    'Add database indexing',
                    'Use asynchronous I/O',
                    'Implement connection pooling'
                ]
            },
            'latency_bottleneck': {
                'indicators': ['response_time_ms', 'throughput_ops_per_sec'],
                'conditions': {
                    'response_time_ms': {'p95': 1000, 'trend': 'increasing'},
                    'throughput_ops_per_sec': {'trend': 'decreasing'}
                },
                'root_causes': [
                    'Network latency issues',
                    'External service dependencies',
                    'Inefficient API calls',
                    'Synchronous processing bottlenecks'
                ],
                'optimizations': [
                    'Implement request batching',
                    'Add response caching',
                    'Use asynchronous processing',
                    'Optimize network calls'
                ]
            },
            'concurrency_bottleneck': {
                'indicators': ['throughput_ops_per_sec', 'response_time_ms', 'thread_count'],
                'conditions': {
                    'throughput_ops_per_sec': {'plateau': True, 'max_utilization': 0.6},
                    'response_time_ms': {'high_variance': True}
                },
                'root_causes': [
                    'Thread contention and locking',
                    'Resource serialization',
                    'Inadequate thread pool sizing',
                    'Blocking operations'
                ],
                'optimizations': [
                    'Implement lock-free algorithms',
                    'Optimize thread pool configuration',
                    'Use non-blocking I/O',
                    'Implement work stealing'
                ]
            }
        }
    
    def _initialize_optimization_templates(self) -> Dict[str, Dict]:
        """Initialize optimization recommendation templates"""
        return {
            'caching_optimization': {
                'title': 'Implement Strategic Caching',
                'description': 'Add caching layers to reduce computational load and improve response times',
                'effort': 'medium',
                'impact': {'response_time': -0.4, 'cpu_usage': -0.3, 'throughput': 0.5},
                'steps': [
                    'Identify frequently accessed data',
                    'Choose appropriate caching strategy',
                    'Implement cache invalidation logic',
                    'Monitor cache hit rates'
                ]
            },
            'database_optimization': {
                'title': 'Optimize Database Performance',
                'description': 'Improve database queries and indexing strategies',
                'effort': 'high',
                'impact': {'response_time': -0.6, 'io_operations': -0.5, 'throughput': 0.4},
                'steps': [
                    'Analyze slow query patterns',
                    'Add appropriate database indexes',
                    'Optimize query structures',
                    'Implement connection pooling'
                ]
            },
            'algorithm_optimization': {
                'title': 'Optimize Algorithm Efficiency',
                'description': 'Improve algorithmic complexity and data processing efficiency',
                'effort': 'high',
                'impact': {'cpu_usage': -0.5, 'response_time': -0.4, 'memory_usage': -0.2},
                'steps': [
                    'Profile algorithm performance',
                    'Identify optimization opportunities',
                    'Implement more efficient algorithms',
                    'Validate performance improvements'
                ]
            },
            'scaling_optimization': {
                'title': 'Implement Horizontal Scaling',
                'description': 'Add capacity through horizontal scaling strategies',
                'effort': 'high',
                'impact': {'throughput': 0.8, 'response_time': -0.3, 'reliability': 0.6},
                'steps': [
                    'Design scaling architecture',
                    'Implement load balancing',
                    'Add auto-scaling capabilities',
                    'Monitor scaling effectiveness'
                ]
            }
        }
    
    def _init_database(self):
        """Initialize trend analysis database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            # Performance profiles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_profiles (
                    profile_id TEXT PRIMARY KEY,
                    analysis_period_hours INTEGER NOT NULL,
                    metrics_analyzed TEXT NOT NULL,
                    overall_health_score REAL NOT NULL,
                    performance_region TEXT NOT NULL,
                    bottlenecks_data TEXT,
                    forecasts_data TEXT,
                    risk_assessment TEXT,
                    generated_at TEXT NOT NULL
                )
            """)
            
            # Bottlenecks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_bottlenecks (
                    bottleneck_id TEXT PRIMARY KEY,
                    bottleneck_type TEXT NOT NULL,
                    affected_metrics TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    impact_score REAL NOT NULL,
                    description TEXT,
                    root_causes TEXT,
                    recommendations TEXT,
                    detection_time TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Trend forecasts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trend_forecasts (
                    forecast_id TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    forecast_horizon_hours INTEGER NOT NULL,
                    predicted_trajectory TEXT NOT NULL,
                    degradation_risk REAL NOT NULL,
                    time_to_threshold_hours INTEGER,
                    recommendations TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_profiles_generated ON performance_profiles(generated_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bottlenecks_detection ON performance_bottlenecks(detection_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_forecasts_created ON trend_forecasts(created_at)")
    
    def analyze_performance_trends(self, period_hours: int = 24) -> PerformanceProfile:
        """Perform comprehensive performance trend analysis"""
        
        profile_id = f"perf_profile_{int(datetime.now().timestamp())}"
        
        try:
            # Define key performance metrics to analyze
            performance_metrics = [
                'performance.response_time',
                'system.cpu_usage',
                'system.memory_usage',
                'system.disk_read',
                'system.disk_write',
                'usage.command_executed',
                'performance.error_rate'
            ]
            
            # Get comprehensive analytics
            analytics_result = self.analytics_engine.get_comprehensive_analysis(
                performance_metrics, period_hours
            )
            
            # Detect performance bottlenecks
            bottlenecks = self._detect_bottlenecks(analytics_result)
            
            # Generate trend forecasts
            forecasts = self._generate_trend_forecasts(analytics_result.trends, period_hours)
            
            # Calculate overall health score
            health_score = self._calculate_health_score(analytics_result, bottlenecks)
            
            # Determine performance region
            performance_region = self._determine_performance_region(health_score, bottlenecks)
            
            # Generate optimization opportunities
            optimizations = self._generate_optimization_opportunities(bottlenecks, analytics_result)
            
            # Assess risks
            risk_assessment = self._assess_performance_risks(bottlenecks, forecasts)
            
            # Create performance profile
            profile = PerformanceProfile(
                profile_id=profile_id,
                analysis_period=timedelta(hours=period_hours),
                metrics_analyzed=performance_metrics,
                overall_health_score=health_score,
                performance_region=performance_region,
                bottlenecks=bottlenecks,
                trend_forecasts=forecasts,
                optimization_opportunities=optimizations,
                risk_assessment=risk_assessment,
                generated_at=datetime.now(timezone.utc)
            )
            
            # Store profile
            self._store_performance_profile(profile)
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance trends: {e}")
            return PerformanceProfile(
                profile_id=profile_id,
                analysis_period=timedelta(hours=period_hours),
                metrics_analyzed=[],
                overall_health_score=0.0,
                performance_region=PerformanceRegion.CRITICAL,
                bottlenecks=[],
                trend_forecasts=[],
                optimization_opportunities=["Analysis failed - investigate system health"],
                risk_assessment={'analysis_failure': 1.0},
                generated_at=datetime.now(timezone.utc)
            )
    
    def _detect_bottlenecks(self, analytics_result) -> List[PerformanceBottleneck]:
        """Detect performance bottlenecks from analytics data"""
        bottlenecks = []
        
        try:
            # Analyze each bottleneck pattern
            for pattern_name, pattern in self.bottleneck_patterns.items():
                bottleneck = self._check_bottleneck_pattern(pattern_name, pattern, analytics_result)
                if bottleneck:
                    bottlenecks.append(bottleneck)
            
            # Check for additional bottlenecks from trends and anomalies
            trend_bottlenecks = self._detect_trend_based_bottlenecks(analytics_result.trends)
            bottlenecks.extend(trend_bottlenecks)
            
            anomaly_bottlenecks = self._detect_anomaly_based_bottlenecks(analytics_result.anomalies)
            bottlenecks.extend(anomaly_bottlenecks)
            
        except Exception as e:
            self.logger.error(f"Error detecting bottlenecks: {e}")
        
        return bottlenecks[:10]  # Limit to top 10 bottlenecks
    
    def _check_bottleneck_pattern(self, pattern_name: str, pattern: Dict, 
                                 analytics_result) -> Optional[PerformanceBottleneck]:
        """Check if a specific bottleneck pattern is present"""
        try:
            indicators = pattern['indicators']
            conditions = pattern['conditions']
            
            # Check if relevant metrics are available
            relevant_trends = [t for t in analytics_result.trends if any(ind in t.metric_name for ind in indicators)]
            relevant_anomalies = [a for a in analytics_result.anomalies if any(ind in a.metric_name for ind in indicators)]
            
            if not relevant_trends and not relevant_anomalies:
                return None
            
            # Check pattern conditions (simplified logic)
            pattern_confidence = 0.0
            affected_metrics = []
            evidence = []
            
            for trend in relevant_trends:
                if 'cpu_usage' in trend.metric_name and pattern_name == 'cpu_bottleneck':
                    if trend.end_value > 70 and trend.direction == TrendDirection.INCREASING:
                        pattern_confidence += 0.4
                        affected_metrics.append(trend.metric_name)
                        evidence.append(f"CPU usage trending up to {trend.end_value:.1f}%")
                
                elif 'memory' in trend.metric_name and pattern_name == 'memory_bottleneck':
                    if trend.change_percent > 10 and trend.direction == TrendDirection.INCREASING:
                        pattern_confidence += 0.4
                        affected_metrics.append(trend.metric_name)
                        evidence.append(f"Memory usage increased by {trend.change_percent:.1f}%")
                
                elif 'response_time' in trend.metric_name and 'latency' in pattern_name:
                    if trend.direction == TrendDirection.INCREASING and trend.confidence > 0.7:
                        pattern_confidence += 0.5
                        affected_metrics.append(trend.metric_name)
                        evidence.append(f"Response time degrading: {trend.change_percent:.1f}% increase")
            
            # Add anomaly evidence
            for anomaly in relevant_anomalies:
                if anomaly.severity in ['high', 'critical']:
                    pattern_confidence += 0.3
                    affected_metrics.append(anomaly.metric_name)
                    evidence.append(f"Anomaly detected: {anomaly.description}")
            
            # Create bottleneck if confidence threshold met
            if pattern_confidence >= 0.6 and affected_metrics:
                bottleneck_type = BottleneckType(pattern_name.replace('_bottleneck', '_bound'))
                severity = self._determine_bottleneck_severity(pattern_confidence, relevant_anomalies)
                
                return PerformanceBottleneck(
                    bottleneck_id=f"{pattern_name}_{int(datetime.now().timestamp())}",
                    bottleneck_type=bottleneck_type,
                    affected_metrics=list(set(affected_metrics)),
                    severity=severity,
                    confidence=pattern_confidence,
                    impact_score=min(1.0, pattern_confidence * len(affected_metrics) / 3),
                    description=f"{pattern_name.replace('_', ' ').title()} detected in system",
                    root_cause_analysis=pattern['root_causes'],
                    recommended_actions=pattern['optimizations'],
                    estimated_impact={'response_time': 0.2, 'throughput': -0.15, 'resource_usage': 0.1},
                    detection_time=datetime.now(timezone.utc),
                    trend_data={'confidence': pattern_confidence, 'evidence': evidence}
                )
            
        except Exception as e:
            self.logger.error(f"Error checking bottleneck pattern {pattern_name}: {e}")
        
        return None
    
    def _detect_trend_based_bottlenecks(self, trends: List[TrendAnalysis]) -> List[PerformanceBottleneck]:
        """Detect bottlenecks based on trend analysis"""
        bottlenecks = []
        
        try:
            # Look for concerning performance trends
            performance_trends = [t for t in trends if any(
                keyword in t.metric_name.lower() 
                for keyword in ['response_time', 'cpu', 'memory', 'error', 'latency']
            )]
            
            for trend in performance_trends:
                # Check for degrading trends
                if (trend.direction == TrendDirection.INCREASING and 
                    trend.confidence > 0.7 and 
                    trend.change_percent > 15):
                    
                    if 'response_time' in trend.metric_name.lower():
                        bottleneck_type = BottleneckType.LATENCY_BOUND
                        description = "Response time showing significant upward trend"
                    elif 'cpu' in trend.metric_name.lower():
                        bottleneck_type = BottleneckType.CPU_BOUND
                        description = "CPU usage showing concerning upward trend"
                    elif 'memory' in trend.metric_name.lower():
                        bottleneck_type = BottleneckType.MEMORY_BOUND
                        description = "Memory usage showing concerning upward trend"
                    else:
                        continue
                    
                    severity = TrendSeverity.URGENT if trend.change_percent > 30 else TrendSeverity.CONCERNING
                    
                    bottleneck = PerformanceBottleneck(
                        bottleneck_id=f"trend_bottleneck_{int(datetime.now().timestamp())}_{trend.metric_name}",
                        bottleneck_type=bottleneck_type,
                        affected_metrics=[trend.metric_name],
                        severity=severity,
                        confidence=trend.confidence,
                        impact_score=min(1.0, trend.change_percent / 50.0),
                        description=description,
                        root_cause_analysis=[f"Metric {trend.metric_name} trending negatively"],
                        recommended_actions=["Investigate root cause", "Implement performance monitoring"],
                        estimated_impact={'performance_degradation': trend.change_percent / 100.0},
                        detection_time=datetime.now(timezone.utc),
                        trend_data=asdict(trend)
                    )
                    
                    bottlenecks.append(bottleneck)
        
        except Exception as e:
            self.logger.error(f"Error detecting trend-based bottlenecks: {e}")
        
        return bottlenecks
    
    def _detect_anomaly_based_bottlenecks(self, anomalies: List) -> List[PerformanceBottleneck]:
        """Detect bottlenecks based on anomaly analysis"""
        bottlenecks = []
        
        try:
            # Group anomalies by metric type
            performance_anomalies = [a for a in anomalies if any(
                keyword in a.metric_name.lower() 
                for keyword in ['response_time', 'cpu', 'memory', 'error', 'throughput']
            )]
            
            # Look for clusters of anomalies that might indicate bottlenecks
            critical_anomalies = [a for a in performance_anomalies if a.severity == 'critical']
            
            if len(critical_anomalies) >= 2:
                # Multiple critical anomalies suggest system-wide bottleneck
                affected_metrics = list(set(a.metric_name for a in critical_anomalies))
                avg_confidence = statistics.mean([a.confidence for a in critical_anomalies])
                
                bottleneck = PerformanceBottleneck(
                    bottleneck_id=f"anomaly_cluster_{int(datetime.now().timestamp())}",
                    bottleneck_type=BottleneckType.ALGORITHM_BOUND,  # General bottleneck
                    affected_metrics=affected_metrics,
                    severity=TrendSeverity.CRITICAL,
                    confidence=avg_confidence,
                    impact_score=min(1.0, len(critical_anomalies) / 5.0),
                    description=f"Multiple critical anomalies detected across {len(affected_metrics)} metrics",
                    root_cause_analysis=["System-wide performance degradation", "Possible resource exhaustion"],
                    recommended_actions=[
                        "Investigate system resource usage",
                        "Check for external dependencies",
                        "Review recent configuration changes"
                    ],
                    estimated_impact={'system_stability': 0.8, 'user_experience': 0.7},
                    detection_time=datetime.now(timezone.utc),
                    trend_data={'anomaly_count': len(critical_anomalies), 'metrics': affected_metrics}
                )
                
                bottlenecks.append(bottleneck)
        
        except Exception as e:
            self.logger.error(f"Error detecting anomaly-based bottlenecks: {e}")
        
        return bottlenecks
    
    def _generate_trend_forecasts(self, trends: List[TrendAnalysis], 
                                 period_hours: int) -> List[TrendForecast]:
        """Generate performance trend forecasts"""
        forecasts = []
        
        try:
            # Focus on key performance metrics
            key_trends = [t for t in trends if any(
                keyword in t.metric_name.lower() 
                for keyword in ['response_time', 'cpu', 'memory', 'throughput', 'error']
            )]
            
            for trend in key_trends:
                forecast = self._create_trend_forecast(trend, period_hours)
                if forecast:
                    forecasts.append(forecast)
        
        except Exception as e:
            self.logger.error(f"Error generating trend forecasts: {e}")
        
        return forecasts
    
    def _create_trend_forecast(self, trend: TrendAnalysis, period_hours: int) -> Optional[TrendForecast]:
        """Create forecast for a single trend"""
        try:
            # Forecast horizon (next 24-48 hours)
            forecast_horizon = timedelta(hours=min(48, period_hours))
            forecast_points = 24  # Hourly forecasts
            
            # Generate forecast trajectory based on trend
            current_time = datetime.now(timezone.utc)
            predicted_trajectory = []
            confidence_bands = []
            
            # Simple linear extrapolation (can be enhanced with more sophisticated models)
            hourly_change = trend.slope if trend.slope != 0 else 0
            current_value = trend.end_value
            
            for i in range(forecast_points):
                forecast_time = current_time + timedelta(hours=i+1)
                predicted_value = current_value + (hourly_change * (i + 1))
                
                # Add some uncertainty
                uncertainty = abs(predicted_value * 0.1) * (1 + i * 0.02)  # Increasing uncertainty
                confidence_band = (
                    max(0, predicted_value - uncertainty),
                    predicted_value + uncertainty
                )
                
                predicted_trajectory.append((forecast_time, predicted_value))
                confidence_bands.append(confidence_band)
            
            # Assess degradation risk
            degradation_risk = self._assess_degradation_risk(trend, predicted_trajectory)
            
            # Determine time to threshold breach
            time_to_threshold = self._calculate_time_to_threshold(trend, predicted_trajectory)
            
            # Generate recommendations
            recommendations = self._generate_forecast_recommendations(trend, degradation_risk)
            
            # Classify trend
            if degradation_risk > 0.7:
                trend_classification = "high_risk_degradation"
            elif degradation_risk > 0.4:
                trend_classification = "moderate_risk"
            elif trend.direction == TrendDirection.IMPROVING:
                trend_classification = "improving"
            else:
                trend_classification = "stable"
            
            return TrendForecast(
                metric_name=trend.metric_name,
                current_value=current_value,
                forecast_horizon=forecast_horizon,
                predicted_trajectory=predicted_trajectory,
                confidence_bands=confidence_bands,
                trend_classification=trend_classification,
                degradation_risk=degradation_risk,
                time_to_threshold=time_to_threshold,
                recommended_interventions=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error creating trend forecast: {e}")
            return None
    
    def _assess_degradation_risk(self, trend: TrendAnalysis, 
                               predicted_trajectory: List[Tuple[datetime, float]]) -> float:
        """Assess risk of performance degradation"""
        try:
            # Check if trend is moving toward problematic thresholds
            metric_name_lower = trend.metric_name.lower()
            
            # Get appropriate thresholds
            thresholds = None
            for threshold_key in self.performance_thresholds:
                if threshold_key.replace('_', '') in metric_name_lower.replace('.', '').replace('_', ''):
                    thresholds = self.performance_thresholds[threshold_key]
                    break
            
            if not thresholds or not predicted_trajectory:
                return 0.5  # Default moderate risk if we can't assess
            
            # Check how close predicted values get to thresholds
            predicted_values = [value for _, value in predicted_trajectory]
            max_predicted = max(predicted_values)
            
            # Determine risk based on threshold proximity
            if max_predicted >= thresholds['failing']:
                return 1.0  # Critical risk
            elif max_predicted >= thresholds['critical']:
                return 0.8  # High risk
            elif max_predicted >= thresholds['degrading']:
                return 0.6  # Moderate risk
            elif max_predicted >= thresholds['acceptable']:
                return 0.3  # Low risk
            else:
                return 0.1  # Minimal risk
            
        except Exception as e:
            self.logger.error(f"Error assessing degradation risk: {e}")
            return 0.5
    
    def _calculate_time_to_threshold(self, trend: TrendAnalysis,
                                   predicted_trajectory: List[Tuple[datetime, float]]) -> Optional[timedelta]:
        """Calculate time until critical threshold is reached"""
        try:
            metric_name_lower = trend.metric_name.lower()
            
            # Get appropriate thresholds
            thresholds = None
            for threshold_key in self.performance_thresholds:
                if threshold_key.replace('_', '') in metric_name_lower.replace('.', '').replace('_', ''):
                    thresholds = self.performance_thresholds[threshold_key]
                    break
            
            if not thresholds or not predicted_trajectory:
                return None
            
            current_time = datetime.now(timezone.utc)
            critical_threshold = thresholds['critical']
            
            # Find first time when threshold is breached
            for forecast_time, predicted_value in predicted_trajectory:
                if predicted_value >= critical_threshold:
                    return forecast_time - current_time
            
            return None  # Threshold not reached in forecast horizon
            
        except Exception as e:
            self.logger.error(f"Error calculating time to threshold: {e}")
            return None
    
    def _generate_forecast_recommendations(self, trend: TrendAnalysis, 
                                         degradation_risk: float) -> List[str]:
        """Generate recommendations based on forecast"""
        recommendations = []
        
        try:
            if degradation_risk > 0.7:
                recommendations.extend([
                    "Immediate intervention required",
                    "Monitor metric closely",
                    "Prepare rollback plans"
                ])
            elif degradation_risk > 0.4:
                recommendations.extend([
                    "Schedule performance review",
                    "Consider proactive optimization",
                    "Increase monitoring frequency"
                ])
            else:
                recommendations.append("Continue monitoring trends")
            
            # Metric-specific recommendations
            metric_lower = trend.metric_name.lower()
            if 'response_time' in metric_lower:
                recommendations.append("Consider caching or query optimization")
            elif 'cpu' in metric_lower:
                recommendations.append("Review CPU-intensive operations")
            elif 'memory' in metric_lower:
                recommendations.append("Check for memory leaks or inefficient allocations")
            
        except Exception as e:
            self.logger.error(f"Error generating forecast recommendations: {e}")
        
        return recommendations
    
    def _calculate_health_score(self, analytics_result, bottlenecks: List[PerformanceBottleneck]) -> float:
        """Calculate overall performance health score"""
        try:
            base_score = 8.0  # Start with good baseline
            
            # Deduct points for bottlenecks
            for bottleneck in bottlenecks:
                if bottleneck.severity == TrendSeverity.CRITICAL:
                    base_score -= 2.0
                elif bottleneck.severity == TrendSeverity.URGENT:
                    base_score -= 1.5
                elif bottleneck.severity == TrendSeverity.CONCERNING:
                    base_score -= 1.0
                else:
                    base_score -= 0.5
            
            # Deduct points for negative trends
            negative_trends = [t for t in analytics_result.trends 
                             if t.direction == TrendDirection.DECREASING and t.confidence > 0.7]
            base_score -= len(negative_trends) * 0.5
            
            # Deduct points for critical anomalies
            critical_anomalies = [a for a in analytics_result.anomalies if a.severity == 'critical']
            base_score -= len(critical_anomalies) * 0.8
            
            return max(0.0, min(10.0, base_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return 5.0
    
    def _determine_performance_region(self, health_score: float, 
                                    bottlenecks: List[PerformanceBottleneck]) -> PerformanceRegion:
        """Determine performance region based on health score and bottlenecks"""
        try:
            critical_bottlenecks = [b for b in bottlenecks if b.severity == TrendSeverity.CRITICAL]
            
            if critical_bottlenecks or health_score < 3.0:
                return PerformanceRegion.CRITICAL
            elif health_score < 5.0:
                return PerformanceRegion.DEGRADING
            elif health_score < 7.0:
                return PerformanceRegion.ACCEPTABLE
            else:
                return PerformanceRegion.OPTIMAL
                
        except Exception as e:
            self.logger.error(f"Error determining performance region: {e}")
            return PerformanceRegion.CRITICAL
    
    def _generate_optimization_opportunities(self, bottlenecks: List[PerformanceBottleneck],
                                           analytics_result) -> List[str]:
        """Generate optimization opportunities"""
        opportunities = []
        
        try:
            # Generate opportunities based on bottlenecks
            bottleneck_types = set(b.bottleneck_type for b in bottlenecks)
            
            for bottleneck_type in bottleneck_types:
                if bottleneck_type == BottleneckType.CPU_BOUND:
                    opportunities.append("Implement CPU optimization strategies")
                elif bottleneck_type == BottleneckType.MEMORY_BOUND:
                    opportunities.append("Optimize memory usage and allocation")
                elif bottleneck_type == BottleneckType.IO_BOUND:
                    opportunities.append("Implement I/O optimization techniques")
                elif bottleneck_type == BottleneckType.LATENCY_BOUND:
                    opportunities.append("Reduce latency through caching and optimization")
            
            # Add general opportunities
            if len(bottlenecks) > 1:
                opportunities.append("Implement comprehensive performance monitoring")
            
            if not opportunities:
                opportunities.append("Continue monitoring for optimization opportunities")
        
        except Exception as e:
            self.logger.error(f"Error generating optimization opportunities: {e}")
        
        return opportunities[:5]  # Limit to top 5
    
    def _assess_performance_risks(self, bottlenecks: List[PerformanceBottleneck],
                                forecasts: List[TrendForecast]) -> Dict[str, float]:
        """Assess various performance risks"""
        risks = {}
        
        try:
            # Degradation risk from forecasts
            if forecasts:
                avg_degradation_risk = statistics.mean([f.degradation_risk for f in forecasts])
                risks['performance_degradation'] = avg_degradation_risk
            
            # System stability risk from bottlenecks
            critical_bottlenecks = [b for b in bottlenecks if b.severity == TrendSeverity.CRITICAL]
            risks['system_stability'] = min(1.0, len(critical_bottlenecks) / 3.0)
            
            # User experience risk
            user_impacting_bottlenecks = [b for b in bottlenecks 
                                        if b.bottleneck_type in [BottleneckType.LATENCY_BOUND, 
                                                               BottleneckType.THROUGHPUT_BOUND]]
            risks['user_experience'] = min(1.0, len(user_impacting_bottlenecks) / 2.0)
            
            # Capacity risk
            capacity_bottlenecks = [b for b in bottlenecks 
                                  if b.bottleneck_type in [BottleneckType.CPU_BOUND, 
                                                         BottleneckType.MEMORY_BOUND]]
            risks['capacity_exhaustion'] = min(1.0, len(capacity_bottlenecks) / 2.0)
        
        except Exception as e:
            self.logger.error(f"Error assessing performance risks: {e}")
        
        return risks
    
    def _determine_bottleneck_severity(self, confidence: float, anomalies: List) -> TrendSeverity:
        """Determine severity of bottleneck"""
        critical_anomalies = [a for a in anomalies if a.severity == 'critical']
        
        if critical_anomalies and confidence > 0.8:
            return TrendSeverity.CRITICAL
        elif confidence > 0.7:
            return TrendSeverity.URGENT
        elif confidence > 0.5:
            return TrendSeverity.CONCERNING
        else:
            return TrendSeverity.BENIGN
    
    def _store_performance_profile(self, profile: PerformanceProfile):
        """Store performance profile in database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO performance_profiles
                    (profile_id, analysis_period_hours, metrics_analyzed, overall_health_score,
                     performance_region, bottlenecks_data, forecasts_data, risk_assessment, generated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.profile_id,
                    int(profile.analysis_period.total_seconds() / 3600),
                    json.dumps(profile.metrics_analyzed),
                    profile.overall_health_score,
                    profile.performance_region.value,
                    json.dumps([asdict(b) for b in profile.bottlenecks], default=str),
                    json.dumps([asdict(f) for f in profile.trend_forecasts], default=str),
                    json.dumps(profile.risk_assessment),
                    profile.generated_at.isoformat()
                ))
                
                # Store bottlenecks separately
                for bottleneck in profile.bottlenecks:
                    conn.execute("""
                        INSERT OR REPLACE INTO performance_bottlenecks
                        (bottleneck_id, bottleneck_type, affected_metrics, severity, confidence,
                         impact_score, description, root_causes, recommendations, detection_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        bottleneck.bottleneck_id,
                        bottleneck.bottleneck_type.value,
                        json.dumps(bottleneck.affected_metrics),
                        bottleneck.severity.value,
                        bottleneck.confidence,
                        bottleneck.impact_score,
                        bottleneck.description,
                        json.dumps(bottleneck.root_cause_analysis),
                        json.dumps(bottleneck.recommended_actions),
                        bottleneck.detection_time.isoformat()
                    ))
        
        except Exception as e:
            self.logger.error(f"Error storing performance profile: {e}")
    
    def get_optimization_recommendations(self, profile: PerformanceProfile) -> List[OptimizationRecommendation]:
        """Generate detailed optimization recommendations"""
        recommendations = []
        
        try:
            # Generate recommendations for each bottleneck
            for bottleneck in profile.bottlenecks:
                rec = self._create_bottleneck_optimization(bottleneck)
                if rec:
                    recommendations.append(rec)
            
            # Generate general recommendations based on performance region
            general_recs = self._create_general_optimizations(profile)
            recommendations.extend(general_recs)
        
        except Exception as e:
            self.logger.error(f"Error generating optimization recommendations: {e}")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _create_bottleneck_optimization(self, bottleneck: PerformanceBottleneck) -> Optional[OptimizationRecommendation]:
        """Create optimization recommendation for specific bottleneck"""
        try:
            bottleneck_type = bottleneck.bottleneck_type.value
            
            if bottleneck_type in ['cpu_bound', 'algorithm_bound']:
                template = self.optimization_templates['algorithm_optimization']
            elif bottleneck_type == 'memory_bound':
                template = self.optimization_templates['caching_optimization']
            elif bottleneck_type in ['io_bound', 'latency_bound']:
                template = self.optimization_templates['database_optimization']
            elif bottleneck_type == 'throughput_bound':
                template = self.optimization_templates['scaling_optimization']
            else:
                return None
            
            return OptimizationRecommendation(
                recommendation_id=f"opt_{bottleneck.bottleneck_id}",
                title=template['title'],
                description=template['description'],
                bottleneck_addressed=bottleneck_type,
                optimization_type=bottleneck_type + "_optimization",
                priority="high" if bottleneck.severity == TrendSeverity.CRITICAL else "medium",
                effort_estimate=template['effort'],
                expected_improvement=template['impact'],
                implementation_steps=template['steps'],
                monitoring_metrics=bottleneck.affected_metrics,
                rollback_plan="Monitor metrics and revert if degradation occurs",
                success_criteria=[f"Reduce {metric} by 20%" for metric in bottleneck.affected_metrics[:3]]
            )
            
        except Exception as e:
            self.logger.error(f"Error creating bottleneck optimization: {e}")
            return None
    
    def _create_general_optimizations(self, profile: PerformanceProfile) -> List[OptimizationRecommendation]:
        """Create general optimization recommendations"""
        recommendations = []
        
        try:
            if profile.performance_region in [PerformanceRegion.DEGRADING, PerformanceRegion.CRITICAL]:
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"general_opt_{int(datetime.now().timestamp())}",
                    title="Implement Comprehensive Performance Monitoring",
                    description="Set up advanced monitoring to track performance trends and detect issues early",
                    bottleneck_addressed="general_performance",
                    optimization_type="monitoring",
                    priority="high",
                    effort_estimate="medium",
                    expected_improvement={'visibility': 0.8, 'response_time': 0.1},
                    implementation_steps=[
                        "Set up performance dashboards",
                        "Configure alerting thresholds",
                        "Implement automated reporting",
                        "Create performance baselines"
                    ],
                    monitoring_metrics=profile.metrics_analyzed,
                    rollback_plan="Disable monitoring if resource impact is significant",
                    success_criteria=["100% metric visibility", "Alert response time <5 minutes"]
                ))
        
        except Exception as e:
            self.logger.error(f"Error creating general optimizations: {e}")
        
        return recommendations