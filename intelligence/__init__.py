"""
Intelligence Module

Hyper-intelligence core for context-aware analysis and AI-powered configuration recommendations.
This module provides the foundation for understanding project intent, detecting patterns,
and making intelligent decisions about Claude Code configurations.
"""

from .context_analyzer import ContextAnalyzer
from .intent_detector import IntentDetector
from .pattern_matcher import PatternMatcher
from .team_analyzer import TeamAnalyzer
from .predictive_engine import PredictiveEngine

__all__ = [
    'ContextAnalyzer',
    'IntentDetector', 
    'PatternMatcher',
    'TeamAnalyzer',
    'PredictiveEngine'
]

__version__ = "1.0.0"
__author__ = "Claude Code Intelligence Team"