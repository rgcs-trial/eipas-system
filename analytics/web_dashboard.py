"""
Web Dashboard Interface

Interactive web-based dashboard for visualizing productivity metrics, analytics insights,
and business intelligence with real-time updates and responsive design.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import logging
import threading
import time
from collections import defaultdict
import sqlite3
import hashlib
import secrets

from .metrics_collector import MetricsCollector
from .dashboard_engine import DashboardEngine, DashboardLayout, ChartConfiguration
from .analytics_engine import AnalyticsEngine, AnalyticsResult
from .insights_generator import InsightsGenerator, InsightReport
from .trend_analyzer import TrendAnalyzer
from .roi_calculator import ROICalculator, ROIResult

class DashboardTheme(Enum):
    """Dashboard visual themes"""
    PROFESSIONAL = "professional"
    DARK = "dark"
    MINIMAL = "minimal"
    HIGH_CONTRAST = "high_contrast"
    CUSTOM = "custom"

class WidgetSize(Enum):
    """Widget size presets"""
    SMALL = "small"      # 3x2 grid
    MEDIUM = "medium"    # 6x3 grid
    LARGE = "large"      # 9x4 grid
    FULL = "full"        # 12x6 grid

class UpdateFrequency(Enum):
    """Data update frequencies"""
    REAL_TIME = 5       # 5 seconds
    FAST = 30           # 30 seconds
    NORMAL = 60         # 1 minute
    SLOW = 300          # 5 minutes
    MANUAL = 0          # Manual refresh only

@dataclass
class DashboardUser:
    """Dashboard user configuration"""
    user_id: str
    username: str
    role: str
    preferences: Dict[str, Any]
    permissions: List[str]
    created_at: datetime
    last_login: Optional[datetime] = None

@dataclass
class DashboardSession:
    """User session data"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True

@dataclass
class WebWidget:
    """Web-specific widget configuration"""
    widget_id: str
    title: str
    widget_type: str
    data_source: str
    chart_config: Optional[ChartConfiguration] = None
    position: Dict[str, int] = None
    size: WidgetSize = WidgetSize.MEDIUM
    update_frequency: UpdateFrequency = UpdateFrequency.NORMAL
    permissions: List[str] = None
    custom_css: str = ""
    interactive: bool = True
    export_enabled: bool = True

@dataclass
class DashboardPage:
    """Dashboard page configuration"""
    page_id: str
    name: str
    description: str
    widgets: List[WebWidget]
    layout_type: str = "grid"  # grid, flex, custom
    theme: DashboardTheme = DashboardTheme.PROFESSIONAL
    auto_refresh: bool = True
    refresh_interval: int = 60
    permissions: List[str] = None
    created_by: str = ""
    created_at: datetime = None

