"""
Dashboard Visualization Engine

Advanced visualization system for creating interactive charts, graphs, and dashboards
from productivity and performance metrics with real-time updates and customizable views.
"""

import json
import math
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import logging
import statistics
from collections import defaultdict

from .metrics_collector import MetricsCollector, MetricType, MetricPoint

class ChartType(Enum):
    """Supported chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    GAUGE = "gauge"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    DONUT = "donut"
    RADAR = "radar"

class TimePeriod(Enum):
    """Time period for data aggregation"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class ChartSeries:
    """Data series for charts"""
    name: str
    data: List[Union[float, int, Dict]]
    color: Optional[str] = None
    type: Optional[ChartType] = None
    yaxis: Optional[str] = None

@dataclass
class ChartConfiguration:
    """Chart configuration and styling"""
    title: str
    chart_type: ChartType
    series: List[ChartSeries]
    x_axis_labels: List[str] = field(default_factory=list)
    x_axis_title: str = ""
    y_axis_title: str = ""
    height: int = 400
    width: int = 600
    theme: str = "light"
    interactive: bool = True
    legend: bool = True
    tooltip: bool = True
    zoom: bool = True
    export_enabled: bool = True
    real_time: bool = False
    refresh_interval: int = 30  # seconds

@dataclass
class DashboardWidget:
    """Individual dashboard widget"""
    widget_id: str
    title: str
    widget_type: str  # chart, metric, table, text
    configuration: Dict[str, Any]
    position: Dict[str, int]  # x, y, width, height
    data_source: str
    refresh_rate: int = 60  # seconds
    visible: bool = True

@dataclass
class DashboardLayout:
    """Complete dashboard layout"""
    dashboard_id: str
    name: str
    description: str
    widgets: List[DashboardWidget]
    grid_cols: int = 12
    grid_rows: int = 20
    auto_refresh: bool = True
    theme: str = "professional"
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)

