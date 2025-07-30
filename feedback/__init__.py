"""
Feedback Module

Intelligent feedback system with real-time validation and guidance.
This module provides instant validation, impact prediction, optimization suggestions,
and smart rollback capabilities for configuration management.
"""

from .configuration_validator import ConfigurationValidator
from .impact_predictor import ImpactPredictor
from .optimization_suggester import OptimizationSuggester
from .rollback_intelligence import RollbackIntelligence

__all__ = [
    'ConfigurationValidator',
    'ImpactPredictor',
    'OptimizationSuggester', 
    'RollbackIntelligence'
]

__version__ = "1.0.0"
__author__ = "Claude Code Intelligence Team"