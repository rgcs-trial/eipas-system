"""
Analytics & Intelligence Dashboard

Comprehensive analytics system for productivity and performance monitoring,
trend analysis, business intelligence, and ROI calculation.
"""

from .metrics_collector import (
    MetricsCollector, MetricType, MetricPoint, ProductivityMetrics,
    PerformanceMetrics, UsageMetrics, QualityMetrics
)

from .dashboard_engine import (
    DashboardEngine, ChartType, TimePeriod, ChartSeries, ChartConfiguration,
    DashboardWidget, DashboardLayout
)

from .analytics_engine import (
    AnalyticsEngine, AnalysisType, TrendDirection, AnomalyType,
    TrendAnalysis, Anomaly, CorrelationResult, Forecast, AnalyticsResult
)

from .insights_generator import (
    InsightsGenerator, Insight, InsightType, Recommendation, 
    RecommendationType, InsightReport
)

from .trend_analyzer import (
    TrendAnalyzer, PerformanceBottleneck, TrendForecast, 
    PerformanceProfile, BottleneckType, TrendType
)

from .roi_calculator import (
    ROICalculator, ROIMetricType, CostType, BenefitType,
    ROIBenchmark, CostItem, BenefitItem, ROIScenario, ROIResult
)

__all__ = [
    # Core classes
    'MetricsCollector', 'DashboardEngine', 'AnalyticsEngine',
    'InsightsGenerator', 'TrendAnalyzer', 'ROICalculator',
    
    # Data types and enums
    'MetricType', 'ChartType', 'TimePeriod', 'AnalysisType',
    'TrendDirection', 'AnomalyType', 'InsightType', 'RecommendationType',
    'BottleneckType', 'TrendType', 'ROIMetricType', 'CostType', 'BenefitType',
    
    # Data structures
    'MetricPoint', 'ProductivityMetrics', 'PerformanceMetrics',
    'UsageMetrics', 'QualityMetrics', 'ChartSeries', 'ChartConfiguration',
    'DashboardWidget', 'DashboardLayout', 'TrendAnalysis', 'Anomaly',
    'CorrelationResult', 'Forecast', 'AnalyticsResult', 'Insight',
    'Recommendation', 'InsightReport', 'PerformanceBottleneck',
    'TrendForecast', 'PerformanceProfile', 'ROIBenchmark',
    'CostItem', 'BenefitItem', 'ROIScenario', 'ROIResult'
]

__version__ = "1.0.0"
__author__ = "Claude Code Analytics Team"
__description__ = "Enterprise-grade analytics and intelligence dashboard for development productivity"