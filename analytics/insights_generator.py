"""
Productivity Insights Generator

Advanced system for generating actionable insights and recommendations from
productivity metrics, user behavior patterns, and performance analytics.
"""

import json
import math
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from enum import Enum
import logging
import statistics
from collections import defaultdict, Counter

from .metrics_collector import MetricsCollector, MetricType
from .analytics_engine import AnalyticsEngine, TrendAnalysis, Anomaly, CorrelationResult

class InsightCategory(Enum):
    """Categories of insights generated"""
    PRODUCTIVITY = "productivity"
    PERFORMANCE = "performance"
    BEHAVIOR = "behavior"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"
    COLLABORATION = "collaboration"
    LEARNING = "learning"
    OPTIMIZATION = "optimization"

class InsightPriority(Enum):
    """Priority levels for insights"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ActionType(Enum):
    """Types of recommended actions"""
    CONFIGURATION_CHANGE = "configuration_change"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    TOOL_ADOPTION = "tool_adoption"
    TRAINING = "training"
    POLICY_UPDATE = "policy_update"
    MONITORING = "monitoring"
    INVESTIGATION = "investigation"

@dataclass
class Insight:
    """Individual productivity insight"""
    insight_id: str
    title: str
    description: str
    category: InsightCategory
    priority: InsightPriority
    confidence: float
    impact_score: float
    evidence: List[str]
    metrics_involved: List[str]
    time_period: timedelta
    generated_at: datetime

@dataclass
class Recommendation:
    """Actionable recommendation"""
    recommendation_id: str
    insight_id: str
    title: str
    description: str
    action_type: ActionType
    priority: InsightPriority
    effort_level: str  # low, medium, high
    expected_impact: str  # low, medium, high
    implementation_steps: List[str]
    success_metrics: List[str]
    estimated_time_to_implement: str
    potential_roi: Optional[float] = None

@dataclass
class InsightReport:
    """Comprehensive insights report"""
    report_id: str
    generated_at: datetime
    time_period: timedelta
    insights: List[Insight]
    recommendations: List[Recommendation]
    summary: str
    key_findings: List[str]
    priority_actions: List[str]
    overall_productivity_score: float
    trend_indicators: Dict[str, str]

class InsightsGenerator:
    """Advanced productivity insights generation engine"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 analytics_engine: Optional[AnalyticsEngine] = None):
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
        
        # Insight generation rules and patterns
        self.insight_rules = self._initialize_insight_rules()
        self.benchmark_thresholds = self._initialize_benchmarks()
        self.optimization_patterns = self._initialize_optimization_patterns()
        
        # Historical insights for learning
        self.insight_history = []
    
    def _initialize_insight_rules(self) -> Dict[str, Dict]:
        """Initialize rules for insight generation"""
        return {
            'productivity_decline': {
                'condition': lambda trends: any(
                    t.direction.value == 'decreasing' and t.change_percent < -10 and t.confidence > 0.7
                    for t in trends if 'productivity' in t.metric_name.lower()
                ),
                'category': InsightCategory.PRODUCTIVITY,
                'priority': InsightPriority.HIGH,
                'title': "Productivity Decline Detected",
                'template': "Productivity has declined by {change_percent:.1f}% over the past {period}. This requires immediate attention."
            },
            'performance_bottleneck': {
                'condition': lambda analytics: any(
                    a.anomaly_type.value in ['spike', 'outlier'] and a.severity in ['high', 'critical']
                    for a in analytics.get('anomalies', [])
                    if 'response_time' in a.metric_name.lower() or 'latency' in a.metric_name.lower()
                ),
                'category': InsightCategory.PERFORMANCE,
                'priority': InsightPriority.CRITICAL,
                'title': "Performance Bottleneck Identified",
                'template': "Critical performance issues detected in response times. Immediate optimization needed."
            },
            'tool_underutilization': {
                'condition': lambda usage_data: self._check_tool_underutilization(usage_data),
                'category': InsightCategory.EFFICIENCY,
                'priority': InsightPriority.MEDIUM,
                'title': "Tools Being Underutilized",
                'template': "Several powerful tools are being underused, representing missed productivity opportunities."
            },
            'positive_correlation_opportunity': {
                'condition': lambda correlations: any(
                    c.correlation_coefficient > 0.7 and c.significance == 'strong'
                    for c in correlations if c.relationship_type == 'positive'
                ),
                'category': InsightCategory.OPTIMIZATION,
                'priority': InsightPriority.MEDIUM,
                'title': "Optimization Opportunity Identified",
                'template': "Strong positive correlations found between metrics suggest optimization opportunities."
            },
            'workflow_efficiency_gain': {
                'condition': lambda session_data: self._check_workflow_efficiency(session_data),
                'category': InsightCategory.EFFICIENCY,
                'priority': InsightPriority.MEDIUM,
                'title': "Workflow Efficiency Opportunity",
                'template': "Analysis suggests specific workflow optimizations could improve efficiency by 15-25%."
            },
            'learning_curve_plateau': {
                'condition': lambda productivity_trend: self._check_learning_plateau(productivity_trend),
                'category': InsightCategory.LEARNING,
                'priority': InsightPriority.MEDIUM,
                'title': "Learning Plateau Detected",
                'template': "Productivity improvement has plateaued, suggesting need for advanced training or new challenges."
            }
        }
    
    def _initialize_benchmarks(self) -> Dict[str, Dict]:
        """Initialize benchmark thresholds for comparison"""
        return {
            'productivity_score': {'excellent': 8.0, 'good': 6.0, 'fair': 4.0, 'poor': 2.0},
            'response_time_ms': {'excellent': 200, 'good': 500, 'fair': 1000, 'poor': 2000},
            'session_duration_minutes': {'optimal_min': 25, 'optimal_max': 90, 'too_short': 15, 'too_long': 180},
            'tools_per_session': {'excellent': 5, 'good': 3, 'minimal': 2, 'single_tool': 1},
            'error_rate_percent': {'excellent': 1.0, 'good': 3.0, 'acceptable': 5.0, 'problematic': 10.0},
            'satisfaction_rating': {'excellent': 8.0, 'good': 6.0, 'fair': 4.0, 'poor': 2.0}
        }
    
    def _initialize_optimization_patterns(self) -> Dict[str, Dict]:
        """Initialize optimization patterns and templates"""
        return {
            'automation_opportunity': {
                'pattern': 'repetitive_commands',
                'threshold': 0.7,  # 70% repetition rate
                'recommendation': "Create custom commands or hooks to automate repetitive tasks",
                'expected_impact': 'high',
                'effort': 'medium'
            },
            'tool_consolidation': {
                'pattern': 'tool_fragmentation',
                'threshold': 8,  # More than 8 different tools
                'recommendation': "Consolidate to fewer, more powerful tools for better focus",
                'expected_impact': 'medium',
                'effort': 'low'
            },
            'workflow_streamlining': {
                'pattern': 'context_switching',
                'threshold': 0.6,  # High context switching
                'recommendation': "Optimize workflow to reduce context switching",
                'expected_impact': 'high',
                'effort': 'medium'
            },
            'skill_development': {
                'pattern': 'plateau_productivity',
                'threshold': 0.05,  # Less than 5% improvement
                'recommendation': "Invest in advanced training to break through productivity plateau",
                'expected_impact': 'high',
                'effort': 'high'
            }
        }
    
    def generate_insights_report(self, period_hours: int = 168) -> InsightReport:
        """Generate comprehensive insights report"""
        
        report_id = f"insights_{int(datetime.now().timestamp())}"
        
        try:
            # Gather data for analysis
            productivity_summary = self.metrics_collector.get_productivity_summary(days=period_hours//24)
            performance_analytics = self.metrics_collector.get_performance_analytics(hours=period_hours)
            usage_patterns = self.metrics_collector.get_usage_patterns(days=period_hours//24)
            
            # Get comprehensive analytics
            key_metrics = ['productivity.session_score', 'performance.response_time', 'usage.tool_used']
            analytics_result = self.analytics_engine.get_comprehensive_analysis(key_metrics, period_hours)
            
            # Generate insights
            insights = self._generate_insights(
                productivity_summary, performance_analytics, usage_patterns, analytics_result
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(insights, analytics_result)
            
            # Calculate overall scores and trends
            overall_score = self._calculate_overall_productivity_score(productivity_summary, performance_analytics)
            trend_indicators = self._generate_trend_indicators(analytics_result.trends)
            
            # Generate summary and key findings
            summary = self._generate_report_summary(insights, recommendations, overall_score)
            key_findings = self._extract_key_findings(insights)
            priority_actions = self._extract_priority_actions(recommendations)
            
            report = InsightReport(
                report_id=report_id,
                generated_at=datetime.now(timezone.utc),
                time_period=timedelta(hours=period_hours),
                insights=insights,
                recommendations=recommendations,
                summary=summary,
                key_findings=key_findings,
                priority_actions=priority_actions,
                overall_productivity_score=overall_score,
                trend_indicators=trend_indicators
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating insights report: {e}")
            return InsightReport(
                report_id=report_id,
                generated_at=datetime.now(timezone.utc),
                time_period=timedelta(hours=period_hours),
                insights=[],
                recommendations=[],
                summary=f"Report generation failed: {str(e)}",
                key_findings=["Unable to generate insights due to error"],
                priority_actions=["Investigate report generation failure"],
                overall_productivity_score=0.0,
                trend_indicators={}
            )
    
    def _generate_insights(self, productivity_summary: Dict, performance_analytics: Dict,
                          usage_patterns: Dict, analytics_result) -> List[Insight]:
        """Generate insights from collected data"""
        insights = []
        
        try:
            # Check each insight rule
            for rule_name, rule in self.insight_rules.items():
                try:
                    if rule_name == 'productivity_decline':
                        if rule['condition'](analytics_result.trends):
                            insight = self._create_productivity_decline_insight(analytics_result.trends, rule)
                            if insight:
                                insights.append(insight)
                    
                    elif rule_name == 'performance_bottleneck':
                        if rule['condition']({'anomalies': analytics_result.anomalies}):
                            insight = self._create_performance_bottleneck_insight(analytics_result.anomalies, rule)
                            if insight:
                                insights.append(insight)
                    
                    elif rule_name == 'tool_underutilization':
                        if rule['condition'](usage_patterns):
                            insight = self._create_tool_underutilization_insight(usage_patterns, rule)
                            if insight:
                                insights.append(insight)
                    
                    elif rule_name == 'positive_correlation_opportunity':
                        if rule['condition'](analytics_result.correlations):
                            insight = self._create_correlation_opportunity_insight(analytics_result.correlations, rule)
                            if insight:
                                insights.append(insight)
                    
                    elif rule_name == 'workflow_efficiency_gain':
                        if rule['condition'](productivity_summary):
                            insight = self._create_workflow_efficiency_insight(productivity_summary, rule)
                            if insight:
                                insights.append(insight)
                    
                    elif rule_name == 'learning_curve_plateau':
                        if rule['condition'](analytics_result.trends):
                            insight = self._create_learning_plateau_insight(analytics_result.trends, rule)
                            if insight:
                                insights.append(insight)
                
                except Exception as e:
                    self.logger.error(f"Error processing rule {rule_name}: {e}")
                    continue
            
            # Generate additional data-driven insights
            additional_insights = self._generate_data_driven_insights(
                productivity_summary, performance_analytics, usage_patterns
            )
            insights.extend(additional_insights)
            
        except Exception as e:
            self.logger.error(f"Error in insight generation: {e}")
        
        return insights[:20]  # Limit to top 20 insights
    
    def _create_productivity_decline_insight(self, trends: List[TrendAnalysis], rule: Dict) -> Optional[Insight]:
        """Create insight for productivity decline"""
        productivity_trends = [t for t in trends if 'productivity' in t.metric_name.lower()]
        declining_trends = [t for t in productivity_trends if t.direction.value == 'decreasing']
        
        if not declining_trends:
            return None
        
        worst_trend = min(declining_trends, key=lambda x: x.change_percent)
        
        return Insight(
            insight_id=f"prod_decline_{int(datetime.now().timestamp())}",
            title=rule['title'],
            description=rule['template'].format(
                change_percent=abs(worst_trend.change_percent),
                period=str(worst_trend.analysis_period)
            ),
            category=rule['category'],
            priority=rule['priority'],
            confidence=worst_trend.confidence,
            impact_score=min(1.0, abs(worst_trend.change_percent) / 20.0),
            evidence=[f"Trend analysis shows {worst_trend.change_percent:.1f}% decline",
                     f"Confidence: {worst_trend.confidence:.2f}",
                     f"Data points: {worst_trend.data_points}"],
            metrics_involved=[worst_trend.metric_name],
            time_period=worst_trend.analysis_period,
            generated_at=datetime.now(timezone.utc)
        )
    
    def _create_performance_bottleneck_insight(self, anomalies: List[Anomaly], rule: Dict) -> Optional[Insight]:
        """Create insight for performance bottlenecks"""
        perf_anomalies = [a for a in anomalies if 'response_time' in a.metric_name.lower() or 'latency' in a.metric_name.lower()]
        critical_anomalies = [a for a in perf_anomalies if a.severity in ['high', 'critical']]
        
        if not critical_anomalies:
            return None
        
        worst_anomaly = max(critical_anomalies, key=lambda x: x.deviation_score)
        
        return Insight(
            insight_id=f"perf_bottleneck_{int(datetime.now().timestamp())}",
            title=rule['title'],
            description=rule['template'],
            category=rule['category'],
            priority=rule['priority'],
            confidence=worst_anomaly.confidence,
            impact_score=min(1.0, worst_anomaly.deviation_score / 5.0),
            evidence=[f"Anomaly detected: {worst_anomaly.description}",
                     f"Deviation: {worst_anomaly.deviation_score:.2f} standard deviations",
                     f"Severity: {worst_anomaly.severity}"],
            metrics_involved=[worst_anomaly.metric_name],
            time_period=timedelta(hours=1),  # Anomalies are point-in-time
            generated_at=datetime.now(timezone.utc)
        )
    
    def _create_tool_underutilization_insight(self, usage_patterns: Dict, rule: Dict) -> Optional[Insight]:
        """Create insight for tool underutilization"""
        most_used_tools = usage_patterns.get('most_used_tools', [])
        
        if len(most_used_tools) < 3:
            return None
        
        # Check if distribution is very skewed (indicates underutilization)
        tool_counts = [tool['count'] for tool in most_used_tools[:5]]
        if not tool_counts:
            return None
            
        max_count = max(tool_counts)
        underutilized_tools = [tool for tool in most_used_tools[2:] if tool['count'] < max_count * 0.2]
        
        if len(underutilized_tools) < 2:
            return None
        
        return Insight(
            insight_id=f"tool_underutil_{int(datetime.now().timestamp())}",
            title=rule['title'],
            description=rule['template'],
            category=rule['category'],
            priority=rule['priority'],
            confidence=0.8,
            impact_score=0.6,
            evidence=[f"Tool usage highly skewed to top tools",
                     f"{len(underutilized_tools)} tools used less than 20% of max frequency",
                     f"Top tool used {max_count} times vs bottom tools averaging {statistics.mean([t['count'] for t in underutilized_tools]):.1f}"],
            metrics_involved=['usage.tool_used'],
            time_period=timedelta(days=7),
            generated_at=datetime.now(timezone.utc)
        )
    
    def _create_correlation_opportunity_insight(self, correlations: List[CorrelationResult], rule: Dict) -> Optional[Insight]:
        """Create insight for correlation-based optimization opportunities"""
        strong_positive_corr = [c for c in correlations 
                               if c.correlation_coefficient > 0.7 and c.relationship_type == 'positive']
        
        if not strong_positive_corr:
            return None
        
        best_correlation = max(strong_positive_corr, key=lambda x: abs(x.correlation_coefficient))
        
        return Insight(
            insight_id=f"corr_opportunity_{int(datetime.now().timestamp())}",
            title=rule['title'],
            description=rule['template'],
            category=rule['category'],
            priority=rule['priority'],
            confidence=0.75,
            impact_score=0.7,
            evidence=[f"Strong correlation found: {best_correlation.metric_a} ↔ {best_correlation.metric_b}",
                     f"Correlation coefficient: {best_correlation.correlation_coefficient:.3f}",
                     f"Relationship type: {best_correlation.relationship_type}"],
            metrics_involved=[best_correlation.metric_a, best_correlation.metric_b],
            time_period=timedelta(hours=24),
            generated_at=datetime.now(timezone.utc)
        )
    
    def _create_workflow_efficiency_insight(self, productivity_summary: Dict, rule: Dict) -> Optional[Insight]:
        """Create insight for workflow efficiency opportunities"""
        avg_duration = productivity_summary.get('avg_session_duration', 0)
        total_sessions = productivity_summary.get('total_sessions', 0)
        
        if avg_duration == 0 or total_sessions < 5:
            return None
        
        # Check for efficiency opportunities
        efficiency_issues = []
        if avg_duration < 25:
            efficiency_issues.append("Sessions too short for deep work")
        elif avg_duration > 120:
            efficiency_issues.append("Sessions too long without breaks")
        
        if not efficiency_issues:
            return None
        
        return Insight(
            insight_id=f"workflow_efficiency_{int(datetime.now().timestamp())}",
            title=rule['title'],
            description=rule['template'],
            category=rule['category'],
            priority=rule['priority'],
            confidence=0.7,
            impact_score=0.65,
            evidence=[f"Average session duration: {avg_duration:.1f} minutes"] + efficiency_issues,
            metrics_involved=['session.duration'],
            time_period=timedelta(days=7),
            generated_at=datetime.now(timezone.utc)
        )
    
    def _create_learning_plateau_insight(self, trends: List[TrendAnalysis], rule: Dict) -> Optional[Insight]:
        """Create insight for learning plateau detection"""
        productivity_trends = [t for t in trends if 'productivity' in t.metric_name.lower()]
        stable_trends = [t for t in productivity_trends if t.direction.value == 'stable' and abs(t.change_percent) < 2]
        
        if not stable_trends:
            return None
        
        return Insight(
            insight_id=f"learning_plateau_{int(datetime.now().timestamp())}",
            title=rule['title'],
            description=rule['template'],
            category=rule['category'],
            priority=rule['priority'],
            confidence=0.6,
            impact_score=0.5,
            evidence=["Productivity improvement has stagnated",
                     f"Change in productivity: {stable_trends[0].change_percent:.1f}%",
                     "Indicates need for new challenges or training"],
            metrics_involved=[trend.metric_name for trend in stable_trends],
            time_period=stable_trends[0].analysis_period,
            generated_at=datetime.now(timezone.utc)
        )
    
    def _generate_data_driven_insights(self, productivity_summary: Dict, 
                                     performance_analytics: Dict, usage_patterns: Dict) -> List[Insight]:
        """Generate additional insights from data patterns"""
        insights = []
        
        try:
            # Session duration insights
            avg_duration = productivity_summary.get('avg_session_duration', 0)
            if avg_duration > 0:
                if avg_duration < self.benchmark_thresholds['session_duration_minutes']['too_short']:
                    insights.append(Insight(
                        insight_id=f"short_sessions_{int(datetime.now().timestamp())}",
                        title="Sessions Too Short for Optimal Productivity",
                        description=f"Average session duration of {avg_duration:.1f} minutes is below optimal range",
                        category=InsightCategory.EFFICIENCY,
                        priority=InsightPriority.MEDIUM,
                        confidence=0.8,
                        impact_score=0.6,
                        evidence=[f"Average: {avg_duration:.1f} min", f"Optimal: {self.benchmark_thresholds['session_duration_minutes']['optimal_min']}-{self.benchmark_thresholds['session_duration_minutes']['optimal_max']} min"],
                        metrics_involved=['session.duration'],
                        time_period=timedelta(days=7),
                        generated_at=datetime.now(timezone.utc)
                    ))
            
            # Performance insights
            avg_response = performance_analytics.get('response_times', {}).get('avg', 0)
            if avg_response > self.benchmark_thresholds['response_time_ms']['poor']:
                insights.append(Insight(
                    insight_id=f"slow_response_{int(datetime.now().timestamp())}",
                    title="Response Times Above Acceptable Threshold",
                    description=f"Average response time of {avg_response:.0f}ms impacts user experience",
                    category=InsightCategory.PERFORMANCE,
                    priority=InsightPriority.HIGH,
                    confidence=0.9,
                    impact_score=0.8,
                    evidence=[f"Current: {avg_response:.0f}ms", f"Target: <{self.benchmark_thresholds['response_time_ms']['good']}ms"],
                    metrics_involved=['performance.response_time'],
                    time_period=timedelta(hours=24),
                    generated_at=datetime.now(timezone.utc)
                ))
            
            # Tool diversity insights
            tool_count = len(usage_patterns.get('most_used_tools', []))
            if tool_count == 1:
                insights.append(Insight(
                    insight_id=f"single_tool_{int(datetime.now().timestamp())}",
                    title="Limited Tool Utilization",
                    description="Using only one tool may limit productivity potential",
                    category=InsightCategory.EFFICIENCY,
                    priority=InsightPriority.LOW,
                    confidence=0.7,
                    impact_score=0.4,
                    evidence=[f"Only {tool_count} tool being used", "Consider exploring additional tools"],
                    metrics_involved=['usage.tool_used'],
                    time_period=timedelta(days=7),
                    generated_at=datetime.now(timezone.utc)
                ))
        
        except Exception as e:
            self.logger.error(f"Error generating data-driven insights: {e}")
        
        return insights
    
    def _generate_recommendations(self, insights: List[Insight], analytics_result) -> List[Recommendation]:
        """Generate actionable recommendations from insights"""
        recommendations = []
        
        try:
            for insight in insights:
                # Generate recommendations based on insight category and content
                if insight.category == InsightCategory.PRODUCTIVITY and insight.priority in [InsightPriority.HIGH, InsightPriority.CRITICAL]:
                    recommendations.extend(self._create_productivity_recommendations(insight))
                
                elif insight.category == InsightCategory.PERFORMANCE and insight.priority in [InsightPriority.HIGH, InsightPriority.CRITICAL]:
                    recommendations.extend(self._create_performance_recommendations(insight))
                
                elif insight.category == InsightCategory.EFFICIENCY:
                    recommendations.extend(self._create_efficiency_recommendations(insight))
                
                elif insight.category == InsightCategory.LEARNING:
                    recommendations.extend(self._create_learning_recommendations(insight))
            
            # Generate optimization recommendations from patterns
            optimization_recommendations = self._create_optimization_recommendations(analytics_result)
            recommendations.extend(optimization_recommendations)
        
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
        
        return recommendations[:15]  # Limit to top 15 recommendations
    
    def _create_productivity_recommendations(self, insight: Insight) -> List[Recommendation]:
        """Create recommendations for productivity insights"""
        recommendations = []
        
        if "decline" in insight.title.lower():
            recommendations.append(Recommendation(
                recommendation_id=f"prod_rec_{int(datetime.now().timestamp())}",
                insight_id=insight.insight_id,
                title="Investigate Productivity Decline Root Cause",
                description="Conduct detailed analysis to identify specific factors causing productivity decline",
                action_type=ActionType.INVESTIGATION,
                priority=InsightPriority.HIGH,
                effort_level="medium",
                expected_impact="high",
                implementation_steps=[
                    "Review recent configuration changes",
                    "Analyze user behavior patterns for anomalies",
                    "Check for system performance issues",
                    "Survey team for workflow challenges"
                ],
                success_metrics=["Productivity trend reversal", "Root cause identified", "Action plan created"],
                estimated_time_to_implement="2-3 days",
                potential_roi=0.25
            ))
        
        return recommendations
    
    def _create_performance_recommendations(self, insight: Insight) -> List[Recommendation]:
        """Create recommendations for performance insights"""
        recommendations = []
        
        if "bottleneck" in insight.title.lower() or "response time" in insight.description.lower():
            recommendations.append(Recommendation(
                recommendation_id=f"perf_rec_{int(datetime.now().timestamp())}",
                insight_id=insight.insight_id,
                title="Optimize System Performance",
                description="Implement performance optimizations to reduce response times and improve user experience",
                action_type=ActionType.CONFIGURATION_CHANGE,
                priority=InsightPriority.HIGH,
                effort_level="medium",
                expected_impact="high",
                implementation_steps=[
                    "Profile application performance",
                    "Identify bottleneck components",
                    "Implement caching strategies",
                    "Optimize database queries",
                    "Monitor improvement"
                ],
                success_metrics=["Response time reduction >30%", "User satisfaction improvement", "Error rate reduction"],
                estimated_time_to_implement="1-2 weeks",
                potential_roi=0.40
            ))
        
        return recommendations
    
    def _create_efficiency_recommendations(self, insight: Insight) -> List[Recommendation]:
        """Create recommendations for efficiency insights"""
        recommendations = []
        
        if "tool" in insight.title.lower():
            recommendations.append(Recommendation(
                recommendation_id=f"eff_rec_{int(datetime.now().timestamp())}",
                insight_id=insight.insight_id,
                title="Optimize Tool Usage and Training",
                description="Provide training on underutilized tools and optimize tool configuration for better adoption",
                action_type=ActionType.TOOL_ADOPTION,
                priority=InsightPriority.MEDIUM,
                effort_level="low",
                expected_impact="medium",
                implementation_steps=[
                    "Create tool usage guides",
                    "Conduct tool training sessions",
                    "Optimize tool configurations",
                    "Set up usage monitoring"
                ],
                success_metrics=["Increased tool diversity", "Improved productivity scores", "User feedback scores"],
                estimated_time_to_implement="1 week",
                potential_roi=0.15
            ))
        
        elif "session" in insight.title.lower():
            recommendations.append(Recommendation(
                recommendation_id=f"workflow_rec_{int(datetime.now().timestamp())}",
                insight_id=insight.insight_id,
                title="Optimize Work Session Structure",
                description="Implement guidelines for optimal session duration and break patterns",
                action_type=ActionType.WORKFLOW_OPTIMIZATION,
                priority=InsightPriority.MEDIUM,
                effort_level="low",
                expected_impact="medium",
                implementation_steps=[
                    "Establish session duration guidelines",
                    "Implement break reminders",
                    "Create focus time blocks",
                    "Monitor session effectiveness"
                ],
                success_metrics=["Optimal session duration achievement", "Productivity improvement", "User satisfaction"],
                estimated_time_to_implement="1 week",
                potential_roi=0.20
            ))
        
        return recommendations
    
    def _create_learning_recommendations(self, insight: Insight) -> List[Recommendation]:
        """Create recommendations for learning insights"""
        recommendations = []
        
        if "plateau" in insight.title.lower():
            recommendations.append(Recommendation(
                recommendation_id=f"learn_rec_{int(datetime.now().timestamp())}",
                insight_id=insight.insight_id,
                title="Break Through Learning Plateau",
                description="Introduce advanced training and new challenges to reignite productivity growth",
                action_type=ActionType.TRAINING,
                priority=InsightPriority.MEDIUM,
                effort_level="high",
                expected_impact="high",
                implementation_steps=[
                    "Assess current skill gaps",
                    "Design advanced training program",
                    "Introduce new challenges and projects",
                    "Provide mentoring opportunities",
                    "Track skill development progress"
                ],
                success_metrics=["Productivity growth resumption", "New skill acquisition", "Challenge completion rates"],
                estimated_time_to_implement="2-4 weeks",
                potential_roi=0.35
            ))
        
        return recommendations
    
    def _create_optimization_recommendations(self, analytics_result) -> List[Recommendation]:
        """Create general optimization recommendations"""
        recommendations = []
        
        # Check for automation opportunities
        if len(analytics_result.correlations) > 2:
            recommendations.append(Recommendation(
                recommendation_id=f"auto_rec_{int(datetime.now().timestamp())}",
                insight_id="correlation_analysis",
                title="Implement Workflow Automation",
                description="Create automated workflows based on identified correlations and patterns",
                action_type=ActionType.WORKFLOW_OPTIMIZATION,
                priority=InsightPriority.MEDIUM,
                effort_level="medium",
                expected_impact="high",
                implementation_steps=[
                    "Map correlated activities",
                    "Design automation workflows",
                    "Implement automation scripts",
                    "Test and validate automation",
                    "Deploy and monitor"
                ],
                success_metrics=["Reduced manual effort", "Increased consistency", "Time savings"],
                estimated_time_to_implement="2-3 weeks",
                potential_roi=0.30
            ))
        
        return recommendations
    
    def _calculate_overall_productivity_score(self, productivity_summary: Dict, 
                                            performance_analytics: Dict) -> float:
        """Calculate overall productivity score"""
        try:
            score_components = []
            
            # Productivity component
            avg_productivity = productivity_summary.get('avg_productivity_score', 5.0)
            if avg_productivity > 0:
                score_components.append(min(10.0, avg_productivity))
            
            # Performance component (inverse of response time)
            avg_response = performance_analytics.get('response_times', {}).get('avg', 500)
            perf_score = max(0, 10 - (avg_response / 200))  # Scale based on 200ms baseline
            score_components.append(perf_score)
            
            # Calculate weighted average
            if score_components:
                return statistics.mean(score_components)
            else:
                return 5.0  # Default neutral score
                
        except Exception as e:
            self.logger.error(f"Error calculating productivity score: {e}")
            return 5.0
    
    def _generate_trend_indicators(self, trends: List[TrendAnalysis]) -> Dict[str, str]:
        """Generate trend indicators for different categories"""
        indicators = {}
        
        try:
            # Group trends by category
            productivity_trends = [t for t in trends if 'productivity' in t.metric_name.lower()]
            performance_trends = [t for t in trends if 'response' in t.metric_name.lower() or 'cpu' in t.metric_name.lower()]
            
            # Productivity trend
            if productivity_trends:
                avg_change = statistics.mean([t.change_percent for t in productivity_trends])
                if avg_change > 5:
                    indicators['productivity'] = 'improving'
                elif avg_change < -5:
                    indicators['productivity'] = 'declining'
                else:
                    indicators['productivity'] = 'stable'
            
            # Performance trend
            if performance_trends:
                avg_change = statistics.mean([t.change_percent for t in performance_trends])
                # For performance metrics, negative change is often good (lower response time, CPU usage)
                if avg_change < -5:
                    indicators['performance'] = 'improving'
                elif avg_change > 5:
                    indicators['performance'] = 'declining'
                else:
                    indicators['performance'] = 'stable'
            
        except Exception as e:
            self.logger.error(f"Error generating trend indicators: {e}")
        
        return indicators
    
    def _generate_report_summary(self, insights: List[Insight], 
                               recommendations: List[Recommendation], overall_score: float) -> str:
        """Generate executive summary of insights report"""
        try:
            high_priority_insights = len([i for i in insights if i.priority in [InsightPriority.HIGH, InsightPriority.CRITICAL]])
            high_impact_recommendations = len([r for r in recommendations if r.expected_impact == 'high'])
            
            summary = f"""
Productivity Analysis Summary:
- Overall Productivity Score: {overall_score:.1f}/10
- {len(insights)} insights identified ({high_priority_insights} high priority)
- {len(recommendations)} recommendations generated ({high_impact_recommendations} high impact)

Key Focus Areas:
- {', '.join(set(i.category.value.title() for i in insights[:5]))}

Recommended Actions:
- {high_impact_recommendations} high-impact optimizations available
- Estimated ROI range: 15-40% productivity improvement
""".strip()
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return "Summary generation failed"
    
    def _extract_key_findings(self, insights: List[Insight]) -> List[str]:
        """Extract key findings from insights"""
        findings = []
        
        try:
            # Group by category and priority
            critical_insights = [i for i in insights if i.priority == InsightPriority.CRITICAL]
            high_insights = [i for i in insights if i.priority == InsightPriority.HIGH]
            
            for insight in (critical_insights + high_insights)[:5]:
                findings.append(f"{insight.category.value.title()}: {insight.title}")
            
        except Exception as e:
            self.logger.error(f"Error extracting key findings: {e}")
        
        return findings[:10]
    
    def _extract_priority_actions(self, recommendations: List[Recommendation]) -> List[str]:
        """Extract priority actions from recommendations"""
        actions = []
        
        try:
            priority_recs = sorted(recommendations, 
                                 key=lambda r: (r.priority.value, r.expected_impact), 
                                 reverse=True)
            
            for rec in priority_recs[:5]:
                actions.append(f"{rec.title} (Impact: {rec.expected_impact}, Effort: {rec.effort_level})")
        
        except Exception as e:
            self.logger.error(f"Error extracting priority actions: {e}")
        
        return actions
    
    # Helper methods for rule conditions
    def _check_tool_underutilization(self, usage_data: Dict) -> bool:
        """Check if tools are being underutilized"""
        tools = usage_data.get('most_used_tools', [])
        if len(tools) < 3:
            return False
        
        # Check if usage is very skewed
        counts = [tool['count'] for tool in tools[:5]]
        if not counts:
            return False
            
        max_count = max(counts)
        min_count = min(counts)
        
        return (max_count / min_count) > 5 if min_count > 0 else True
    
    def _check_workflow_efficiency(self, session_data: Dict) -> bool:
        """Check for workflow efficiency opportunities"""
        avg_duration = session_data.get('avg_session_duration', 0)
        return avg_duration < 25 or avg_duration > 120
    
    def _check_learning_plateau(self, trends: List[TrendAnalysis]) -> bool:
        """Check for learning plateau indicators"""
        productivity_trends = [t for t in trends if 'productivity' in t.metric_name.lower()]
        return any(t.direction.value == 'stable' and abs(t.change_percent) < 2 
                  for t in productivity_trends)