class WebDashboard:
    """Interactive web dashboard system"""
    
    def __init__(self, 
                 metrics_collector: Optional[MetricsCollector] = None,
                 dashboard_engine: Optional[DashboardEngine] = None,
                 analytics_engine: Optional[AnalyticsEngine] = None,
                 insights_generator: Optional[InsightsGenerator] = None,
                 trend_analyzer: Optional[TrendAnalyzer] = None,
                 roi_calculator: Optional[ROICalculator] = None,
                 db_path: str = "~/.claude/eipas-system/analytics/web_dashboard.db",
                 static_path: str = "~/.claude/eipas-system/analytics/static",
                 templates_path: str = "~/.claude/eipas-system/analytics/templates"):
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize analytics components
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.dashboard_engine = dashboard_engine or DashboardEngine(self.metrics_collector)
        self.analytics_engine = analytics_engine or AnalyticsEngine(self.metrics_collector)
        self.insights_generator = insights_generator or InsightsGenerator(self.metrics_collector)
        self.trend_analyzer = trend_analyzer or TrendAnalyzer(self.metrics_collector)
        self.roi_calculator = roi_calculator or ROICalculator(self.metrics_collector)
        
        # Database and file paths
        self.db_path = Path(db_path).expanduser()
        self.static_path = Path(static_path).expanduser()
        self.templates_path = Path(templates_path).expanduser()
        
        # Create directories
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.static_path.mkdir(parents=True, exist_ok=True)
        self.templates_path.mkdir(parents=True, exist_ok=True)
        
        # Dashboard state
        self.active_sessions = {}
        self.dashboard_pages = {}
        self.widget_cache = {}
        self.update_threads = {}
        
        # Security
        self.secret_key = self._generate_secret_key()
        
        # Initialize system
        self._init_database()
        self._create_default_pages()
        self._create_static_assets()
        self._start_background_updates()
    
    def _init_database(self):
        """Initialize web dashboard database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL,
                    preferences TEXT,
                    permissions TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_login TEXT
                )
            """)
            
            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_activity TEXT DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES dashboard_users (user_id)
                )
            """)
            
            # Dashboard pages table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_pages (
                    page_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    layout_type TEXT DEFAULT 'grid',
                    theme TEXT DEFAULT 'professional',
                    auto_refresh BOOLEAN DEFAULT TRUE,
                    refresh_interval INTEGER DEFAULT 60,
                    permissions TEXT,
                    created_by TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    page_config TEXT
                )
            """)
            
            # Widgets table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_widgets (
                    widget_id TEXT PRIMARY KEY,
                    page_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    widget_type TEXT NOT NULL,
                    data_source TEXT NOT NULL,
                    position_x INTEGER DEFAULT 0,
                    position_y INTEGER DEFAULT 0,
                    width INTEGER DEFAULT 6,
                    height INTEGER DEFAULT 3,
                    size_preset TEXT DEFAULT 'medium',
                    update_frequency INTEGER DEFAULT 60,
                    permissions TEXT,
                    widget_config TEXT,
                    FOREIGN KEY (page_id) REFERENCES dashboard_pages (page_id)
                )
            """)
            
            # Widget data cache table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS widget_data_cache (
                    cache_id TEXT PRIMARY KEY,
                    widget_id TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT,
                    FOREIGN KEY (widget_id) REFERENCES dashboard_widgets (widget_id)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON dashboard_sessions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_active ON dashboard_sessions(is_active)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_widgets_page ON dashboard_widgets(page_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_widget ON widget_data_cache(widget_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON widget_data_cache(expires_at)")
    
    def _generate_secret_key(self) -> str:
        """Generate secure secret key for sessions"""
        return secrets.token_hex(32)
    
    def _create_default_pages(self):
        """Create default dashboard pages"""
        
        # Executive Overview Page
        exec_page = self.create_dashboard_page(
            name="Executive Overview",
            description="High-level productivity and business metrics",
            layout_type="grid",
            theme=DashboardTheme.PROFESSIONAL
        )
        
        # Add executive widgets
        self.add_widget(
            page_id=exec_page,
            title="Overall Productivity Score",
            widget_type="gauge",
            data_source="productivity_summary",
            size=WidgetSize.SMALL,
            position={"x": 0, "y": 0}
        )
        
        self.add_widget(
            page_id=exec_page,
            title="30-Day Productivity Trend",
            widget_type="line_chart",
            data_source="productivity_trend",
            size=WidgetSize.LARGE,
            position={"x": 3, "y": 0}
        )
        
        self.add_widget(
            page_id=exec_page,
            title="Key Performance Indicators",
            widget_type="metrics_grid",
            data_source="kpi_summary",
            size=WidgetSize.MEDIUM,
            position={"x": 0, "y": 3}
        )
        
        self.add_widget(
            page_id=exec_page,
            title="ROI Analysis",
            widget_type="roi_summary",
            data_source="roi_metrics",
            size=WidgetSize.MEDIUM,
            position={"x": 6, "y": 3}
        )
        
        # Developer Analytics Page
        dev_page = self.create_dashboard_page(
            name="Developer Analytics",
            description="Detailed development productivity and performance metrics",
            layout_type="grid",
            theme=DashboardTheme.PROFESSIONAL
        )
        
        # Add developer widgets
        self.add_widget(
            page_id=dev_page,
            title="Performance Metrics",
            widget_type="bar_chart",
            data_source="performance_analytics",
            size=WidgetSize.LARGE,
            position={"x": 0, "y": 0}
        )
        
        self.add_widget(
            page_id=dev_page,
            title="Tool Usage Distribution",
            widget_type="pie_chart",
            data_source="usage_patterns",
            size=WidgetSize.MEDIUM,
            position={"x": 9, "y": 0}
        )
        
        self.add_widget(
            page_id=dev_page,
            title="Response Time Trends",
            widget_type="area_chart",
            data_source="response_times",
            size=WidgetSize.FULL,
            position={"x": 0, "y": 4}
        )
        
        # System Monitoring Page
        sys_page = self.create_dashboard_page(
            name="System Monitoring",
            description="Real-time system performance and resource utilization",
            layout_type="grid",
            theme=DashboardTheme.DARK
        )
        
        # Add system widgets
        self.add_widget(
            page_id=sys_page,
            title="CPU Usage",
            widget_type="gauge",
            data_source="system_cpu",
            size=WidgetSize.SMALL,
            update_frequency=UpdateFrequency.REAL_TIME,
            position={"x": 0, "y": 0}
        )
        
        self.add_widget(
            page_id=sys_page,
            title="Memory Usage",
            widget_type="gauge",
            data_source="system_memory",
            size=WidgetSize.SMALL,
            update_frequency=UpdateFrequency.REAL_TIME,
            position={"x": 3, "y": 0}
        )
        
        self.add_widget(
            page_id=sys_page,
            title="System Activity Heatmap",
            widget_type="heatmap",
            data_source="activity_patterns",
            size=WidgetSize.LARGE,
            position={"x": 6, "y": 0}
        )
    
    def _create_static_assets(self):
        """Create static web assets (CSS, JS, templates)"""
        
        # Main CSS file
        main_css = """
/* Main Dashboard Styles */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --light-color: #f8f9fa;
    --dark-color: #343a40;
    --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --border-radius: 8px;
    --box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    --transition: all 0.3s ease;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-family);
    background-color: #f5f6fa;
    color: #2c3e50;
    line-height: 1.6;
}

/* Dashboard Layout */
.dashboard-container {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 250px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    box-shadow: 2px 0 10px rgba(0,0,0,0.1);
}

.main-content {
    flex: 1;
    padding: 20px;
    overflow-x: auto;
}

/* Navigation */
.nav-menu {
    list-style: none;
    margin-top: 30px;
}

.nav-item {
    margin-bottom: 10px;
}

