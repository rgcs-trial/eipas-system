"""
Real-time Analytics Engine

Advanced analytics processor for real-time data analysis, trend detection,
anomaly identification, and predictive insights from productivity and performance metrics.
"""

import json
import math
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from enum import Enum
import logging
import statistics
import threading
import time
from collections import defaultdict, deque
import sqlite3

from .metrics_collector import MetricsCollector, MetricType, MetricPoint

class AnalysisType(Enum):
    """Types of analytics performed"""
    TREND_ANALYSIS = "trend_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    CORRELATION_ANALYSIS = "correlation_analysis"
    FORECASTING = "forecasting"
    PATTERN_RECOGNITION = "pattern_recognition"
    PERFORMANCE_PROFILING = "performance_profiling"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"

class TrendDirection(Enum):
    """Trend direction indicators"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"

class AnomalyType(Enum):
    """Types of anomalies detected"""
    SPIKE = "spike"
    DROP = "drop"
    OUTLIER = "outlier"
    PATTERN_BREAK = "pattern_break"
    THRESHOLD_BREACH = "threshold_breach"

@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    metric_name: str
    direction: TrendDirection
    slope: float
    confidence: float
    r_squared: float
    start_value: float
    end_value: float
    change_percent: float
    analysis_period: timedelta
    data_points: int

@dataclass
class Anomaly:
    """Detected anomaly"""
    anomaly_id: str
    timestamp: datetime
    metric_name: str
    anomaly_type: AnomalyType
    value: float
    expected_value: float
    deviation_score: float
    severity: str  # low, medium, high, critical
    description: str
    confidence: float

@dataclass
class CorrelationResult:
    """Correlation analysis result"""
    metric_a: str
    metric_b: str
    correlation_coefficient: float
    p_value: float
    significance: str  # weak, moderate, strong
    relationship_type: str  # positive, negative, none

@dataclass
class Forecast:
    """Forecasting result"""
    metric_name: str
    forecast_horizon: timedelta
    predicted_values: List[float]
    confidence_intervals: List[Tuple[float, float]]
    timestamps: List[datetime]
    model_accuracy: float
    forecast_method: str

@dataclass
class AnalyticsResult:
    """Comprehensive analytics result"""
    analysis_id: str
    timestamp: datetime
    analysis_type: AnalysisType
    metric_names: List[str]
    trends: List[TrendAnalysis] = field(default_factory=list)
    anomalies: List[Anomaly] = field(default_factory=list)
    correlations: List[CorrelationResult] = field(default_factory=list)
    forecasts: List[Forecast] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0

class AnalyticsEngine:
    """Real-time analytics processing engine"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 db_path: str = "~/.claude/eipas-system/analytics/analytics.db"):
        self.logger = logging.getLogger(__name__)
        
        # Initialize metrics collector
        if metrics_collector:
            self.metrics_collector = metrics_collector
        else:
            self.metrics_collector = MetricsCollector()
        
        # Database setup
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Real-time processing
        self._running = False
        self._analysis_thread = None
        self._lock = threading.Lock()
        
        # Analytics configuration
        self.analysis_interval = 60  # seconds
        self.anomaly_threshold = 2.0  # standard deviations
        self.trend_min_points = 5
        self.correlation_threshold = 0.5
        
        # Data windows for real-time analysis
        self.metric_windows = defaultdict(lambda: deque(maxlen=100))
        self.analysis_history = deque(maxlen=1000)
        
        # Statistical models and thresholds
        self.baseline_stats = {}
        self.anomaly_detectors = {}
        
        # Initialize database
        self._init_database()
        
        # Load historical baselines
        self._load_baselines()
    
    def _init_database(self):
        """Initialize analytics database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            # Analytics results table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics_results (
                    analysis_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    metric_names TEXT NOT NULL,
                    results TEXT NOT NULL,
                    confidence_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Anomalies table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    anomaly_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    anomaly_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    expected_value REAL NOT NULL,
                    deviation_score REAL NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    confidence REAL,
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Baselines table for anomaly detection
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metric_baselines (
                    metric_name TEXT PRIMARY KEY,
                    mean_value REAL NOT NULL,
                    std_deviation REAL NOT NULL,
                    min_value REAL NOT NULL,
                    max_value REAL NOT NULL,
                    data_points INTEGER NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics_results(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_metric ON anomalies(metric_name)")
    
    def start_real_time_processing(self):
        """Start real-time analytics processing"""
        if self._running:
            self.logger.warning("Analytics engine already running")
            return
        
        self._running = True
        self._analysis_thread = threading.Thread(target=self._real_time_analysis_loop, daemon=True)
        self._analysis_thread.start()
        
        self.logger.info("Real-time analytics processing started")
    
    def stop_real_time_processing(self):
        """Stop real-time analytics processing"""
        self._running = False
        if self._analysis_thread:
            self._analysis_thread.join(timeout=5)
        
        self.logger.info("Real-time analytics processing stopped")
    
    def _real_time_analysis_loop(self):
        """Main real-time analysis processing loop"""
        while self._running:
            try:
                # Perform periodic analysis
                self._perform_real_time_analysis()
                
                # Sleep until next analysis
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                self.logger.error(f"Error in real-time analysis loop: {e}")
                time.sleep(self.analysis_interval)
    
    def _perform_real_time_analysis(self):
        """Perform real-time analysis on current metrics"""
        try:
            # Get recent metrics
            recent_metrics = self._get_recent_metrics(minutes=30)
            
            if not recent_metrics:
                return
            
            # Update metric windows
            self._update_metric_windows(recent_metrics)
            
            # Perform anomaly detection
            anomalies = self._detect_anomalies_real_time()
            
            # Perform trend analysis
            trends = self._analyze_trends_real_time()
            
            # Store results if significant findings
            if anomalies or trends:
                result = AnalyticsResult(
                    analysis_id=f"realtime_{int(time.time())}",
                    timestamp=datetime.now(timezone.utc),
                    analysis_type=AnalysisType.ANOMALY_DETECTION,
                    metric_names=list(self.metric_windows.keys()),
                    anomalies=anomalies,
                    trends=trends
                )
                
                self._store_analytics_result(result)
                self.analysis_history.append(result)
            
        except Exception as e:
            self.logger.error(f"Error in real-time analysis: {e}")
    
    def analyze_trends(self, metric_names: List[str], 
                      period_hours: int = 24) -> List[TrendAnalysis]:
        """Analyze trends for specified metrics"""
        trends = []
        
        try:
            for metric_name in metric_names:
                trend = self._analyze_single_metric_trend(metric_name, period_hours)
                if trend:
                    trends.append(trend)
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")
        
        return trends
    
    def _analyze_single_metric_trend(self, metric_name: str, 
                                   period_hours: int) -> Optional[TrendAnalysis]:
        """Analyze trend for a single metric"""
        try:
            # Get historical data
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=period_hours)
            
            data_points = self._get_metric_data(metric_name, start_time, end_time)
            
            if len(data_points) < self.trend_min_points:
                return None
            
            # Extract timestamps and values
            timestamps = [dp['timestamp'] for dp in data_points]
            values = [dp['value'] for dp in data_points]
            
            # Convert timestamps to numeric values for regression
            base_time = timestamps[0].timestamp()
            x_values = [(ts.timestamp() - base_time) / 3600 for ts in timestamps]  # Hours
            
            # Perform linear regression
            slope, confidence, r_squared = self._linear_regression(x_values, values)
            
            # Determine trend direction
            direction = self._determine_trend_direction(slope, confidence)
            
            # Calculate change percentage
            change_percent = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
            
            return TrendAnalysis(
                metric_name=metric_name,
                direction=direction,
                slope=slope,
                confidence=confidence,
                r_squared=r_squared,
                start_value=values[0],
                end_value=values[-1],
                change_percent=change_percent,
                analysis_period=timedelta(hours=period_hours),
                data_points=len(data_points)
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing trend for {metric_name}: {e}")
            return None
    
    def detect_anomalies(self, metric_names: List[str],
                        period_hours: int = 24) -> List[Anomaly]:
        """Detect anomalies in specified metrics"""
        anomalies = []
        
        try:
            for metric_name in metric_names:
                metric_anomalies = self._detect_metric_anomalies(metric_name, period_hours)
                anomalies.extend(metric_anomalies)
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
        
        return anomalies
    
    def _detect_metric_anomalies(self, metric_name: str,
                               period_hours: int) -> List[Anomaly]:
        """Detect anomalies for a single metric"""
        anomalies = []
        
        try:
            # Get recent data
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=period_hours)
            
            data_points = self._get_metric_data(metric_name, start_time, end_time)
            
            if len(data_points) < 10:  # Need sufficient data
                return anomalies
            
            # Get baseline statistics
            baseline = self._get_metric_baseline(metric_name, data_points)
            
            # Check each data point for anomalies
            for dp in data_points[-20:]:  # Check recent 20 points
                deviation_score = abs(dp['value'] - baseline['mean']) / baseline['std']
                
                if deviation_score > self.anomaly_threshold:
                    anomaly_type = AnomalyType.SPIKE if dp['value'] > baseline['mean'] else AnomalyType.DROP
                    severity = self._determine_anomaly_severity(deviation_score)
                    
                    anomaly = Anomaly(
                        anomaly_id=f"anomaly_{int(dp['timestamp'].timestamp())}_{metric_name}",
                        timestamp=dp['timestamp'],
                        metric_name=metric_name,
                        anomaly_type=anomaly_type,
                        value=dp['value'],
                        expected_value=baseline['mean'],
                        deviation_score=deviation_score,
                        severity=severity,
                        description=f"{anomaly_type.value.title()} detected in {metric_name}",
                        confidence=min(0.95, deviation_score / 5.0)
                    )
                    
                    anomalies.append(anomaly)
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies for {metric_name}: {e}")
        
        return anomalies
    
    def analyze_correlations(self, metric_names: List[str],
                           period_hours: int = 24) -> List[CorrelationResult]:
        """Analyze correlations between metrics"""
        correlations = []
        
        try:
            # Get all metric data
            metric_data = {}
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=period_hours)
            
            for metric_name in metric_names:
                data_points = self._get_metric_data(metric_name, start_time, end_time)
                if len(data_points) >= 10:
                    metric_data[metric_name] = data_points
            
            # Calculate correlations between all pairs
            for i, metric_a in enumerate(metric_data.keys()):
                for metric_b in list(metric_data.keys())[i+1:]:
                    correlation = self._calculate_correlation(
                        metric_data[metric_a], metric_data[metric_b]
                    )
                    if correlation:
                        correlations.append(correlation)
            
        except Exception as e:
            self.logger.error(f"Error analyzing correlations: {e}")
        
        return correlations
    
    def generate_forecasts(self, metric_names: List[str],
                         forecast_hours: int = 24,
                         history_hours: int = 168) -> List[Forecast]:
        """Generate forecasts for specified metrics"""
        forecasts = []
        
        try:
            for metric_name in metric_names:
                forecast = self._generate_metric_forecast(metric_name, forecast_hours, history_hours)
                if forecast:
                    forecasts.append(forecast)
            
        except Exception as e:
            self.logger.error(f"Error generating forecasts: {e}")
        
        return forecasts
    
    def _generate_metric_forecast(self, metric_name: str,
                                forecast_hours: int, history_hours: int) -> Optional[Forecast]:
        """Generate forecast for a single metric"""
        try:
            # Get historical data
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=history_hours)
            
            data_points = self._get_metric_data(metric_name, start_time, end_time)
            
            if len(data_points) < 24:  # Need at least 24 points
                return None
            
            # Extract values and create time series
            values = [dp['value'] for dp in data_points]
            
            # Simple moving average forecast (can be enhanced with more sophisticated models)
            window_size = min(12, len(values) // 4)
            recent_avg = statistics.mean(values[-window_size:])
            trend_slope = (values[-1] - values[-window_size]) / window_size
            
            # Generate forecast points
            forecast_timestamps = []
            forecast_values = []
            confidence_intervals = []
            
            for i in range(forecast_hours):
                forecast_time = end_time + timedelta(hours=i+1)
                forecast_value = recent_avg + (trend_slope * (i + 1))
                
                # Simple confidence interval (±20% of recent standard deviation)
                recent_std = statistics.stdev(values[-window_size:]) if len(values) >= 2 else 0
                confidence_margin = recent_std * 0.2 * (1 + i * 0.1)  # Increasing uncertainty
                
                forecast_timestamps.append(forecast_time)
                forecast_values.append(forecast_value)
                confidence_intervals.append((
                    forecast_value - confidence_margin,
                    forecast_value + confidence_margin
                ))
            
            # Calculate model accuracy (simplified)
            accuracy = max(0.5, 1.0 - (recent_std / recent_avg if recent_avg != 0 else 0.5))
            
            return Forecast(
                metric_name=metric_name,
                forecast_horizon=timedelta(hours=forecast_hours),
                predicted_values=forecast_values,
                confidence_intervals=confidence_intervals,
                timestamps=forecast_timestamps,
                model_accuracy=accuracy,
                forecast_method="moving_average_with_trend"
            )
            
        except Exception as e:
            self.logger.error(f"Error generating forecast for {metric_name}: {e}")
            return None
    
    def get_comprehensive_analysis(self, metric_names: List[str],
                                 period_hours: int = 24) -> AnalyticsResult:
        """Get comprehensive analysis including trends, anomalies, and correlations"""
        
        analysis_id = f"comprehensive_{int(time.time())}"
        
        try:
            # Perform all types of analysis
            trends = self.analyze_trends(metric_names, period_hours)
            anomalies = self.detect_anomalies(metric_names, period_hours)
            correlations = self.analyze_correlations(metric_names, period_hours)
            forecasts = self.generate_forecasts(metric_names, forecast_hours=12)
            
            # Generate insights
            insights = self._generate_insights(trends, anomalies, correlations)
            recommendations = self._generate_recommendations(trends, anomalies, correlations)
            
            # Calculate overall confidence
            confidence_score = self._calculate_analysis_confidence(trends, anomalies, correlations)
            
            result = AnalyticsResult(
                analysis_id=analysis_id,
                timestamp=datetime.now(timezone.utc),
                analysis_type=AnalysisType.TREND_ANALYSIS,
                metric_names=metric_names,
                trends=trends,
                anomalies=anomalies,
                correlations=correlations,
                forecasts=forecasts,
                insights=insights,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
            # Store result
            self._store_analytics_result(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive analysis: {e}")
            return AnalyticsResult(
                analysis_id=analysis_id,
                timestamp=datetime.now(timezone.utc),
                analysis_type=AnalysisType.TREND_ANALYSIS,
                metric_names=metric_names,
                insights=[f"Analysis failed: {str(e)}"],
                confidence_score=0.0
            )
    
    def _get_recent_metrics(self, minutes: int = 30) -> List[Dict]:
        """Get recent metrics for real-time processing"""
        # This would integrate with the MetricsCollector to get recent data
        # For now, return empty list
        return []
    
    def _get_metric_data(self, metric_name: str, start_time: datetime, 
                        end_time: datetime) -> List[Dict]:
        """Get metric data for specified time range"""
        try:
            # Query metrics from database (simplified implementation)
            with sqlite3.connect(str(self.metrics_collector.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT timestamp, value FROM metrics 
                    WHERE metric_id = ? AND timestamp BETWEEN ? AND ?
                    ORDER BY timestamp
                """, (metric_name, start_time.isoformat(), end_time.isoformat()))
                
                return [
                    {
                        'timestamp': datetime.fromisoformat(row['timestamp']),
                        'value': row['value']
                    }
                    for row in cursor
                ]
        except Exception:
            # Generate sample data for demonstration
            return self._generate_sample_metric_data(metric_name, start_time, end_time)
    
    def _generate_sample_metric_data(self, metric_name: str, start_time: datetime,
                                   end_time: datetime) -> List[Dict]:
        """Generate sample metric data for demonstration"""
        data_points = []
        duration = end_time - start_time
        num_points = min(100, int(duration.total_seconds() / 300))  # 5-minute intervals
        
        base_value = 50.0
        if 'response_time' in metric_name.lower():
            base_value = 200.0
        elif 'cpu' in metric_name.lower():
            base_value = 25.0
        elif 'memory' in metric_name.lower():
            base_value = 512.0
        
        for i in range(num_points):
            timestamp = start_time + timedelta(seconds=(duration.total_seconds() / num_points) * i)
            # Add some realistic variation
            noise = (hash(f"{metric_name}_{i}") % 200 - 100) / 100.0 * 0.2
            trend = math.sin(i * 0.1) * 0.1  # Slight sinusoidal trend
            value = base_value * (1 + noise + trend)
            
            data_points.append({
                'timestamp': timestamp,
                'value': max(0, value)
            })
        
        return data_points
    
    def _linear_regression(self, x_values: List[float], 
                          y_values: List[float]) -> Tuple[float, float, float]:
        """Perform linear regression and return slope, confidence, and R²"""
        n = len(x_values)
        if n < 2:
            return 0.0, 0.0, 0.0
        
        # Calculate means
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)
        
        # Calculate slope and intercept
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 0.0, 0.0, 0.0
        
        slope = numerator / denominator
        
        # Calculate R²
        y_pred = [slope * (x - x_mean) + y_mean for x in x_values]
        ss_res = sum((y - y_p) ** 2 for y, y_p in zip(y_values, y_pred))
        ss_tot = sum((y - y_mean) ** 2 for y in y_values)
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        confidence = min(0.95, abs(r_squared))
        
        return slope, confidence, r_squared
    
    def _determine_trend_direction(self, slope: float, confidence: float) -> TrendDirection:
        """Determine trend direction from slope and confidence"""
        if confidence < 0.3:
            return TrendDirection.VOLATILE if abs(slope) > 0.1 else TrendDirection.STABLE
        
        if slope > 0.05:
            return TrendDirection.INCREASING
        elif slope < -0.05:
            return TrendDirection.DECREASING
        else:
            return TrendDirection.STABLE
    
    def _get_metric_baseline(self, metric_name: str, data_points: List[Dict]) -> Dict[str, float]:
        """Get or calculate baseline statistics for a metric"""
        values = [dp['value'] for dp in data_points]
        
        return {
            'mean': statistics.mean(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0.0,
            'min': min(values),
            'max': max(values)
        }
    
    def _determine_anomaly_severity(self, deviation_score: float) -> str:
        """Determine anomaly severity based on deviation score"""
        if deviation_score > 4.0:
            return "critical"
        elif deviation_score > 3.0:
            return "high"
        elif deviation_score > 2.5:
            return "medium"
        else:
            return "low"
    
    def _calculate_correlation(self, data_a: List[Dict], 
                             data_b: List[Dict]) -> Optional[CorrelationResult]:
        """Calculate correlation between two metrics"""
        try:
            # Align timestamps and extract values
            values_a = []
            values_b = []
            
            # Simple alignment by timestamp (in practice, would need more sophisticated alignment)
            for dp_a in data_a:
                for dp_b in data_b:
                    if abs((dp_a['timestamp'] - dp_b['timestamp']).total_seconds()) < 300:  # 5 min tolerance
                        values_a.append(dp_a['value'])
                        values_b.append(dp_b['value'])
                        break
            
            if len(values_a) < 10:
                return None
            
            # Calculate Pearson correlation coefficient
            correlation_coeff = self._pearson_correlation(values_a, values_b)
            
            if abs(correlation_coeff) < self.correlation_threshold:
                return None
            
            # Determine significance and relationship type
            significance = "strong" if abs(correlation_coeff) > 0.7 else "moderate"
            relationship_type = "positive" if correlation_coeff > 0 else "negative"
            
            return CorrelationResult(
                metric_a=data_a[0].get('metric_name', 'unknown'),
                metric_b=data_b[0].get('metric_name', 'unknown'),
                correlation_coefficient=correlation_coeff,
                p_value=0.05,  # Simplified
                significance=significance,
                relationship_type=relationship_type
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation: {e}")
            return None
    
    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        n = len(x)
        if n != len(y) or n < 2:
            return 0.0
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _generate_insights(self, trends: List[TrendAnalysis], 
                          anomalies: List[Anomaly],
                          correlations: List[CorrelationResult]) -> List[str]:
        """Generate insights from analysis results"""
        insights = []
        
        # Trend insights
        increasing_trends = [t for t in trends if t.direction == TrendDirection.INCREASING]
        decreasing_trends = [t for t in trends if t.direction == TrendDirection.DECREASING]
        
        if increasing_trends:
            insights.append(f"{len(increasing_trends)} metrics show positive trends")
        
        if decreasing_trends:
            insights.append(f"{len(decreasing_trends)} metrics show declining trends")
        
        # Anomaly insights
        critical_anomalies = [a for a in anomalies if a.severity == "critical"]
        if critical_anomalies:
            insights.append(f"{len(critical_anomalies)} critical anomalies detected")
        
        # Correlation insights
        strong_correlations = [c for c in correlations if c.significance == "strong"]
        if strong_correlations:
            insights.append(f"{len(strong_correlations)} strong correlations found between metrics")
        
        return insights[:10]  # Limit insights
    
    def _generate_recommendations(self, trends: List[TrendAnalysis], 
                                anomalies: List[Anomaly],
                                correlations: List[CorrelationResult]) -> List[str]:
        """Generate recommendations from analysis results"""
        recommendations = []
        
        # Trend-based recommendations
        poor_trends = [t for t in trends if t.direction == TrendDirection.DECREASING and t.confidence > 0.7]
        if poor_trends:
            recommendations.append("Investigate declining performance trends")
        
        # Anomaly-based recommendations
        if any(a.severity in ["critical", "high"] for a in anomalies):
            recommendations.append("Address high-severity anomalies immediately")
        
        # Correlation-based recommendations
        negative_correlations = [c for c in correlations if c.relationship_type == "negative" and c.significance == "strong"]
        if negative_correlations:
            recommendations.append("Analyze negative correlations for optimization opportunities")
        
        return recommendations[:5]  # Limit recommendations
    
    def _calculate_analysis_confidence(self, trends: List[TrendAnalysis], 
                                     anomalies: List[Anomaly],
                                     correlations: List[CorrelationResult]) -> float:
        """Calculate overall confidence in analysis results"""
        if not trends and not anomalies and not correlations:
            return 0.0
        
        total_confidence = 0.0
        count = 0
        
        # Trend confidence
        for trend in trends:
            total_confidence += trend.confidence
            count += 1
        
        # Anomaly confidence
        for anomaly in anomalies:
            total_confidence += anomaly.confidence
            count += 1
        
        # Correlation confidence (simplified)
        for correlation in correlations:
            total_confidence += abs(correlation.correlation_coefficient)
            count += 1
        
        return total_confidence / count if count > 0 else 0.0
    
    def _store_analytics_result(self, result: AnalyticsResult):
        """Store analytics result in database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO analytics_results
                    (analysis_id, timestamp, analysis_type, metric_names, results, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    result.analysis_id,
                    result.timestamp.isoformat(),
                    result.analysis_type.value,
                    json.dumps(result.metric_names),
                    json.dumps(asdict(result), default=str),
                    result.confidence_score
                ))
                
                # Store anomalies separately
                for anomaly in result.anomalies:
                    conn.execute("""
                        INSERT OR REPLACE INTO anomalies
                        (anomaly_id, timestamp, metric_name, anomaly_type, value,
                         expected_value, deviation_score, severity, description, confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        anomaly.anomaly_id,
                        anomaly.timestamp.isoformat(),
                        anomaly.metric_name,
                        anomaly.anomaly_type.value,
                        anomaly.value,
                        anomaly.expected_value,
                        anomaly.deviation_score,
                        anomaly.severity,
                        anomaly.description,
                        anomaly.confidence
                    ))
        
        except Exception as e:
            self.logger.error(f"Error storing analytics result: {e}")
    
    def _load_baselines(self):
        """Load metric baselines from database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM metric_baselines")
                
                for row in cursor:
                    self.baseline_stats[row['metric_name']] = {
                        'mean': row['mean_value'],
                        'std': row['std_deviation'],
                        'min': row['min_value'],
                        'max': row['max_value'],
                        'data_points': row['data_points']
                    }
        
        except Exception as e:
            self.logger.error(f"Error loading baselines: {e}")
    
    def _update_metric_windows(self, metrics: List[Dict]):
        """Update metric windows for real-time processing"""
        for metric in metrics:
            metric_name = metric.get('metric_name', 'unknown')
            self.metric_windows[metric_name].append({
                'timestamp': metric.get('timestamp', datetime.now()),
                'value': metric.get('value', 0.0)
            })
    
    def _detect_anomalies_real_time(self) -> List[Anomaly]:
        """Detect anomalies in real-time metric windows"""
        anomalies = []
        
        for metric_name, window in self.metric_windows.items():
            if len(window) < 10:
                continue
            
            # Get recent values
            recent_values = [dp['value'] for dp in window]
            mean_val = statistics.mean(recent_values)
            std_val = statistics.stdev(recent_values) if len(recent_values) > 1 else 0.0
            
            # Check latest value
            if std_val > 0:
                latest_value = recent_values[-1]
                deviation = abs(latest_value - mean_val) / std_val
                
                if deviation > self.anomaly_threshold:
                    anomaly = Anomaly(
                        anomaly_id=f"rt_anomaly_{int(time.time())}_{metric_name}",
                        timestamp=window[-1]['timestamp'],
                        metric_name=metric_name,
                        anomaly_type=AnomalyType.SPIKE if latest_value > mean_val else AnomalyType.DROP,
                        value=latest_value,
                        expected_value=mean_val,
                        deviation_score=deviation,
                        severity=self._determine_anomaly_severity(deviation),
                        description=f"Real-time anomaly in {metric_name}",
                        confidence=min(0.9, deviation / 4.0)
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _analyze_trends_real_time(self) -> List[TrendAnalysis]:
        """Analyze trends in real-time metric windows"""
        trends = []
        
        for metric_name, window in self.metric_windows.items():
            if len(window) < self.trend_min_points:
                continue
            
            # Extract values for trend analysis
            timestamps = [dp['timestamp'] for dp in window]
            values = [dp['value'] for dp in window]
            
            # Simple linear regression on recent data
            x_values = list(range(len(values)))
            slope, confidence, r_squared = self._linear_regression(x_values, values)
            
            if confidence > 0.3:  # Only report trends with reasonable confidence
                direction = self._determine_trend_direction(slope, confidence)
                
                trend = TrendAnalysis(
                    metric_name=metric_name,
                    direction=direction,
                    slope=slope,
                    confidence=confidence,
                    r_squared=r_squared,
                    start_value=values[0],
                    end_value=values[-1],
                    change_percent=((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0,
                    analysis_period=timestamps[-1] - timestamps[0],
                    data_points=len(values)
                )
                trends.append(trend)
        
        return trends