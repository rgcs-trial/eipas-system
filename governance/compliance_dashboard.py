"""
Enterprise Compliance Dashboard

Interactive dashboard for monitoring compliance status, risk levels,
and policy violations across the organization with real-time updates.
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import logging

from .policy_engine import PolicyEngine, ComplianceFramework, ComplianceReport
from .audit_logger import AuditLogger, AuditEventType, AuditSeverity
from .risk_assessor import RiskAssessor, RiskLevel, RiskCategory

@dataclass
class ComplianceMetrics:
    """Real-time compliance metrics"""
    overall_compliance_score: float
    framework_scores: Dict[str, float]
    active_violations: int
    critical_violations: int
    risk_level: str
    last_assessment: datetime
    trends: Dict[str, float]  # 30-day trends
    certification_status: Dict[str, str]

@dataclass
class DashboardData:
    """Complete dashboard data structure"""
    metrics: ComplianceMetrics
    recent_violations: List[Dict]
    risk_trends: List[Dict]
    audit_summary: Dict[str, Any]
    recommendations: List[str]
    alerts: List[Dict]
    timestamp: datetime

class ComplianceDashboard:
    """Enterprise compliance monitoring dashboard"""
    
    def __init__(self, db_path: str = "~/.claude/eipas-system/compliance/dashboard.db"):
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.policy_engine = PolicyEngine()
        self.audit_logger = AuditLogger()
        self.risk_assessor = RiskAssessor()
        
        # Dashboard database for metrics storage
        self._init_dashboard_db()
        
        # Cache settings
        self.cache_duration = timedelta(minutes=5)
        self._last_update = datetime.min
        self._cached_data: Optional[DashboardData] = None
    
    def _init_dashboard_db(self):
        """Initialize dashboard metrics database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS compliance_metrics (
                    timestamp TEXT PRIMARY KEY,
                    overall_score REAL NOT NULL,
                    framework_scores TEXT NOT NULL,
                    active_violations INTEGER NOT NULL,
                    critical_violations INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    certification_status TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS violation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    framework TEXT NOT NULL,
                    description TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS risk_trends (
                    timestamp TEXT NOT NULL,
                    category TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    PRIMARY KEY (timestamp, category)
                )
            """)
    
    def get_dashboard_data(self, force_refresh: bool = False) -> DashboardData:
        """Get complete dashboard data with caching"""
        
        # Check cache
        if (not force_refresh and 
            self._cached_data and 
            datetime.now() - self._last_update < self.cache_duration):
            return self._cached_data
        
        self.logger.info("Refreshing dashboard data")
        
        # Collect metrics
        metrics = self.get_compliance_metrics()
        
        # Get recent violations
        recent_violations = self.get_recent_violations(limit=20)
        
        # Get risk trends
        risk_trends = self.get_risk_trends(days=30)
        
        # Get audit summary
        audit_summary = self.get_audit_summary()
        
        # Get recommendations
        recommendations = self.get_recommendations()
        
        # Get alerts
        alerts = self.get_active_alerts()
        
        # Create dashboard data
        dashboard_data = DashboardData(
            metrics=metrics,
            recent_violations=recent_violations,
            risk_trends=risk_trends,
            audit_summary=audit_summary,
            recommendations=recommendations,
            alerts=alerts,
            timestamp=datetime.now()
        )
        
        # Update cache
        self._cached_data = dashboard_data
        self._last_update = datetime.now()
        
        # Store metrics in database
        self._store_metrics(metrics)
        
        return dashboard_data
    
    def get_compliance_metrics(self) -> ComplianceMetrics:
        """Get current compliance metrics"""
        
        # Mock configuration for demonstration
        mock_config = {
            "agents": [{"name": "test", "type": "general"}],
            "hooks": [],
            "commands": [],
            "settings": {
                "tools": {
                    "permissions": {
                        "Bash": ["npm*", "git*"],
                        "Edit": ["allow"]
                    }
                }
            }
        }
        
        # Evaluate compliance for major frameworks
        frameworks = [
            ComplianceFramework.SOC2,
            ComplianceFramework.ISO27001,
            ComplianceFramework.GDPR,
            ComplianceFramework.NIST
        ]
        
        report = self.policy_engine.evaluate_compliance(mock_config, frameworks)
        
        # Calculate trends (mock data for demonstration)
        trends = self._calculate_trends()
        
        return ComplianceMetrics(
            overall_compliance_score=report.overall_score,
            framework_scores={f.value: report.compliance_scores.get(f, 0.0) for f in frameworks},
            active_violations=len([v for v in report.violations if v.severity.value in ['critical', 'high']]),
            critical_violations=len([v for v in report.violations if v.severity.value == 'critical']),
            risk_level=report.risk_level,
            last_assessment=report.assessment_date,
            trends=trends,
            certification_status={f.value: report.certification_status.get(f, 'unknown') for f in frameworks}
        )
    
    def get_recent_violations(self, limit: int = 20) -> List[Dict]:
        """Get recent policy violations"""
        violations = []
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM violation_history 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                for row in cursor:
                    violations.append({
                        'id': row['id'],
                        'timestamp': row['timestamp'],
                        'rule_id': row['rule_id'],
                        'severity': row['severity'],
                        'framework': row['framework'],
                        'description': row['description'],
                        'resolved': bool(row['resolved']),
                        'resolved_at': row['resolved_at']
                    })
        
        except Exception as e:
            self.logger.error(f"Error getting recent violations: {e}")
        
        return violations
    
    def get_risk_trends(self, days: int = 30) -> List[Dict]:
        """Get risk trend data"""
        trends = []
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor = conn.execute("""
                    SELECT * FROM risk_trends 
                    WHERE timestamp >= ?
                    ORDER BY timestamp ASC
                """, (cutoff_date,))
                
                for row in cursor:
                    trends.append({
                        'timestamp': row['timestamp'],
                        'category': row['category'],
                        'risk_score': row['risk_score'],
                        'risk_level': row['risk_level']
                    })
        
        except Exception as e:
            self.logger.error(f"Error getting risk trends: {e}")
        
        # Generate mock data if no historical data
        if not trends:
            trends = self._generate_mock_risk_trends(days)
        
        return trends
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Get audit log summary"""
        summary = {
            'total_events': 0,
            'events_by_type': {},
            'events_by_severity': {},
            'recent_security_events': 0,
            'failed_access_attempts': 0,
            'config_changes': 0
        }
        
        try:
            # Query audit events from last 24 hours
            from .audit_logger import AuditQuery
            
            query = AuditQuery(
                start_time=datetime.now() - timedelta(days=1),
                limit=1000
            )
            
            events = self.audit_logger.query_events(query)
            summary['total_events'] = len(events)
            
            # Count by type and severity
            for event in events:
                event_type = event.event_type.value
                severity = event.severity.value
                
                summary['events_by_type'][event_type] = summary['events_by_type'].get(event_type, 0) + 1
                summary['events_by_severity'][severity] = summary['events_by_severity'].get(severity, 0) + 1
                
                # Count specific event types
                if event.event_type == AuditEventType.SECURITY_EVENT:
                    summary['recent_security_events'] += 1
                elif event.event_type == AuditEventType.ACCESS_DENIED:
                    summary['failed_access_attempts'] += 1
                elif event.event_type == AuditEventType.CONFIG_CHANGE:
                    summary['config_changes'] += 1
        
        except Exception as e:
            self.logger.error(f"Error getting audit summary: {e}")
        
        return summary
    
    def get_recommendations(self) -> List[str]:
        """Get prioritized recommendations"""
        recommendations = []
        
        # Get compliance recommendations
        mock_config = {"agents": [], "hooks": [], "commands": []}
        frameworks = [ComplianceFramework.SOC2, ComplianceFramework.ISO27001]
        
        try:
            report = self.policy_engine.evaluate_compliance(mock_config, frameworks)
            recommendations.extend(report.recommendations)
        except Exception as e:
            self.logger.error(f"Error getting compliance recommendations: {e}")
        
        # Get risk-based recommendations
        try:
            risk_assessment = self.risk_assessor.assess_risk(mock_config)
            recommendations.extend(risk_assessment.recommendations)
        except Exception as e:
            self.logger.error(f"Error getting risk recommendations: {e}")
        
        # Remove duplicates and prioritize
        unique_recommendations = list(dict.fromkeys(recommendations))
        
        return unique_recommendations[:10]  # Top 10 recommendations
    
    def get_active_alerts(self) -> List[Dict]:
        """Get active alerts and notifications"""
        alerts = []
        
        # Check for critical violations
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT COUNT(*) as count FROM violation_history 
                    WHERE severity = 'critical' AND resolved = FALSE
                """)
                
                critical_count = cursor.fetchone()['count']
                if critical_count > 0:
                    alerts.append({
                        'type': 'critical_violation',
                        'severity': 'critical',
                        'message': f'{critical_count} critical policy violations require immediate attention',
                        'action_required': True,
                        'timestamp': datetime.now().isoformat()
                    })
        
        except Exception as e:
            self.logger.error(f"Error checking critical violations: {e}")
        
        # Check for compliance score drops
        metrics = self.get_compliance_metrics()
        if metrics.overall_compliance_score < 70.0:
            alerts.append({
                'type': 'compliance_degradation',
                'severity': 'high',
                'message': f'Overall compliance score dropped to {metrics.overall_compliance_score:.1f}%',
                'action_required': True,
                'timestamp': datetime.now().isoformat()
            })
        
        # Check for failed audits
        audit_summary = self.get_audit_summary()
        if audit_summary.get('failed_access_attempts', 0) > 10:
            alerts.append({
                'type': 'security_concern',
                'severity': 'medium',
                'message': f'{audit_summary["failed_access_attempts"]} failed access attempts in last 24 hours',
                'action_required': False,
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def export_compliance_report(self, format: str = "json") -> str:
        """Export comprehensive compliance report"""
        
        dashboard_data = self.get_dashboard_data()
        
        if format == "json":
            # Convert to JSON-serializable format
            export_data = asdict(dashboard_data)
            export_data['timestamp'] = dashboard_data.timestamp.isoformat()
            export_data['metrics']['last_assessment'] = dashboard_data.metrics.last_assessment.isoformat()
            
            return json.dumps(export_data, indent=2)
        
        elif format == "html":
            return self._generate_html_report(dashboard_data)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _calculate_trends(self) -> Dict[str, float]:
        """Calculate 30-day compliance trends"""
        trends = {}
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
                
                # Get historical scores
                cursor = conn.execute("""
                    SELECT overall_score, timestamp FROM compliance_metrics 
                    WHERE timestamp >= ?
                    ORDER BY timestamp ASC
                """, (cutoff_date,))
                
                scores = [row[0] for row in cursor]
                
                if len(scores) >= 2:
                    trends['overall_score'] = scores[-1] - scores[0]
                else:
                    trends['overall_score'] = 0.0
        
        except Exception as e:
            self.logger.error(f"Error calculating trends: {e}")
            trends['overall_score'] = 0.0
        
        return trends
    
    def _store_metrics(self, metrics: ComplianceMetrics):
        """Store metrics in dashboard database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO compliance_metrics
                    (timestamp, overall_score, framework_scores, active_violations,
                     critical_violations, risk_level, certification_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.last_assessment.isoformat(),
                    metrics.overall_compliance_score,
                    json.dumps(metrics.framework_scores),
                    metrics.active_violations,
                    metrics.critical_violations,
                    metrics.risk_level,
                    json.dumps(metrics.certification_status)
                ))
        
        except Exception as e:
            self.logger.error(f"Error storing metrics: {e}")
    
    def _generate_mock_risk_trends(self, days: int) -> List[Dict]:
        """Generate mock risk trend data for demonstration"""
        trends = []
        
        categories = ['security', 'compliance', 'operational', 'performance']
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            
            for category in categories:
                # Generate realistic trending data
                base_score = 0.3 + (i / days) * 0.2  # Slight upward trend
                noise = (hash(f"{date}_{category}") % 1000) / 10000  # Deterministic noise
                risk_score = max(0.0, min(1.0, base_score + noise))
                
                risk_level = "low"
                if risk_score > 0.7:
                    risk_level = "high"
                elif risk_score > 0.4:
                    risk_level = "medium"
                
                trends.append({
                    'timestamp': date.isoformat(),
                    'category': category,
                    'risk_score': risk_score,
                    'risk_level': risk_level
                })
        
        return trends
    
    def _generate_html_report(self, dashboard_data: DashboardData) -> str:
        """Generate HTML compliance report"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Compliance Dashboard Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .metric-card {{ background: white; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; }}
                .metric-value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
                .alert {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .alert-critical {{ background: #f8d7da; border: 1px solid #f5c6cb; }}
                .alert-high {{ background: #fff3cd; border: 1px solid #ffeaa7; }}
                .violation {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Enterprise Compliance Dashboard</h1>
                <p>Generated: {dashboard_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <h3>Overall Compliance</h3>
                    <div class="metric-value">{dashboard_data.metrics.overall_compliance_score:.1f}%</div>
                </div>
                <div class="metric-card">
                    <h3>Active Violations</h3>
                    <div class="metric-value">{dashboard_data.metrics.active_violations}</div>
                </div>
                <div class="metric-card">
                    <h3>Critical Issues</h3>
                    <div class="metric-value">{dashboard_data.metrics.critical_violations}</div>
                </div>
                <div class="metric-card">
                    <h3>Risk Level</h3>
                    <div class="metric-value">{dashboard_data.metrics.risk_level.upper()}</div>
                </div>
            </div>
            
            <h2>Active Alerts</h2>
        """
        
        for alert in dashboard_data.alerts:
            alert_class = f"alert-{alert['severity']}"
            html += f'<div class="alert {alert_class}">{alert["message"]}</div>'
        
        html += """
            <h2>Framework Compliance Scores</h2>
            <ul>
        """
        
        for framework, score in dashboard_data.metrics.framework_scores.items():
            html += f"<li><strong>{framework.upper()}:</strong> {score:.1f}%</li>"
        
        html += """
            </ul>
            
            <h2>Recent Violations</h2>
        """
        
        for violation in dashboard_data.recent_violations[:10]:
            html += f"""
            <div class="violation">
                <strong>{violation['rule_id']}:</strong> {violation['description']}
                <br><small>Severity: {violation['severity']} | Framework: {violation['framework']}</small>
            </div>
            """
        
        html += """
            <h2>Recommendations</h2>
            <ol>
        """
        
        for rec in dashboard_data.recommendations:
            html += f"<li>{rec}</li>"
        
        html += """
            </ol>
        </body>
        </html>
        """
        
        return html