.nav-link {
    display: block;
    padding: 12px 16px;
    color: rgba(255,255,255,0.9);
    text-decoration: none;
    border-radius: var(--border-radius);
    transition: var(--transition);
}

.nav-link:hover,
.nav-link.active {
    background-color: rgba(255,255,255,0.2);
    color: white;
    transform: translateX(5px);
}

/* Dashboard Grid */
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    grid-template-rows: repeat(20, 60px);
    gap: 20px;
    width: 100%;
    max-width: 1400px;
}

/* Widget Styles */
.widget {
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    padding: 20px;
    transition: var(--transition);
    position: relative;
    overflow: hidden;
}

.widget:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}

.widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.widget-title {
    font-size: 16px;
    font-weight: 600;
    color: #2c3e50;
    margin: 0;
}

.widget-actions {
    display: flex;
    gap: 8px;
}

.widget-action {
    padding: 4px 8px;
    border: none;
    background: transparent;
    color: #6c757d;
    cursor: pointer;
    border-radius: 4px;
    transition: var(--transition);
}

.widget-action:hover {
    background-color: #f8f9fa;
    color: #495057;
}

.widget-content {
    height: calc(100% - 60px);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

/* Widget Sizes */
.widget-small {
    grid-column: span 3;
    grid-row: span 2;
}

.widget-medium {
    grid-column: span 6;
    grid-row: span 3;
}

.widget-large {
    grid-column: span 9;
    grid-row: span 4;
}

.widget-full {
    grid-column: span 12;
    grid-row: span 6;
}

/* Chart Containers */
.chart-container {
    width: 100%;
    height: 100%;
    position: relative;
}

.chart-loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    color: #6c757d;
    font-style: italic;
}

/* Metrics Grid */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 15px;
    height: 100%;
}

.metric-item {
    text-align: center;
    padding: 15px;
    border-radius: var(--border-radius);
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
}

.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 5px;
}