class DashboardEngine:
    """Advanced dashboard visualization engine"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize metrics collector
        if metrics_collector:
            self.metrics_collector = metrics_collector
        else:
            self.metrics_collector = MetricsCollector()
        
        # Chart templates and themes
        self.chart_templates = self._init_chart_templates()
        self.themes = self._init_themes()
        
        # Color palettes
        self.color_palettes = self._init_color_palettes()
        
        # Pre-built dashboard templates
        self.dashboard_templates = self._init_dashboard_templates()
    
    def _init_chart_templates(self) -> Dict[str, ChartConfiguration]:
        """Initialize pre-built chart templates"""
        return {
            'productivity_trend': ChartConfiguration(
                title="Productivity Trend",
                chart_type=ChartType.LINE,
                series=[],
                x_axis_title="Time",
                y_axis_title="Productivity Score",
                height=350,
                real_time=True
            ),
            'performance_metrics': ChartConfiguration(
                title="Performance Metrics",
                chart_type=ChartType.BAR,
                series=[],
                x_axis_title="Metrics",
                y_axis_title="Value",
                height=300
            ),
            'usage_distribution': ChartConfiguration(
                title="Tool Usage Distribution",
                chart_type=ChartType.PIE,
                series=[],
                height=300
            ),
            'response_time_histogram': ChartConfiguration(
                title="Response Time Distribution",
                chart_type=ChartType.HISTOGRAM,
                series=[],
                x_axis_title="Response Time (ms)",
                y_axis_title="Frequency",
                height=300
            ),
            'resource_gauge': ChartConfiguration(
                title="System Resources",
                chart_type=ChartType.GAUGE,
                series=[],
                height=250
            ),
            'activity_heatmap': ChartConfiguration(
                title="Activity Heatmap",
                chart_type=ChartType.HEATMAP,
                series=[],
                height=400
            )
        }
    
    def _init_themes(self) -> Dict[str, Dict]:
        """Initialize visualization themes"""
        return {
            'professional': {
                'background': '#ffffff',
                'grid_color': '#f0f0f0',
                'text_color': '#333333',
                'primary_color': '#007bff',
                'success_color': '#28a745',
                'warning_color': '#ffc107',
                'danger_color': '#dc3545',
                'font_family': 'Inter, Arial, sans-serif'
            },
            'dark': {
                'background': '#1a1a1a',
                'grid_color': '#333333',
                'text_color': '#ffffff',
                'primary_color': '#0d6efd',
                'success_color': '#198754',
                'warning_color': '#fd7e14',
                'danger_color': '#dc3545',
                'font_family': 'Inter, Arial, sans-serif'
            },
            'minimal': {
                'background': '#fafafa',
                'grid_color': '#e0e0e0',
                'text_color': '#424242',
                'primary_color': '#2196f3',
                'success_color': '#4caf50',
                'warning_color': '#ff9800',
                'danger_color': '#f44336',
                'font_family': 'Roboto, Arial, sans-serif'
            }
        }
    
    def _init_color_palettes(self) -> Dict[str, List[str]]:
        """Initialize color palettes for charts"""
        return {
            'default': ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6c757d', '#17a2b8', '#6f42c1', '#e83e8c'],
            'productivity': ['#28a745', '#20c997', '#17a2b8', '#007bff', '#6f42c1'],
            'performance': ['#007bff', '#0d6efd', '#6610f2', '#6f42c1', '#d63384'],
            'quality': ['#28a745', '#198754', '#20c997', '#0dcaf0', '#17a2b8'],
            'alerts': ['#dc3545', '#fd7e14', '#ffc107', '#28a745', '#6c757d'],
            'gradient_blue': ['#e3f2fd', '#bbdefb', '#90caf9', '#64b5f6', '#42a5f5', '#2196f3', '#1e88e5', '#1976d2'],
            'gradient_green': ['#e8f5e8', '#c8e6c9', '#a5d6a7', '#81c784', '#66bb6a', '#4caf50', '#43a047', '#388e3c']
        }
    
    def _init_dashboard_templates(self) -> Dict[str, DashboardLayout]:
        """Initialize pre-built dashboard templates"""
        templates = {}
        
        # Executive Dashboard
        exec_widgets = [
            DashboardWidget(
                widget_id="exec_productivity",
                title="Overall Productivity",
                widget_type="gauge",
                configuration={"template": "resource_gauge", "metric": "productivity_score"},
                position={"x": 0, "y": 0, "width": 3, "height": 3},
                data_source="productivity_metrics"
            ),
            DashboardWidget(
                widget_id="exec_trend",
                title="30-Day Productivity Trend",
                widget_type="chart",
                configuration={"template": "productivity_trend", "period": "day", "days": 30},
                position={"x": 3, "y": 0, "width": 6, "height": 3},
                data_source="productivity_summary"
            ),
            DashboardWidget(
                widget_id="exec_metrics",
                title="Key Performance Indicators",
                widget_type="metrics_grid",
                configuration={"metrics": ["total_sessions", "avg_productivity", "error_rate", "satisfaction"]},
                position={"x": 9, "y": 0, "width": 3, "height": 3},
                data_source="kpi_summary"
            )
        ]
        templates['executive'] = DashboardLayout(
            dashboard_id="exec_dashboard",
            name="Executive Dashboard",
            description="High-level productivity and performance overview",
            widgets=exec_widgets
        )
        
        # Developer Dashboard
        dev_widgets = [
            DashboardWidget(
                widget_id="dev_performance",
                title="Performance Metrics",
                widget_type="chart",
                configuration={"template": "performance_metrics", "period": "hour", "hours": 24},
                position={"x": 0, "y": 0, "width": 6, "height": 4},
                data_source="performance_analytics"
            ),
            DashboardWidget(
                widget_id="dev_usage",
                title="Tool Usage",
                widget_type="chart",
                configuration={"template": "usage_distribution", "period": "day", "days": 7},
                position={"x": 6, "y": 0, "width": 6, "height": 4},
                data_source="usage_patterns"
            ),
            DashboardWidget(
                widget_id="dev_response_times",
                title="Response Time Distribution",
                widget_type="chart",
                configuration={"template": "response_time_histogram", "period": "hour", "hours": 6},
                position={"x": 0, "y": 4, "width": 12, "height": 3},
                data_source="performance_analytics"
            )
        ]
        templates['developer'] = DashboardLayout(
            dashboard_id="dev_dashboard",
            name="Developer Dashboard",
            description="Detailed performance and usage analytics",
            widgets=dev_widgets
        )
        
        return templates
    
    def create_chart(self, template_name: str, data_source: str, 
                    time_period: TimePeriod = TimePeriod.DAY,
                    period_count: int = 7, **kwargs) -> ChartConfiguration:
        """Create a chart from template with data"""
        
        if template_name not in self.chart_templates:
            raise ValueError(f"Unknown chart template: {template_name}")
        
        # Get template
        chart_config = self.chart_templates[template_name]
        
        # Fetch data based on template type
        if template_name == 'productivity_trend':
            chart_config = self._create_productivity_trend_chart(chart_config, time_period, period_count)
        elif template_name == 'performance_metrics':
            chart_config = self._create_performance_metrics_chart(chart_config, time_period, period_count)
        elif template_name == 'usage_distribution':
            chart_config = self._create_usage_distribution_chart(chart_config, time_period, period_count)
        elif template_name == 'response_time_histogram':
            chart_config = self._create_response_time_histogram(chart_config, time_period, period_count)
        elif template_name == 'resource_gauge':
            chart_config = self._create_resource_gauge_chart(chart_config)
        elif template_name == 'activity_heatmap':
            chart_config = self._create_activity_heatmap(chart_config, time_period, period_count)
        
        # Apply any custom overrides
        for key, value in kwargs.items():
            if hasattr(chart_config, key):
                setattr(chart_config, key, value)
        
        return chart_config
    
    def _create_productivity_trend_chart(self, config: ChartConfiguration, 
                                       time_period: TimePeriod, period_count: int) -> ChartConfiguration:
        """Create productivity trend line chart"""
        
        try:
            # Get productivity summary
            summary = self.metrics_collector.get_productivity_summary(days=period_count)
            trend_data = summary.get('productivity_trend', [])
            
            if not trend_data:
                # Generate sample data if no real data available
                trend_data = self._generate_sample_productivity_data(period_count)
            
            # Prepare chart data
            dates = [point['date'] for point in trend_data]
            scores = [point['score'] for point in trend_data]
            
            config.series = [
                ChartSeries(
                    name="Productivity Score",
                    data=scores,
                    color=self.color_palettes['productivity'][0]
                )
            ]
            config.x_axis_labels = dates
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error creating productivity trend chart: {e}")
            return self._create_empty_chart(config, "No productivity data available")
    
    def _create_performance_metrics_chart(self, config: ChartConfiguration,
                                        time_period: TimePeriod, period_count: int) -> ChartConfiguration:
        """Create performance metrics bar chart"""
        
        try:
            # Get performance analytics
            analytics = self.metrics_collector.get_performance_analytics(hours=period_count)
            
            # Extract key metrics
            metrics = {
                'Avg Response Time': analytics.get('response_times', {}).get('avg', 0),
                'P95 Response Time': analytics.get('response_times', {}).get('p95', 0),
                'CPU Usage %': analytics.get('resource_usage', {}).get('cpu_avg', 0),
                'Memory Usage (MB)': analytics.get('resource_usage', {}).get('memory_avg', 0),
                'Commands/Hour': analytics.get('throughput', {}).get('commands_per_hour', 0)
            }
            
            if not any(metrics.values()):
                # Generate sample data
                metrics = {
                    'Avg Response Time': 450.0,
                    'P95 Response Time': 1200.0,
                    'CPU Usage %': 15.5,
                    'Memory Usage (MB)': 256.8,
                    'Commands/Hour': 45.2
                }
            
            config.series = [
                ChartSeries(
                    name="Performance Metrics",
                    data=list(metrics.values()),
                    color=self.color_palettes['performance'][0]
                )
            ]
            config.x_axis_labels = list(metrics.keys())
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error creating performance metrics chart: {e}")
            return self._create_empty_chart(config, "No performance data available")
    
    def _create_usage_distribution_chart(self, config: ChartConfiguration,
                                       time_period: TimePeriod, period_count: int) -> ChartConfiguration:
        """Create tool usage distribution pie chart"""
        
        try:
            # Get usage patterns
            patterns = self.metrics_collector.get_usage_patterns(days=period_count)
            tools_data = patterns.get('most_used_tools', [])
            
            if not tools_data:
                # Generate sample data
                tools_data = [
                    {'tool': 'Bash', 'count': 125},
                    {'tool': 'Edit', 'count': 89},
                    {'tool': 'Read', 'count': 67},
                    {'tool': 'Write', 'count': 45},
                    {'tool': 'Grep', 'count': 34}
                ]
            
            # Prepare pie chart data
            pie_data = []
            colors = self.color_palettes['default']
            
            for i, tool_data in enumerate(tools_data[:8]):  # Limit to top 8
                pie_data.append({
                    'name': tool_data['tool'],
                    'y': tool_data['count'],
                    'color': colors[i % len(colors)]
                })
            
            config.series = [
                ChartSeries(
                    name="Tool Usage",
                    data=pie_data
                )
            ]
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error creating usage distribution chart: {e}")
            return self._create_empty_chart(config, "No usage data available")
    
    def _create_response_time_histogram(self, config: ChartConfiguration,
                                      time_period: TimePeriod, period_count: int) -> ChartConfiguration:
        """Create response time histogram"""
        
        try:
            # Get performance analytics
            analytics = self.metrics_collector.get_performance_analytics(hours=period_count)
            
            # Generate histogram bins (sample data for demonstration)
            bins = ['0-100ms', '100-300ms', '300-500ms', '500-1s', '1-2s', '2-5s', '5s+']
            frequencies = [45, 78, 67, 34, 12, 5, 2]  # Sample frequencies
            
            config.series = [
                ChartSeries(
                    name="Response Time Distribution",
                    data=frequencies,
                    color=self.color_palettes['performance'][2]
                )
            ]
            config.x_axis_labels = bins
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error creating response time histogram: {e}")
            return self._create_empty_chart(config, "No response time data available")
    
    def _create_resource_gauge_chart(self, config: ChartConfiguration) -> ChartConfiguration:
        """Create system resource gauge chart"""
        
        try:
            # Get current system metrics
            self.metrics_collector.collect_system_metrics()
            
            # Sample gauge data (in real implementation, get from recent metrics)
            gauge_data = [
                {'name': 'CPU Usage', 'value': 25.5, 'max': 100, 'color': '#28a745'},
                {'name': 'Memory Usage', 'value': 456.8, 'max': 1024, 'color': '#007bff'},
                {'name': 'Disk I/O', 'value': 12.3, 'max': 100, 'color': '#ffc107'}
            ]
            
            config.series = [
                ChartSeries(
                    name="System Resources",
                    data=gauge_data
                )
            ]
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error creating resource gauge chart: {e}")
            return self._create_empty_chart(config, "No system data available")
    
    def _create_activity_heatmap(self, config: ChartConfiguration,
                               time_period: TimePeriod, period_count: int) -> ChartConfiguration:
        """Create activity heatmap"""
        
        try:
            # Generate sample heatmap data (24h x 7 days)
            hours = list(range(24))
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            heatmap_data = []
            for day_idx, day in enumerate(days):
                for hour in hours:
                    # Generate realistic activity pattern
                    if 9 <= hour <= 17:  # Work hours
                        activity = 50 + (hash(f"{day}{hour}") % 40)
                    elif 7 <= hour <= 21:  # Extended hours
                        activity = 20 + (hash(f"{day}{hour}") % 30)
                    else:  # Night hours
                        activity = hash(f"{day}{hour}") % 15
                    
                    heatmap_data.append([hour, day_idx, activity])
            
            config.series = [
                ChartSeries(
                    name="Activity Level",
                    data=heatmap_data
                )
            ]
            config.x_axis_labels = [f"{h:02d}:00" for h in hours]
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error creating activity heatmap: {e}")
            return self._create_empty_chart(config, "No activity data available")
    
    def _generate_sample_productivity_data(self, days: int) -> List[Dict]:
        """Generate sample productivity data for demonstration"""
        data = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            # Generate realistic trending data
            base_score = 3.0 + (i / days) * 1.5  # Slight upward trend
            noise = (hash(f"prod_{i}") % 100) / 100.0 - 0.5  # Random noise
            score = max(1.0, min(5.0, base_score + noise))
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'score': round(score, 2)
            })
        
        return data
    
    def _create_empty_chart(self, config: ChartConfiguration, message: str) -> ChartConfiguration:
        """Create empty chart with message"""
        config.series = []
        config.title = f"{config.title} - {message}"
        return config
    
    def create_dashboard(self, template_name: str, **kwargs) -> DashboardLayout:
        """Create a dashboard from template"""
        
        if template_name not in self.dashboard_templates:
            raise ValueError(f"Unknown dashboard template: {template_name}")
        
        dashboard = self.dashboard_templates[template_name]
        
        # Apply customizations
        for key, value in kwargs.items():
            if hasattr(dashboard, key):
                setattr(dashboard, key, value)
        
        # Update last modified time
        dashboard.last_modified = datetime.now()
        
        return dashboard
    
    def export_chart_config(self, chart_config: ChartConfiguration, format: str = "json") -> str:
        """Export chart configuration in various formats"""
        
        if format == "json":
            return json.dumps(asdict(chart_config), indent=2, default=str)
        
        elif format == "highcharts":
            return self._export_highcharts_config(chart_config)
        
        elif format == "plotly":
            return self._export_plotly_config(chart_config)
        
        elif format == "chartjs":
            return self._export_chartjs_config(chart_config)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_highcharts_config(self, config: ChartConfiguration) -> str:
        """Export as Highcharts configuration"""
        
        highcharts_config = {
            "chart": {
                "type": self._map_chart_type_to_highcharts(config.chart_type),
                "height": config.height,
                "width": config.width
            },
            "title": {"text": config.title},
            "xAxis": {
                "categories": config.x_axis_labels,
                "title": {"text": config.x_axis_title}
            },
            "yAxis": {
                "title": {"text": config.y_axis_title}
            },
            "series": [
                {
                    "name": series.name,
                    "data": series.data,
                    "color": series.color
                }
                for series in config.series
            ],
            "legend": {"enabled": config.legend},
            "tooltip": {"enabled": config.tooltip},
            "exporting": {"enabled": config.export_enabled}
        }
        
        return json.dumps(highcharts_config, indent=2)
    
    def _export_plotly_config(self, config: ChartConfiguration) -> str:
        """Export as Plotly configuration"""
        
        plotly_data = []
        for series in config.series:
            trace = {
                "name": series.name,
                "type": self._map_chart_type_to_plotly(config.chart_type),
                "y": series.data if config.chart_type != ChartType.PIE else None,
                "x": config.x_axis_labels if config.chart_type != ChartType.PIE else None,
                "values": series.data if config.chart_type == ChartType.PIE else None,
                "labels": config.x_axis_labels if config.chart_type == ChartType.PIE else None,
                "marker": {"color": series.color} if series.color else {}
            }
            # Remove None values
            trace = {k: v for k, v in trace.items() if v is not None}
            plotly_data.append(trace)
        
        plotly_config = {
            "data": plotly_data,
            "layout": {
                "title": config.title,
                "xaxis": {"title": config.x_axis_title},
                "yaxis": {"title": config.y_axis_title},
                "height": config.height,
                "width": config.width,
                "showlegend": config.legend
            }
        }
        
        return json.dumps(plotly_config, indent=2)
    
    def _export_chartjs_config(self, config: ChartConfiguration) -> str:
        """Export as Chart.js configuration"""
        
        chartjs_config = {
            "type": self._map_chart_type_to_chartjs(config.chart_type),
            "data": {
                "labels": config.x_axis_labels,
                "datasets": [
                    {
                        "label": series.name,
                        "data": series.data,
                        "backgroundColor": series.color,
                        "borderColor": series.color
                    }
                    for series in config.series
                ]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": config.title
                    },
                    "legend": {
                        "display": config.legend
                    }
                },
                "scales": {
                    "x": {
                        "title": {
                            "display": bool(config.x_axis_title),
                            "text": config.x_axis_title
                        }
                    },
                    "y": {
                        "title": {
                            "display": bool(config.y_axis_title),
                            "text": config.y_axis_title
                        }
                    }
                }
            }
        }
        
        return json.dumps(chartjs_config, indent=2)
    
    def _map_chart_type_to_highcharts(self, chart_type: ChartType) -> str:
        """Map ChartType to Highcharts type"""
        mapping = {
            ChartType.LINE: "line",
            ChartType.BAR: "column",
            ChartType.PIE: "pie",
            ChartType.SCATTER: "scatter",
            ChartType.AREA: "area",
            ChartType.GAUGE: "gauge",
            ChartType.HEATMAP: "heatmap",
            ChartType.HISTOGRAM: "column",
            ChartType.DONUT: "pie",
            ChartType.RADAR: "line"
        }
        return mapping.get(chart_type, "line")
    
    def _map_chart_type_to_plotly(self, chart_type: ChartType) -> str:
        """Map ChartType to Plotly type"""
        mapping = {
            ChartType.LINE: "scatter",
            ChartType.BAR: "bar",
            ChartType.PIE: "pie",
            ChartType.SCATTER: "scatter",
            ChartType.AREA: "scatter",
            ChartType.GAUGE: "indicator",
            ChartType.HEATMAP: "heatmap",
            ChartType.HISTOGRAM: "histogram",
            ChartType.DONUT: "pie",
            ChartType.RADAR: "scatterpolar"
        }
        return mapping.get(chart_type, "scatter")
    
    def _map_chart_type_to_chartjs(self, chart_type: ChartType) -> str:
        """Map ChartType to Chart.js type"""
        mapping = {
            ChartType.LINE: "line",
            ChartType.BAR: "bar",
            ChartType.PIE: "pie",
            ChartType.SCATTER: "scatter",
            ChartType.AREA: "line",
            ChartType.GAUGE: "doughnut",
            ChartType.HEATMAP: "scatter",
            ChartType.HISTOGRAM: "bar",
            ChartType.DONUT: "doughnut",
            ChartType.RADAR: "radar"
        }
        return mapping.get(chart_type, "line")
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available chart and dashboard templates"""
        
        chart_info = {}
        for name, config in self.chart_templates.items():
            chart_info[name] = {
                "title": config.title,
                "type": config.chart_type.value,
                "description": f"{config.chart_type.value.title()} chart for {name.replace('_', ' ')}"
            }
        
        dashboard_info = {}
        for name, layout in self.dashboard_templates.items():
            dashboard_info[name] = {
                "name": layout.name,
                "description": layout.description,
                "widgets": len(layout.widgets)
            }
        
        return {
            "charts": chart_info,
            "dashboards": dashboard_info,
            "themes": list(self.themes.keys()),
            "color_palettes": list(self.color_palettes.keys())
        }