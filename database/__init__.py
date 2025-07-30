"""
Database Module

Configuration intelligence database for learning patterns and storing successful configurations.
This module provides persistent storage and analytics for configuration patterns, performance metrics,
and team insights.
"""

from .config_patterns import ConfigPatternsDB
from .performance_metrics import PerformanceMetricsDB
from .team_insights import TeamInsightsDB
from .security_intelligence import SecurityIntelligenceDB

__all__ = [
    'ConfigPatternsDB',
    'PerformanceMetricsDB', 
    'TeamInsightsDB',
    'SecurityIntelligenceDB'
]

__version__ = "1.0.0"
__author__ = "Claude Code Intelligence Team"