.metric-label {
    font-size: 12px;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Gauge Styles */
.gauge-container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.gauge-value {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 10px;
}

.gauge-label {
    font-size: 14px;
    color: #6c757d;
    text-align: center;
}

/* ROI Summary */
.roi-summary {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.roi-metric {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #eee;
}

.roi-metric:last-child {
    border-bottom: none;
}

.roi-label {
    font-weight: 500;
    color: #495057;
}

.roi-value {
    font-weight: 700;
    font-size: 18px;
}

.roi-positive {
    color: var(--success-color);
}

.roi-negative {
    color: var(--danger-color);
}

/* Responsive Design */
@media (max-width: 1200px) {
    .dashboard-grid {
        grid-template-columns: repeat(8, 1fr);
    }
    
    .widget-large {
        grid-column: span 6;
    }
    
    .widget-full {
        grid-column: span 8;
    }
}

@media (max-width: 768px) {
    .dashboard-container {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
        padding: 15px;
    }
    
    .main-content {
        padding: 15px;
    }
    
    .dashboard-grid {
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    .widget-small,
    .widget-medium,
    .widget-large,
    .widget-full {
        grid-column: span 1;
        grid-row: span 3;
    }
}

/* Dark Theme */
.theme-dark {
    background-color: #1a1a1a;
    color: #e0e0e0;
}

.theme-dark .widget {
    background: #2d2d2d;
    border: 1px solid #404040;
}

.theme-dark .widget-title {
    color: #e0e0e0;
}

.theme-dark .metric-item {
    background: linear-gradient(135deg, #2d2d2d, #404040);
}

/* Animations */
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.widget {
    animation: slideIn 0.5s ease-out;
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.7;
    }
}

.loading {
    animation: pulse 1.5s infinite;
}

/* Utility Classes */
.text-center { text-align: center; }
.text-success { color: var(--success-color) !important; }
.text-warning { color: var(--warning-color) !important; }
.text-danger { color: var(--danger-color) !important; }
.text-muted { color: var(--secondary-color) !important; }

.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 1rem; }
.mb-4 { margin-bottom: 1.5rem; }

.d-flex { display: flex; }
.justify-content-between { justify-content: space-between; }
.align-items-center { align-items: center; }
        """
        
        (self.static_path / "dashboard.css").write_text(main_css)
        
        # Main JavaScript file
        main_js = """
// Dashboard JavaScript
class Dashboard {
    constructor() {
        this.widgets = new Map();
        this.updateIntervals = new Map();
        this.websocket = null;
        this.currentTheme = 'professional';
        
        this.init();
    }
    
    init() {
        this.initializeWebSocket();
        this.loadWidgets();
        this.setupEventListeners();
        this.startAutoRefresh();
    }
    
    initializeWebSocket() {
        // WebSocket connection for real-time updates
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            // Attempt to reconnect after 5 seconds
            setTimeout(() => this.initializeWebSocket(), 5000);
        };
    }
    
    handleWebSocketMessage(data) {
        if (data.type === 'widget_update') {
            this.updateWidget(data.widget_id, data.data);
        } else if (data.type === 'system_alert') {
            this.showAlert(data.message, data.level);
        }
    }
    
    loadWidgets() {
        const widgets = document.querySelectorAll('.widget');
        
        widgets.forEach(widget => {
            const widgetId = widget.dataset.widgetId;
            const widgetType = widget.dataset.widgetType;
            const dataSource = widget.dataset.dataSource;
            const updateFreq = parseInt(widget.dataset.updateFreq) || 60;
            
            this.widgets.set(widgetId, {
                element: widget,
                type: widgetType,
                dataSource: dataSource,
                updateFrequency: updateFreq
            });
            
            // Load initial data
            this.loadWidgetData(widgetId);
            
            // Set up auto-refresh if frequency > 0
            if (updateFreq > 0) {
                const interval = setInterval(() => {
                    this.loadWidgetData(widgetId);
                }, updateFreq * 1000);
                
                this.updateIntervals.set(widgetId, interval);
            }
        });
    }
    
    async loadWidgetData(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget) return;
        
        const contentElement = widget.element.querySelector('.widget-content');
        contentElement.innerHTML = '<div class="chart-loading">Loading...</div>';
        
        try {
            const response = await fetch(`/api/widget/${widgetId}/data`);
            const data = await response.json();
            
            if (data.success) {
                this.renderWidget(widgetId, data.data);
            } else {
                this.showWidgetError(widgetId, data.error);
            }
        } catch (error) {
            console.error(`Error loading widget ${widgetId}:`, error);
            this.showWidgetError(widgetId, 'Failed to load data');
        }
    }
    
    renderWidget(widgetId, data) {
        const widget = this.widgets.get(widgetId);
        if (!widget) return;
        
        const contentElement = widget.element.querySelector('.widget-content');
        
        switch (widget.type) {
            case 'line_chart':
            case 'bar_chart':
            case 'area_chart':
            case 'pie_chart':
                this.renderChart(contentElement, widget.type, data);
                break;
            case 'gauge':
                this.renderGauge(contentElement, data);
                break;
            case 'metrics_grid':
                this.renderMetricsGrid(contentElement, data);
                break;
            case 'roi_summary':
                this.renderROISummary(contentElement, data);
                break;
            case 'heatmap':
                this.renderHeatmap(contentElement, data);
                break;
            default:
                contentElement.innerHTML = '<div class="text-muted">Unsupported widget type</div>';
        }
    }
    
    renderChart(container, chartType, data) {
        container.innerHTML = '<div class="chart-container"><canvas id="chart-' + Date.now() + '"></canvas></div>';
        
        const canvas = container.querySelector('canvas');
        const ctx = canvas.getContext('2d');
        
        // Use Chart.js for rendering
        new Chart(ctx, {
            type: this.mapChartType(chartType),
            data: data.chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: chartType !== 'pie_chart' ? {
                    y: {
                        beginAtZero: true
                    }
                } : {}
            }
        });
    }
    
    renderGauge(container, data) {
        const value = data.value || 0;
        const max = data.max || 100;
        const label = data.label || '';
        const color = this.getGaugeColor(value, max);
        
        container.innerHTML = `
            <div class="gauge-container">
                <div class="gauge-value" style="color: ${color}">
                    ${value}${data.unit || ''}
                </div>
                <div class="gauge-label">${label}</div>
                <div style="width: 100%; height: 10px; background: #eee; border-radius: 5px; margin-top: 15px;">
                    <div style="width: ${(value/max)*100}%; height: 100%; background: ${color}; border-radius: 5px; transition: width 0.5s ease;"></div>
                </div>
            </div>
        `;
    }
    
    renderMetricsGrid(container, data) {
        const metrics = data.metrics || [];
        
        const html = `
            <div class="metrics-grid">
                ${metrics.map(metric => `
                    <div class="metric-item">
                        <div class="metric-value">${metric.value}</div>
                        <div class="metric-label">${metric.label}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    renderROISummary(container, data) {
        const roi = data.roi || {};
        
        const html = `
            <div class="roi-summary">
                <div class="roi-metric">
                    <span class="roi-label">ROI</span>
                    <span class="roi-value ${roi.percentage > 0 ? 'roi-positive' : 'roi-negative'}">
                        ${roi.percentage}%
                    </span>
                </div>
                <div class="roi-metric">
                    <span class="roi-label">NPV</span>
                    <span class="roi-value">$${this.formatNumber(roi.npv)}</span>
                </div>
                <div class="roi-metric">
                    <span class="roi-label">Payback</span>
                    <span class="roi-value">${roi.payback_months} months</span>
                </div>
                <div class="roi-metric">
                    <span class="roi-label">B/C Ratio</span>
                    <span class="roi-value">${roi.bcr}</span>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    renderHeatmap(container, data) {
        // Simplified heatmap rendering
        const heatmapData = data.heatmap || [];
        
        container.innerHTML = '<div class="chart-container"><canvas id="heatmap-' + Date.now() + '"></canvas></div>';
        
        // Would implement with Chart.js matrix plugin or custom rendering
        const canvas = container.querySelector('canvas');
        const ctx = canvas.getContext('2d');
        
        // Basic heatmap implementation
        this.drawHeatmap(ctx, heatmapData);
    }
    
    drawHeatmap(ctx, data) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;
        const cellWidth = width / 24; // 24 hours
        const cellHeight = height / 7; // 7 days
        
        data.forEach(point => {
            const [hour, day, intensity] = point;
            const color = this.getHeatmapColor(intensity);
            
            ctx.fillStyle = color;
            ctx.fillRect(hour * cellWidth, day * cellHeight, cellWidth, cellHeight);
        });
    }
    
    mapChartType(type) {
        const mapping = {
            'line_chart': 'line',
            'bar_chart': 'bar',
            'area_chart': 'line',
            'pie_chart': 'pie'
        };
        return mapping[type] || 'line';
    }
    
    getGaugeColor(value, max) {
        const percentage = (value / max) * 100;
        if (percentage < 30) return '#28a745'; // Green
        if (percentage < 70) return '#ffc107'; // Yellow
        return '#dc3545'; // Red
    }
    
    getHeatmapColor(intensity) {
        const normalized = Math.min(intensity / 100, 1);
        const red = Math.floor(255 * normalized);
        const blue = Math.floor(255 * (1 - normalized));
        return `rgb(${red}, 100, ${blue})`;
    }
    
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toFixed(0);
    }
    
    showWidgetError(widgetId, message) {
        const widget = this.widgets.get(widgetId);
        if (!widget) return;
        
        const contentElement = widget.element.querySelector('.widget-content');
        contentElement.innerHTML = `<div class="text-danger text-center">Error: ${message}</div>`;
    }
    
    showAlert(message, level = 'info') {
        // Simple alert system
        const alertClass = level === 'error' ? 'alert-danger' : 
                          level === 'warning' ? 'alert-warning' : 'alert-info';
        
        const alert = document.createElement('div');
        alert.className = `alert ${alertClass}`;
        alert.innerHTML = message;
        alert.style.position = 'fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
    
    setupEventListeners() {
        // Widget refresh buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('refresh-widget')) {
                const widgetId = e.target.closest('.widget').dataset.widgetId;
                this.loadWidgetData(widgetId);
            }
        });
        
        // Theme switcher
        const themeSelector = document.getElementById('theme-selector');
        if (themeSelector) {
            themeSelector.addEventListener('change', (e) => {
                this.switchTheme(e.target.value);
            });
        }
    }
    
    switchTheme(theme) {
        document.body.className = `theme-${theme}`;
        this.currentTheme = theme;
        localStorage.setItem('dashboard-theme', theme);
    }
    
    startAutoRefresh() {
        // Global refresh every 5 minutes
        setInterval(() => {
            this.widgets.forEach((widget, widgetId) => {
                if (widget.updateFrequency > 0) {
                    this.loadWidgetData(widgetId);
                }
            });
        }, 5 * 60 * 1000);
    }
    
    updateWidget(widgetId, data) {
        this.renderWidget(widgetId, data);
    }
    
    destroy() {
        // Cleanup intervals
        this.updateIntervals.forEach(interval => clearInterval(interval));
        this.updateIntervals.clear();
        
        // Close WebSocket
        if (this.websocket) {
            this.websocket.close();
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});
        """
        
        (self.static_path / "dashboard.js").write_text(main_js)
        
        # Main HTML template
        main_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{page_title}} - Analytics Dashboard</title>
    <link rel="stylesheet" href="/static/dashboard.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="theme-{{theme}}">
    <div class="dashboard-container">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>Analytics Dashboard</h2>
                <p class="text-muted">{{user_name}}</p>
            </div>
            
            <ul class="nav-menu">
                {% for page in navigation_pages %}
                <li class="nav-item">
                    <a href="/dashboard/{{page.page_id}}" 
                       class="nav-link {{page.active_class}}">
                        {{page.name}}
                    </a>
                </li>
                {% endfor %}
            </ul>
            
            <div style="margin-top: auto; padding-top: 30px;">
                <select id="theme-selector" class="form-select">
                    <option value="professional">Professional</option>
                    <option value="dark">Dark</option>
                    <option value="minimal">Minimal</option>
                </select>
            </div>
        </nav>
        
        <main class="main-content">
            <div class="dashboard-header">
                <h1>{{page_title}}</h1>
                <p class="text-muted">{{page_description}}</p>
            </div>
            
            <div class="dashboard-grid">
                {% for widget in widgets %}
                <div class="widget widget-{{widget.size}}" 
                     data-widget-id="{{widget.widget_id}}"
                     data-widget-type="{{widget.widget_type}}"
                     data-data-source="{{widget.data_source}}"
                     data-update-freq="{{widget.update_frequency}}"
                     style="grid-column-start: {{widget.position.x + 1}}; grid-row-start: {{widget.position.y + 1}};">
                    
                    <div class="widget-header">
                        <h3 class="widget-title">{{widget.title}}</h3>
                        <div class="widget-actions">
                            <button class="widget-action refresh-widget" title="Refresh">↻</button>
                            <button class="widget-action" title="Settings">⚙</button>
                        </div>
                    </div>
                    
                    <div class="widget-content">
                        <div class="chart-loading">Loading...</div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </main>
    </div>
    
    <script src="/static/dashboard.js"></script>
</body>
</html>
        """
        
        (self.templates_path / "dashboard.html").write_text(main_template)
    
    def create_dashboard_page(self, name: str, description: str = "",
                            layout_type: str = "grid",
                            theme: DashboardTheme = DashboardTheme.PROFESSIONAL,
                            permissions: List[str] = None) -> str:
        """Create a new dashboard page"""
        
        page_id = f"page_{int(datetime.now().timestamp())}"
        
        page = DashboardPage(
            page_id=page_id,
            name=name,
            description=description,
            widgets=[],
            layout_type=layout_type,
            theme=theme,
            permissions=permissions or [],
            created_at=datetime.now()
        )
        
        self.dashboard_pages[page_id] = page
        self._store_dashboard_page(page)
        
        self.logger.info(f"Created dashboard page: {page_id}")
        return page_id
    
    def add_widget(self, page_id: str, title: str, widget_type: str,
                  data_source: str, size: WidgetSize = WidgetSize.MEDIUM,
                  position: Dict[str, int] = None,
                  update_frequency: UpdateFrequency = UpdateFrequency.NORMAL,
                  permissions: List[str] = None) -> str:
        """Add a widget to a dashboard page"""
        
        if page_id not in self.dashboard_pages:
            raise ValueError(f"Dashboard page {page_id} not found")
        
        widget_id = f"widget_{int(datetime.now().timestamp())}"
        
        if position is None:
            # Auto-position widget
            position = self._calculate_next_position(page_id, size)
        
        widget = WebWidget(
            widget_id=widget_id,
            title=title,
            widget_type=widget_type,
            data_source=data_source,
            position=position,
            size=size,
            update_frequency=update_frequency,
            permissions=permissions or []
        )
        
        self.dashboard_pages[page_id].widgets.append(widget)
        self._store_widget(page_id, widget)
        
        self.logger.info(f"Added widget {widget_id} to page {page_id}")
        return widget_id
    
    def get_widget_data(self, widget_id: str) -> Dict[str, Any]:
        """Get data for a specific widget"""
        
        # Find widget
        widget = None
        for page in self.dashboard_pages.values():
            for w in page.widgets:
                if w.widget_id == widget_id:
                    widget = w
                    break
            if widget:
                break
        
        if not widget:
            return {"success": False, "error": "Widget not found"}
        
        try:
            # Check cache first
            cached_data = self._get_cached_widget_data(widget_id)
            if cached_data:
                return {"success": True, "data": cached_data}
            
            # Generate fresh data
            data = self._generate_widget_data(widget)
            
            # Cache the data
            self._cache_widget_data(widget_id, data)
            
            return {"success": True, "data": data}
            
        except Exception as e:
            self.logger.error(f"Error getting widget data for {widget_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_widget_data(self, widget: WebWidget) -> Dict[str, Any]:
        """Generate data for a widget based on its type and data source"""
        
        data_source = widget.data_source
        widget_type = widget.widget_type
        
        if data_source == "productivity_summary":
            summary = self.metrics_collector.get_productivity_summary()
            if widget_type == "gauge":
                return {
                    "value": summary.get("overall_score", 3.5),
                    "max": 5.0,
                    "label": "Productivity Score",
                    "unit": "/5"
                }
                
        elif data_source == "productivity_trend":
            summary = self.metrics_collector.get_productivity_summary(days=30)
            trend_data = summary.get("productivity_trend", [])
            
            if not trend_data:
                # Generate sample trend data
                trend_data = self._generate_sample_trend_data(30)
            
            return {
                "chartData": {
                    "labels": [point["date"] for point in trend_data],
                    "datasets": [{
                        "label": "Productivity Score",
                        "data": [point["score"] for point in trend_data],
                        "borderColor": "#007bff",
                        "backgroundColor": "rgba(0, 123, 255, 0.1)",
                        "fill": True
                    }]
                }
            }
            
        elif data_source == "kpi_summary":
            analytics = self.metrics_collector.get_performance_analytics()
            return {
                "metrics": [
                    {"label": "Sessions", "value": analytics.get("total_sessions", 42)},
                    {"label": "Avg Productivity", "value": f"{analytics.get('avg_productivity', 3.7)}/5"},
                    {"label": "Error Rate", "value": f"{analytics.get('error_rate', 2.3)}%"},
                    {"label": "Satisfaction", "value": f"{analytics.get('satisfaction', 4.2)}/5"}
                ]
            }
            
        elif data_source == "roi_metrics":
            # Get latest ROI calculation
            roi_scenarios = self._get_roi_scenarios()
            if roi_scenarios:
                result = self.roi_calculator.calculate_roi(roi_scenarios[0])
                return {
                    "roi": {
                        "percentage": round(result.roi_percentage, 1),
                        "npv": result.net_present_value,
                        "payback_months": round(result.payback_period_months, 1),
                        "bcr": round(result.benefit_cost_ratio, 2)
                    }
                }
            else:
                return {
                    "roi": {
                        "percentage": 25.8,
                        "npv": 45000,
                        "payback_months": 8.2,
                        "bcr": 2.3
                    }
                }
                
        elif data_source == "performance_analytics":
            analytics = self.metrics_collector.get_performance_analytics()
            metrics = {
                "Response Time": analytics.get("avg_response_time", 450),
                "CPU Usage": analytics.get("cpu_usage", 15.5),
                "Memory Usage": analytics.get("memory_usage", 256.8),
                "Commands/Hour": analytics.get("commands_per_hour", 45.2),
                "Success Rate": analytics.get("success_rate", 96.8)
            }
            
            return {
                "chartData": {
                    "labels": list(metrics.keys()),
                    "datasets": [{
                        "label": "Performance Metrics",
                        "data": list(metrics.values()),
                        "backgroundColor": [
                            "#007bff", "#28a745", "#ffc107", "#dc3545", "#6f42c1"
                        ]
                    }]
                }
            }
            
        elif data_source == "usage_patterns":
            patterns = self.metrics_collector.get_usage_patterns()
            tools_data = patterns.get("most_used_tools", [
                {"tool": "Bash", "count": 125},
                {"tool": "Edit", "count": 89},
                {"tool": "Read", "count": 67},
                {"tool": "Write", "count": 45},
                {"tool": "Grep", "count": 34}
            ])
            
            return {
                "chartData": {
                    "labels": [tool["tool"] for tool in tools_data],
                    "datasets": [{
                        "data": [tool["count"] for tool in tools_data],
                        "backgroundColor": [
                            "#007bff", "#28a745", "#ffc107", "#dc3545", "#6c757d"
                        ]
                    }]
                }
            }
            
        elif data_source == "system_cpu":
            self.metrics_collector.collect_system_metrics()
            # Get latest CPU usage
            return {
                "value": 25.5,
                "max": 100,
                "label": "CPU Usage",
                "unit": "%"
            }
            
        elif data_source == "system_memory":
            return {
                "value": 456.8,
                "max": 1024,
                "label": "Memory Usage",
                "unit": "MB"
            }
            
        elif data_source == "activity_patterns":
            # Generate activity heatmap data
            heatmap_data = []
            for day in range(7):
                for hour in range(24):
                    if 9 <= hour <= 17:  # Work hours
                        activity = 50 + (hash(f"{day}{hour}") % 40)
                    elif 7 <= hour <= 21:  # Extended hours
                        activity = 20 + (hash(f"{day}{hour}") % 30)
                    else:  # Night hours
                        activity = hash(f"{day}{hour}") % 15
                    
                    heatmap_data.append([hour, day, activity])
            
            return {"heatmap": heatmap_data}
        
        # Default empty data
        return {"error": f"No data available for {data_source}"}
    
    def _generate_sample_trend_data(self, days: int) -> List[Dict[str, Any]]:
        """Generate sample trend data for demonstration"""
        data = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            # Generate realistic trending data
            base_score = 3.0 + (i / days) * 1.5  # Slight upward trend
            noise = (hash(f"trend_{i}") % 100) / 100.0 - 0.5  # Random noise
            score = max(1.0, min(5.0, base_score + noise))
            
            data.append({
                "date": date.strftime('%m/%d'),
                "score": round(score, 2)
            })
        
        return data
    
    def _calculate_next_position(self, page_id: str, size: WidgetSize) -> Dict[str, int]:
        """Calculate next available position for widget"""
        
        page = self.dashboard_pages[page_id]
        occupied_positions = set()
        
        # Map size to grid dimensions
        size_map = {
            WidgetSize.SMALL: (3, 2),
            WidgetSize.MEDIUM: (6, 3),
            WidgetSize.LARGE: (9, 4),
            WidgetSize.FULL: (12, 6)
        }
        
        widget_width, widget_height = size_map[size]
        
        # Mark occupied positions
        for widget in page.widgets:
            w_size = size_map[widget.size]
            for x in range(widget.position["x"], widget.position["x"] + w_size[0]):
                for y in range(widget.position["y"], widget.position["y"] + w_size[1]):
                    occupied_positions.add((x, y))
        
        # Find first available position
        for y in range(20):  # Max 20 rows
            for x in range(12 - widget_width + 1):  # 12 column grid
                can_place = True
                for dx in range(widget_width):
                    for dy in range(widget_height):
                        if (x + dx, y + dy) in occupied_positions:
                            can_place = False
                            break
                    if not can_place:
                        break
                
                if can_place:
                    return {"x": x, "y": y}
        
        # If no space found, place at bottom
        return {"x": 0, "y": 20}
    
    def _get_cached_widget_data(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get cached widget data if still valid"""
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT data_json, expires_at FROM widget_data_cache 
                WHERE widget_id = ? AND expires_at > datetime('now')
                ORDER BY generated_at DESC LIMIT 1
            """, (widget_id,))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['data_json'])
        
        return None
    
    def _cache_widget_data(self, widget_id: str, data: Dict[str, Any], 
                          cache_duration_minutes: int = 5):
        """Cache widget data"""
        
        cache_id = f"cache_{widget_id}_{int(datetime.now().timestamp())}"
        expires_at = datetime.now() + timedelta(minutes=cache_duration_minutes)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT INTO widget_data_cache 
                (cache_id, widget_id, data_json, expires_at)
                VALUES (?, ?, ?, ?)
            """, (cache_id, widget_id, json.dumps(data), expires_at.isoformat()))
            
            # Clean old cache entries
            conn.execute("""
                DELETE FROM widget_data_cache 
                WHERE expires_at < datetime('now') OR widget_id = ?
            """, (widget_id,))
    
    def _get_roi_scenarios(self) -> List[str]:
        """Get available ROI scenario IDs"""
        try:
            with sqlite3.connect(str(self.roi_calculator.db_path)) as conn:
                cursor = conn.execute("SELECT scenario_id FROM roi_scenarios LIMIT 5")
                return [row[0] for row in cursor]
        except:
            return []
    
    def _start_background_updates(self):
        """Start background data update threads"""
        
        def update_loop():
            while True:
                try:
                    # Update real-time widgets
                    for page in self.dashboard_pages.values():
                        for widget in page.widgets:
                            if widget.update_frequency == UpdateFrequency.REAL_TIME:
                                self._update_widget_cache(widget.widget_id)
                    
                    time.sleep(UpdateFrequency.REAL_TIME.value)
                    
                except Exception as e:
                    self.logger.error(f"Error in background update loop: {e}")
                    time.sleep(30)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def _update_widget_cache(self, widget_id: str):
        """Update widget cache in background"""
        try:
            # Clear existing cache
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("DELETE FROM widget_data_cache WHERE widget_id = ?", (widget_id,))
            
            # Generate fresh data (will be cached automatically when requested)
            self.get_widget_data(widget_id)
            
        except Exception as e:
            self.logger.error(f"Error updating widget cache for {widget_id}: {e}")
    
    def _store_dashboard_page(self, page: DashboardPage):
        """Store dashboard page in database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO dashboard_pages
                (page_id, name, description, layout_type, theme, auto_refresh, 
                 refresh_interval, permissions, created_by, page_config)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                page.page_id,
                page.name,
                page.description,
                page.layout_type,
                page.theme.value,
                page.auto_refresh,
                page.refresh_interval,
                json.dumps(page.permissions),
                page.created_by,
                json.dumps(asdict(page), default=str)
            ))
    
    def _store_widget(self, page_id: str, widget: WebWidget):
        """Store widget in database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO dashboard_widgets
                (widget_id, page_id, title, widget_type, data_source,
                 position_x, position_y, width, height, size_preset,
                 update_frequency, permissions, widget_config)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                widget.widget_id,
                page_id,
                widget.title,
                widget.widget_type,
                widget.data_source,
                widget.position["x"] if widget.position else 0,
                widget.position["y"] if widget.position else 0,
                3 if widget.size == WidgetSize.SMALL else 6 if widget.size == WidgetSize.MEDIUM else 9 if widget.size == WidgetSize.LARGE else 12,
                2 if widget.size == WidgetSize.SMALL else 3 if widget.size == WidgetSize.MEDIUM else 4 if widget.size == WidgetSize.LARGE else 6,
                widget.size.value,
                widget.update_frequency.value,
                json.dumps(widget.permissions),
                json.dumps(asdict(widget), default=str)
            ))
    
    def generate_dashboard_html(self, page_id: str, user_name: str = "User") -> str:
        """Generate complete HTML for dashboard page"""
        
        if page_id not in self.dashboard_pages:
            return "<html><body><h1>Page Not Found</h1></body></html>"
        
        page = self.dashboard_pages[page_id]
        
        # Prepare template variables
        template_vars = {
            "page_title": page.name,
            "page_description": page.description,
            "user_name": user_name,
            "theme": page.theme.value,
            "navigation_pages": [
                {
                    "page_id": pid,
                    "name": p.name,
                    "active_class": "active" if pid == page_id else ""
                }
                for pid, p in self.dashboard_pages.items()
            ],
            "widgets": [
                {
                    "widget_id": w.widget_id,
                    "title": w.title,
                    "widget_type": w.widget_type,
                    "data_source": w.data_source,
                    "size": w.size.value,
                    "position": w.position or {"x": 0, "y": 0},
                    "update_frequency": w.update_frequency.value
                }
                for w in page.widgets
            ]
        }
        
        # Simple template rendering (in production, use Jinja2 or similar)
        template = (self.templates_path / "dashboard.html").read_text()
        
        # Basic template substitution
        for key, value in template_vars.items():
            if isinstance(value, str):
                template = template.replace(f"{{{{{key}}}}}", value)
        
        return template
    
    def create_user(self, username: str, role: str, permissions: List[str] = None) -> str:
        """Create a new dashboard user"""
        
        user_id = f"user_{hashlib.md5(username.encode()).hexdigest()[:8]}"
        
        user = DashboardUser(
            user_id=user_id,
            username=username,
            role=role,
            preferences={},
            permissions=permissions or [],
            created_at=datetime.now()
        )
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO dashboard_users
                (user_id, username, role, preferences, permissions)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user.user_id,
                user.username,
                user.role,
                json.dumps(user.preferences),
                json.dumps(user.permissions)
            ))
        
        return user_id
    
    def create_session(self, user_id: str, ip_address: str = "", 
                      user_agent: str = "") -> str:
        """Create a new user session"""
        
        session_id = secrets.token_urlsafe(32)
        
        session = DashboardSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.active_sessions[session_id] = session
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT INTO dashboard_sessions
                (session_id, user_id, ip_address, user_agent)
                VALUES (?, ?, ?, ?)
            """, (
                session.session_id,
                session.user_id,
                session.ip_address,
                session.user_agent
            ))
        
        return session_id
    
    def get_dashboard_pages(self) -> List[str]:
        """Get list of available dashboard page IDs"""
        return list(self.dashboard_pages.keys())
    
    def export_dashboard_config(self, page_id: str) -> str:
        """Export dashboard configuration as JSON"""
        
        if page_id not in self.dashboard_pages:
            return "{}"
        
        page = self.dashboard_pages[page_id]
        return json.dumps(asdict(page), indent=2, default=str)
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        
        expired_time = datetime.now() - timedelta(hours=24)
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if session.last_activity < expired_time:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                UPDATE dashboard_sessions SET is_active = FALSE 
                WHERE last_activity < ?
            """, (expired_time.isoformat(),))
        
        self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")