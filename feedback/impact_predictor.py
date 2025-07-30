"""
Impact Predictor

Predict effects of configuration changes with intelligent analysis.
Uses machine learning and historical data to forecast productivity impact, 
potential issues, and optimization opportunities.
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import logging
import statistics

@dataclass
class ImpactPrediction:
    """Predicted impact of a configuration change"""
    category: str
    metric: str
    current_value: float
    predicted_value: float
    confidence: float
    timeframe_days: int
    explanation: str
    contributing_factors: List[str]

@dataclass
class ChangeImpactAnalysis:
    """Comprehensive analysis of configuration change impact"""
    overall_impact_score: float  # -1 to 1 (negative = worse, positive = better)
    productivity_predictions: List[ImpactPrediction]
    performance_predictions: List[ImpactPrediction]
    security_predictions: List[ImpactPrediction]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    rollback_recommendation: bool
    success_probability: float

@dataclass
class ConfigurationChange:
    """Represents a configuration change for impact analysis"""
    change_type: str  # 'add', 'remove', 'modify'
    component_type: str  # 'agent', 'hook', 'command', 'setting'
    old_config: Optional[Dict]
    new_config: Dict
    context: Dict

class ImpactPredictor:
    """Advanced predictor for configuration change impacts"""
    
    def __init__(self, performance_db=None, patterns_db=None):
        self.logger = logging.getLogger(__name__)
        self.performance_db = performance_db
        self.patterns_db = patterns_db
        
        # Impact models and weights
        self.impact_models = {
            'productivity': {
                'agent_addition': 0.15,
                'hook_automation': 0.25,
                'command_efficiency': 0.10,
                'tool_permission_restriction': -0.05,
                'complexity_increase': -0.08
            },
            'performance': {
                'agent_count_increase': -0.02,
                'hook_count_increase': -0.01,
                'command_optimization': 0.08,
                'validation_overhead': -0.03,
                'caching_improvement': 0.12
            },
            'security': {
                'permission_restriction': 0.20,
                'dangerous_command_removal': 0.30,
                'secret_exposure': -0.40,
                'tool_access_expansion': -0.10,
                'validation_addition': 0.15
            }
        }
        
        # Baseline metrics for comparison
        self.baseline_metrics = {
            'setup_time_seconds': 60,
            'daily_commits': 5,
            'error_frequency': 0.1,
            'satisfaction_rating': 0.7,
            'security_score': 0.8
        }
        
        # Risk factors
        self.risk_factors = {
            'high_complexity': {
                'threshold': 0.8,
                'impact_multiplier': 1.5,
                'description': 'Complex configurations are harder to maintain'
            },
            'many_dependencies': {
                'threshold': 10,
                'impact_multiplier': 1.2,
                'description': 'Many tool dependencies increase failure risk'
            },
            'broad_permissions': {
                'threshold': 0.9,
                'impact_multiplier': 1.3,
                'description': 'Broad tool permissions increase security risk'
            }
        }
    
    def predict_change_impact(self, change: ConfigurationChange, 
                            current_config: Dict, project_context: Dict = None) -> ChangeImpactAnalysis:
        """Predict comprehensive impact of a configuration change"""
        self.logger.info(f"Predicting impact of {change.change_type} {change.component_type}")
        
        # Analyze the specific change
        productivity_predictions = self._predict_productivity_impact(change, current_config, project_context)
        performance_predictions = self._predict_performance_impact(change, current_config, project_context)
        security_predictions = self._predict_security_impact(change, current_config, project_context)
        
        # Calculate overall impact score
        overall_impact_score = self._calculate_overall_impact(
            productivity_predictions, performance_predictions, security_predictions
        )
        
        # Assess risks
        risk_assessment = self._assess_risks(change, current_config, project_context)
        
        # Generate recommendations
        recommendations = self._generate_impact_recommendations(
            productivity_predictions, performance_predictions, security_predictions, risk_assessment
        )
        
        # Determine rollback recommendation
        rollback_recommendation = self._should_recommend_rollback(
            overall_impact_score, risk_assessment
        )
        
        # Calculate success probability
        success_probability = self._calculate_success_probability(
            change, overall_impact_score, risk_assessment
        )
        
        analysis = ChangeImpactAnalysis(
            overall_impact_score=overall_impact_score,
            productivity_predictions=productivity_predictions,
            performance_predictions=performance_predictions,
            security_predictions=security_predictions,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            rollback_recommendation=rollback_recommendation,
            success_probability=success_probability
        )
        
        self.logger.info(f"Impact prediction complete: {overall_impact_score:.2f} overall score")
        return analysis
    
    def _predict_productivity_impact(self, change: ConfigurationChange, 
                                   current_config: Dict, project_context: Dict) -> List[ImpactPrediction]:
        """Predict productivity impact of configuration change"""
        predictions = []
        
        if change.component_type == 'agent':
            if change.change_type == 'add':
                # Adding agent generally improves productivity
                agent_config = change.new_config
                agent_type = agent_config.get('type', 'general')
                
                impact_magnitude = self._get_agent_productivity_impact(agent_type)
                current_commits = self.baseline_metrics['daily_commits']
                predicted_commits = current_commits * (1 + impact_magnitude)
                
                predictions.append(ImpactPrediction(
                    category='productivity',
                    metric='daily_commits',
                    current_value=current_commits,
                    predicted_value=predicted_commits,
                    confidence=0.75 if self._has_historical_data(agent_type) else 0.60,
                    timeframe_days=14,
                    explanation=f"Adding {agent_type} agent typically improves development velocity",
                    contributing_factors=[
                        f"Agent specialization: {agent_type}",
                        "Automated assistance reduces manual effort",
                        "Consistent code quality improvements"
                    ]
                ))
        
        elif change.component_type == 'hook':
            if change.change_type == 'add':
                # Adding automation hooks improves productivity
                hook_config = change.new_config
                hook_actions = len(hook_config.get('actions', []))
                
                impact_magnitude = min(0.3, hook_actions * 0.1)  # Cap at 30% improvement
                current_commits = self.baseline_metrics['daily_commits']
                predicted_commits = current_commits * (1 + impact_magnitude)
                
                predictions.append(ImpactPrediction(
                    category='productivity',
                    metric='daily_commits',
                    current_value=current_commits,
                    predicted_value=predicted_commits,
                    confidence=0.80,
                    timeframe_days=7,
                    explanation="Automation hooks reduce manual task overhead",
                    contributing_factors=[
                        f"Automates {hook_actions} development tasks",
                        "Eliminates context switching",
                        "Reduces manual errors"
                    ]
                ))
                
                # Error frequency reduction through automation
                current_errors = self.baseline_metrics['error_frequency']
                predicted_errors = current_errors * 0.7  # 30% reduction
                
                predictions.append(ImpactPrediction(
                    category='productivity',
                    metric='error_frequency',
                    current_value=current_errors,
                    predicted_value=predicted_errors,
                    confidence=0.85,
                    timeframe_days=14,
                    explanation="Automated validation reduces human errors",
                    contributing_factors=[
                        "Consistent application of quality checks",
                        "Immediate feedback on issues",
                        "Prevention of common mistakes"
                    ]
                ))
        
        elif change.component_type == 'command':
            if change.change_type == 'add':
                # Adding commands provides efficiency gains
                command_config = change.new_config
                command_complexity = len(command_config.get('command', '').split())
                
                # More complex commands typically provide bigger efficiency gains
                impact_magnitude = min(0.15, command_complexity * 0.01)
                current_efficiency = 1.0
                predicted_efficiency = current_efficiency * (1 + impact_magnitude)
                
                predictions.append(ImpactPrediction(
                    category='productivity',
                    metric='task_efficiency',
                    current_value=current_efficiency,
                    predicted_value=predicted_efficiency,
                    confidence=0.70,
                    timeframe_days=3,
                    explanation="Custom commands streamline repetitive tasks",
                    contributing_factors=[
                        "Reduces command-line complexity",
                        "Standardizes common operations",
                        "Improves team consistency"
                    ]
                ))
        
        return predictions
    
    def _predict_performance_impact(self, change: ConfigurationChange,
                                  current_config: Dict, project_context: Dict) -> List[ImpactPrediction]:
        """Predict performance impact of configuration change"""
        predictions = []
        
        # Count current components for overhead calculations
        current_agents = len(current_config.get('agents', []))
        current_hooks = len(current_config.get('hooks', []))
        
        if change.component_type == 'agent' and change.change_type == 'add':
            # Adding agents increases processing overhead
            current_setup_time = self.baseline_metrics['setup_time_seconds']
            overhead_per_agent = 2  # seconds per agent
            predicted_setup_time = current_setup_time + overhead_per_agent
            
            predictions.append(ImpactPrediction(
                category='performance',
                metric='setup_time_seconds',
                current_value=current_setup_time,
                predicted_value=predicted_setup_time,
                confidence=0.90,
                timeframe_days=1,
                explanation="Additional agents increase initialization time",
                contributing_factors=[
                    f"Agent count increasing from {current_agents} to {current_agents + 1}",
                    "Each agent requires processing overhead",
                    "Linear scaling of setup time"
                ]
            ))
        
        elif change.component_type == 'hook' and change.change_type == 'add':
            # Adding hooks increases processing time
            hook_config = change.new_config
            hook_actions = len(hook_config.get('actions', []))
            
            current_setup_time = self.baseline_metrics['setup_time_seconds']
            overhead_per_hook = hook_actions * 1.5  # seconds per action
            predicted_setup_time = current_setup_time + overhead_per_hook
            
            predictions.append(ImpactPrediction(
                category='performance',
                metric='setup_time_seconds',
                current_value=current_setup_time,
                predicted_value=predicted_setup_time,
                confidence=0.85,
                timeframe_days=1,
                explanation="Hook execution adds processing overhead",
                contributing_factors=[
                    f"Hook with {hook_actions} actions",
                    "Each action requires execution time",
                    "I/O operations for file processing"
                ]
            ))
            
            # But hooks can improve runtime performance through optimization
            if any('format' in str(action).lower() for action in hook_config.get('actions', [])):
                predictions.append(ImpactPrediction(
                    category='performance',
                    metric='code_quality_score',
                    current_value=0.7,
                    predicted_value=0.85,
                    confidence=0.80,
                    timeframe_days=7,
                    explanation="Automated formatting improves code quality",
                    contributing_factors=[
                        "Consistent code formatting",
                        "Automated style enforcement",
                        "Reduced code review overhead"
                    ]
                ))
        
        elif change.component_type == 'setting':
            # Settings changes can have various performance impacts
            setting_path = change.context.get('setting_path', '')
            
            if 'permissions' in setting_path:
                # Permission changes affect validation overhead
                if change.change_type == 'modify' and change.old_config:
                    old_perms = len(str(change.old_config))
                    new_perms = len(str(change.new_config))
                    
                    if new_perms > old_perms:
                        # More restrictive permissions increase validation time
                        current_setup_time = self.baseline_metrics['setup_time_seconds']
                        predicted_setup_time = current_setup_time * 1.1
                        
                        predictions.append(ImpactPrediction(
                            category='performance',
                            metric='setup_time_seconds',
                            current_value=current_setup_time,
                            predicted_value=predicted_setup_time,
                            confidence=0.75,
                            timeframe_days=1,
                            explanation="More restrictive permissions increase validation overhead",
                            contributing_factors=[
                                "Additional permission checks",
                                "More complex validation logic",
                                "Security overhead"
                            ]
                        ))
        
        return predictions
    
    def _predict_security_impact(self, change: ConfigurationChange,
                               current_config: Dict, project_context: Dict) -> List[ImpactPrediction]:
        """Predict security impact of configuration change"""
        predictions = []
        
        current_security_score = self.baseline_metrics['security_score']
        
        if change.component_type == 'setting' and 'permissions' in change.context.get('setting_path', ''):
            if change.change_type == 'modify':
                # Analyze permission changes
                old_perms = change.old_config or {}
                new_perms = change.new_config
                
                # Check if permissions are becoming more restrictive
                security_improvement = self._calculate_permission_security_change(old_perms, new_perms)
                predicted_security_score = min(1.0, current_security_score + security_improvement)
                
                predictions.append(ImpactPrediction(
                    category='security',
                    metric='security_score',
                    current_value=current_security_score,
                    predicted_value=predicted_security_score,
                    confidence=0.85,
                    timeframe_days=1,
                    explanation="Permission changes affect security posture",
                    contributing_factors=[
                        "Tool access control modifications",
                        "Command execution restrictions",
                        "Attack surface changes"
                    ]
                ))
        
        elif change.component_type == 'hook':
            if change.change_type == 'add':
                hook_config = change.new_config
                
                # Security-focused hooks improve security
                if any('security' in str(action).lower() or 'audit' in str(action).lower() 
                      for action in hook_config.get('actions', [])):
                    predicted_security_score = min(1.0, current_security_score + 0.1)
                    
                    predictions.append(ImpactPrediction(
                        category='security',
                        metric='security_score',
                        current_value=current_security_score,
                        predicted_value=predicted_security_score,
                        confidence=0.80,
                        timeframe_days=7,
                        explanation="Security automation hooks improve security posture",
                        contributing_factors=[
                            "Automated security checks",
                            "Consistent security validation",
                            "Early detection of issues"
                        ]
                    ))
                
                # Check for potentially dangerous commands in hooks
                dangerous_commands = self._detect_dangerous_commands(hook_config)
                if dangerous_commands:
                    predicted_security_score = max(0.0, current_security_score - 0.2)
                    
                    predictions.append(ImpactPrediction(
                        category='security',
                        metric='security_score',
                        current_value=current_security_score,
                        predicted_value=predicted_security_score,
                        confidence=0.95,
                        timeframe_days=1,
                        explanation="Hook contains potentially dangerous commands",
                        contributing_factors=[
                            f"Dangerous commands detected: {', '.join(dangerous_commands)}",
                            "Increased attack surface",
                            "Potential for privilege escalation"
                        ]
                    ))
        
        elif change.component_type == 'agent':
            if change.change_type == 'add':
                agent_config = change.new_config
                agent_type = agent_config.get('type', 'general')
                
                # Security-focused agents improve security
                if agent_type == 'security_auditor':
                    predicted_security_score = min(1.0, current_security_score + 0.15)
                    
                    predictions.append(ImpactPrediction(
                        category='security',
                        metric='security_score',
                        current_value=current_security_score,
                        predicted_value=predicted_security_score,
                        confidence=0.80,
                        timeframe_days=14,
                        explanation="Security auditor agent enhances security monitoring",
                        contributing_factors=[
                            "Automated security code review",
                            "Vulnerability detection",
                            "Security best practice enforcement"
                        ]
                    ))
        
        return predictions
    
    def _calculate_overall_impact(self, productivity_preds: List[ImpactPrediction],
                                performance_preds: List[ImpactPrediction],
                                security_preds: List[ImpactPrediction]) -> float:
        """Calculate overall impact score from all predictions"""
        
        # Weights for different categories
        weights = {
            'productivity': 0.4,
            'performance': 0.3,
            'security': 0.3
        }
        
        category_scores = {}
        
        # Calculate productivity score
        if productivity_preds:
            prod_impacts = []
            for pred in productivity_preds:
                if pred.current_value != 0:
                    relative_change = (pred.predicted_value - pred.current_value) / pred.current_value
                    weighted_change = relative_change * pred.confidence
                    prod_impacts.append(weighted_change)
            
            category_scores['productivity'] = statistics.mean(prod_impacts) if prod_impacts else 0.0
        else:
            category_scores['productivity'] = 0.0
        
        # Calculate performance score
        if performance_preds:
            perf_impacts = []
            for pred in performance_preds:
                if pred.current_value != 0:
                    # For performance, lower values are often better (setup time)
                    if 'time' in pred.metric:
                        relative_change = (pred.current_value - pred.predicted_value) / pred.current_value
                    else:
                        relative_change = (pred.predicted_value - pred.current_value) / pred.current_value
                    
                    weighted_change = relative_change * pred.confidence
                    perf_impacts.append(weighted_change)
            
            category_scores['performance'] = statistics.mean(perf_impacts) if perf_impacts else 0.0
        else:
            category_scores['performance'] = 0.0
        
        # Calculate security score
        if security_preds:
            sec_impacts = []
            for pred in security_preds:
                if pred.current_value != 0:
                    relative_change = (pred.predicted_value - pred.current_value) / pred.current_value
                    weighted_change = relative_change * pred.confidence
                    sec_impacts.append(weighted_change)
            
            category_scores['security'] = statistics.mean(sec_impacts) if sec_impacts else 0.0
        else:
            category_scores['security'] = 0.0
        
        # Calculate weighted overall score
        overall_score = sum(score * weights[category] for category, score in category_scores.items())
        
        # Clamp to [-1, 1] range
        return max(-1.0, min(1.0, overall_score))
    
    def _assess_risks(self, change: ConfigurationChange, current_config: Dict,
                     project_context: Dict) -> Dict[str, Any]:
        """Assess risks associated with the configuration change"""
        risks = {
            'high_risk_factors': [],
            'medium_risk_factors': [],
            'low_risk_factors': [],
            'overall_risk_level': 'low'
        }
        
        # Check for high complexity
        if self._calculate_config_complexity(current_config) > self.risk_factors['high_complexity']['threshold']:
            risks['high_risk_factors'].append({
                'factor': 'high_complexity',
                'description': self.risk_factors['high_complexity']['description'],
                'mitigation': 'Consider simplifying configuration or adding comprehensive testing'
            })
        
        # Check for many dependencies
        total_components = sum(len(current_config.get(section, [])) for section in ['agents', 'hooks', 'commands'])
        if total_components > self.risk_factors['many_dependencies']['threshold']:
            risks['medium_risk_factors'].append({
                'factor': 'many_dependencies',
                'description': self.risk_factors['many_dependencies']['description'],
                'mitigation': 'Test thoroughly and have rollback plan ready'
            })
        
        # Check for broad permissions
        permission_breadth = self._calculate_permission_breadth(current_config)
        if permission_breadth > self.risk_factors['broad_permissions']['threshold']:
            risks['high_risk_factors'].append({
                'factor': 'broad_permissions',
                'description': self.risk_factors['broad_permissions']['description'],
                'mitigation': 'Restrict permissions to minimum required for functionality'
            })
        
        # Determine overall risk level
        if risks['high_risk_factors']:
            risks['overall_risk_level'] = 'high'
        elif risks['medium_risk_factors']:
            risks['overall_risk_level'] = 'medium'
        
        return risks
    
    def _generate_impact_recommendations(self, productivity_preds: List[ImpactPrediction],
                                       performance_preds: List[ImpactPrediction],
                                       security_preds: List[ImpactPrediction],
                                       risk_assessment: Dict) -> List[str]:
        """Generate recommendations based on impact predictions"""
        recommendations = []
        
        # Productivity recommendations
        negative_productivity = [p for p in productivity_preds if p.predicted_value < p.current_value]
        if negative_productivity:
            recommendations.append("Monitor productivity metrics closely after deployment")
        
        positive_productivity = [p for p in productivity_preds if p.predicted_value > p.current_value]
        if positive_productivity:
            recommendations.append("Expected productivity improvements - consider measuring actual gains")
        
        # Performance recommendations
        slower_performance = [p for p in performance_preds if 'time' in p.metric and p.predicted_value > p.current_value]
        if slower_performance:
            recommendations.append("Configuration may slow down setup/execution - optimize if necessary")
        
        # Security recommendations
        security_concerns = [p for p in security_preds if p.predicted_value < p.current_value]
        if security_concerns:
            recommendations.append("Security concerns identified - review and address before deployment")
        
        # Risk-based recommendations
        if risk_assessment['overall_risk_level'] == 'high':
            recommendations.append("High risk change - implement comprehensive testing and monitoring")
        elif risk_assessment['overall_risk_level'] == 'medium':
            recommendations.append("Medium risk change - test thoroughly before full deployment")
        
        return recommendations
    
    def _should_recommend_rollback(self, overall_impact_score: float,
                                 risk_assessment: Dict) -> bool:
        """Determine if rollback should be recommended"""
        
        # Recommend rollback for significantly negative impact
        if overall_impact_score < -0.3:
            return True
        
        # Recommend rollback for high risk with negative impact
        if risk_assessment['overall_risk_level'] == 'high' and overall_impact_score < 0:
            return True
        
        # Recommend rollback if there are critical security concerns
        if any('security_score' in str(factor) for factor in risk_assessment['high_risk_factors']):
            return True
        
        return False
    
    def _calculate_success_probability(self, change: ConfigurationChange,
                                     overall_impact_score: float,
                                     risk_assessment: Dict) -> float:
        """Calculate probability of successful change implementation"""
        
        base_probability = 0.8  # Base success rate
        
        # Adjust based on impact score
        if overall_impact_score > 0:
            base_probability += overall_impact_score * 0.1
        else:
            base_probability += overall_impact_score * 0.2  # Negative impact reduces success more
        
        # Adjust based on risk level
        risk_adjustments = {
            'high': -0.3,
            'medium': -0.1,
            'low': 0.0
        }
        
        base_probability += risk_adjustments.get(risk_assessment['overall_risk_level'], 0)
        
        # Adjust based on change type (some changes are inherently riskier)
        change_type_adjustments = {
            ('setting', 'modify'): -0.05,  # Settings changes can be tricky
            ('hook', 'add'): -0.02,        # New automation can fail
            ('agent', 'add'): 0.02,        # Agents are usually safe additions
            ('command', 'add'): 0.05       # Commands are low risk
        }
        
        change_key = (change.component_type, change.change_type)
        base_probability += change_type_adjustments.get(change_key, 0)
        
        # Clamp to [0, 1] range
        return max(0.0, min(1.0, base_probability))
    
    # Helper methods
    
    def _get_agent_productivity_impact(self, agent_type: str) -> float:
        """Get expected productivity impact for agent type"""
        impact_map = {
            'code_reviewer': 0.20,
            'tester': 0.15,
            'formatter': 0.10,
            'security_auditor': 0.18,
            'documentation': 0.12,
            'general': 0.08
        }
        return impact_map.get(agent_type, 0.05)
    
    def _has_historical_data(self, component_type: str) -> bool:
        """Check if we have historical data for this component type"""
        # In a real implementation, this would query the performance database
        return component_type in ['code_reviewer', 'tester', 'formatter']
    
    def _calculate_config_complexity(self, config: Dict) -> float:
        """Calculate configuration complexity score (0-1)"""
        total_components = sum(len(config.get(section, [])) for section in ['agents', 'hooks', 'commands'])
        complexity = min(1.0, total_components / 20)  # Normalize to 0-1
        return complexity
    
    def _calculate_permission_breadth(self, config: Dict) -> float:
        """Calculate how broad the permissions are (0-1)"""
        permissions = config.get('settings', {}).get('tools', {}).get('permissions', {})
        
        if not permissions:
            return 0.0
        
        # Count tools with 'allow' permission
        broad_permissions = sum(1 for perms in permissions.values() 
                              if perms == 'allow' or perms == ['allow'])
        
        total_permissions = len(permissions)
        return broad_permissions / max(1, total_permissions)
    
    def _calculate_permission_security_change(self, old_perms: Dict, new_perms: Dict) -> float:
        """Calculate security impact of permission changes"""
        
        # Simplistic calculation - more restrictive = better security
        old_broad = sum(1 for perms in old_perms.values() if perms == 'allow' or perms == ['allow'])
        new_broad = sum(1 for perms in new_perms.values() if perms == 'allow' or perms == ['allow'])
        
        if old_broad > new_broad:
            return 0.1  # Security improvement
        elif old_broad < new_broad:
            return -0.1  # Security degradation
        else:
            return 0.0  # No change
    
    def _detect_dangerous_commands(self, hook_config: Dict) -> List[str]:
        """Detect potentially dangerous commands in hook configuration"""
        dangerous = []
        
        dangerous_patterns = [
            r'\brm\s+-rf',
            r'\bsudo\s+rm',
            r'\bchmod\s+777',
            r'curl.*\|.*bash',
            r'wget.*\|.*sh'
        ]
        
        for action in hook_config.get('actions', []):
            if action.get('type') == 'command':
                command = action.get('command', '')
                for pattern in dangerous_patterns:
                    if re.search(pattern, command, re.IGNORECASE):
                        dangerous.append(pattern)
        
        return dangerous