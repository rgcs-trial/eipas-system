"""
Interface Module

Revolutionary user experience with conversational setup and intelligent feedback.
This module provides natural language processing, visual configuration building,
and real-time validation for the ultimate configuration experience.
"""

from .natural_language_processor import NaturalLanguageProcessor
from .visual_builder import VisualBuilder
from .live_preview import LivePreview
from .explanation_engine import ExplanationEngine

__all__ = [
    'NaturalLanguageProcessor',
    'VisualBuilder',
    'LivePreview', 
    'ExplanationEngine'
]

__version__ = "1.0.0"
__author__ = "Claude Code Intelligence Team"