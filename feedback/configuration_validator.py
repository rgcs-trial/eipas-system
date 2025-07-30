"""
Configuration Validator

Instant validation with detailed explanations for Claude Code configurations.
Provides comprehensive syntax checking, compatibility validation, and intelligent error reporting.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
import logging
import subprocess

class ValidationLevel(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning" 
    INFO = "info"
    SUCCESS = "success"

@dataclass
class ValidationResult:
    """Result of configuration validation"""
    level: ValidationLevel
    category: str
    message: str
    details: str
    suggestion: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    auto_fixable: bool = False

@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    overall_status: ValidationLevel
    results: List[ValidationResult]
    summary: Dict[str, int]
    performance_score: float
    compatibility_score: float
    security_score: float
    recommendations: List[str]

class ConfigurationValidator:
    """Advanced validator for Claude Code configurations with intelligent feedback"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Validation rules
        self.agent_required_fields = ['name', 'type', 'description']
        self.hook_required_fields = ['event', 'matcher', 'actions']
        self.command_required_fields = ['name', 'description', 'command']
        
        # Tool permission validation
        self.valid_tools = [
            'Bash', 'Edit', 'Read', 'Write', 'Glob', 'Grep', 'WebFetch', 
            'TodoWrite', 'NotebookRead', 'NotebookEdit', 'Task'
        ]
        
        # Hook event validation
        self.valid_hook_events = [
            'PreToolUse', 'PostToolUse', 'UserPromptSubmit', 'ConfigLoad'
        ]
        
        # Security patterns
        self.security_patterns = {
            'dangerous_commands': [
                r'\brm\s+-rf\s+/',
                r'\bsudo\s+rm',
                r'\bchmod\s+777',
                r'>\s*/dev/null\s+2>&1',
                r'\bcurl\s+.*\|\s*bash',
                r'\bwget\s+.*\|\s*sh'
            ],
            'sensitive_paths': [
                r'/etc/',
                r'/root/',
                r'~/.ssh/',
                r'\.env',
                r'\.secret'
            ],
            'api_keys': [
                r'api[_-]?key',
                r'secret[_-]?key',
                r'access[_-]?token',
                r'auth[_-]?token'
            ]
        }
        
        # Performance benchmarks
        self.performance_thresholds = {
            'agent_count': {'warning': 10, 'error': 20},
            'hook_count': {'warning': 15, 'error': 25},
            'command_count': {'warning': 20, 'error': 35},
            'agent_description_length': {'warning': 500, 'error': 1000}
        }
    
    def validate_configuration(self, config: Dict, config_path: Optional[Path] = None) -> ValidationReport:
        """Perform comprehensive validation of Claude Code configuration"""
        self.logger.info("Starting comprehensive configuration validation")
        
        results = []
        
        # Schema validation
        results.extend(self._validate_schema(config))
        
        # Agent validation
        if 'agents' in config:
            results.extend(self._validate_agents(config['agents']))
        
        # Hook validation
        if 'hooks' in config:
            results.extend(self._validate_hooks(config['hooks']))
        
        # Command validation
        if 'commands' in config:
            results.extend(self._validate_commands(config['commands']))
        
        # Settings validation
        if 'settings' in config:
            results.extend(self._validate_settings(config['settings']))
        
        # Security validation
        results.extend(self._validate_security(config))
        
        # Performance validation
        results.extend(self._validate_performance(config))
        
        # Tool availability validation
        results.extend(self._validate_tool_availability(config))
        
        # Generate report
        report = self._generate_validation_report(results, config)
        
        self.logger.info(f"Validation complete: {report.overall_status.value} with {len(results)} findings")
        return report
    
    def _validate_schema(self, config: Dict) -> List[ValidationResult]:
        """Validate basic configuration schema"""
        results = []
        
        # Check if config is valid JSON structure
        if not isinstance(config, dict):
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="schema",
                message="Configuration must be a valid JSON object",
                details="The configuration file does not contain a valid JSON object structure",
                suggestion="Ensure the configuration file is properly formatted JSON"
            ))
            return results
        
        # Check for required top-level structure
        expected_sections = ['agents', 'hooks', 'commands', 'settings']
        present_sections = [section for section in expected_sections if section in config]
        
        if not present_sections:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="schema",
                message="No configuration sections found",
                details="Configuration should contain at least one of: agents, hooks, commands, or settings",
                suggestion="Add at least one configuration section to make the file useful"
            ))
        
        # Validate each section structure
        for section in present_sections:
            if section in ['agents', 'hooks', 'commands']:
                if not isinstance(config[section], list):
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="schema",
                        message=f"Section '{section}' must be an array",
                        details=f"The {section} section should contain an array of {section[:-1]} objects",
                        suggestion=f"Change {section} to an array: \"\" + \"{section}\": [...]",
                        auto_fixable=True
                    ))
            elif section == 'settings':
                if not isinstance(config[section], dict):
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="schema",
                        message="Settings section must be an object",
                        details="The settings section should contain configuration key-value pairs",
                        suggestion="Change settings to an object: \"settings\": {...}",
                        auto_fixable=True
                    ))
        
        return results
    
    def _validate_agents(self, agents: List[Dict]) -> List[ValidationResult]:
        """Validate agent configurations"""
        results = []
        
        if not agents:
            results.append(ValidationResult(
                level=ValidationLevel.INFO,
                category="agents",
                message="No agents configured",
                details="Consider adding agents to help with code review, testing, or other tasks",
                suggestion="Add agents based on your development workflow needs"
            ))
            return results
        
        agent_names = set()
        
        for i, agent in enumerate(agents):
            # Check required fields
            for field in self.agent_required_fields:
                if field not in agent:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="agents",
                        message=f"Agent {i+1} missing required field: {field}",
                        details=f"All agents must have: {', '.join(self.agent_required_fields)}",
                        suggestion=f"Add the missing '{field}' field to agent {i+1}",
                        auto_fixable=True
                    ))
            
            # Check for duplicate names
            if 'name' in agent:
                name = agent['name']
                if name in agent_names:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="agents",
                        message=f"Duplicate agent name: '{name}'",
                        details="Each agent must have a unique name",
                        suggestion=f"Rename one of the agents with name '{name}' to be unique"
                    ))
                else:
                    agent_names.add(name)
            
            # Validate agent type
            if 'type' in agent:
                valid_types = ['code_reviewer', 'tester', 'formatter', 'security_auditor', 'documentation', 'general']
                if agent['type'] not in valid_types:
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        category="agents",
                        message=f"Unknown agent type: '{agent['type']}'",
                        details=f"Recommended types: {', '.join(valid_types)}",
                        suggestion="Use a standard agent type for better integration"
                    ))
            
            # Check description length
            if 'description' in agent:
                desc_length = len(agent['description'])
                if desc_length > self.performance_thresholds['agent_description_length']['error']:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="performance",
                        message=f"Agent '{agent.get('name', i+1)}' description too long ({desc_length} chars)",
                        details="Very long descriptions can impact performance",
                        suggestion="Keep agent descriptions under 500 characters"
                    ))
                elif desc_length > self.performance_thresholds['agent_description_length']['warning']:
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        category="performance",
                        message=f"Agent '{agent.get('name', i+1)}' description is long ({desc_length} chars)",
                        details="Consider shortening the description for better performance",
                        suggestion="Keep descriptions concise and focused"
                    ))
            
            # Validate specializations
            if 'specializations' in agent and isinstance(agent['specializations'], list):
                if len(agent['specializations']) > 10:
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        category="agents",
                        message=f"Agent '{agent.get('name', i+1)}' has many specializations",
                        details="Too many specializations can make agents less focused",
                        suggestion="Limit specializations to 3-5 core areas"
                    ))
        
        return results
    
    def _validate_hooks(self, hooks: List[Dict]) -> List[ValidationResult]:
        """Validate hook configurations"""
        results = []
        
        if not hooks:
            results.append(ValidationResult(
                level=ValidationLevel.INFO,
                category="hooks",
                message="No hooks configured",
                details="Hooks can automate tasks like formatting, testing, and linting",
                suggestion="Consider adding hooks for common development tasks"
            ))
            return results
        
        for i, hook in enumerate(hooks):
            # Check required fields
            for field in self.hook_required_fields:
                if field not in hook:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="hooks",
                        message=f"Hook {i+1} missing required field: {field}",
                        details=f"All hooks must have: {', '.join(self.hook_required_fields)}",
                        suggestion=f"Add the missing '{field}' field to hook {i+1}",
                        auto_fixable=True
                    ))
            
            # Validate event type
            if 'event' in hook:
                if hook['event'] not in self.valid_hook_events:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="hooks",
                        message=f"Invalid hook event: '{hook['event']}'",
                        details=f"Valid events: {', '.join(self.valid_hook_events)}",
                        suggestion="Use a valid hook event type"
                    ))
            
            # Validate matcher patterns
            if 'matcher' in hook:
                try:
                    re.compile(hook['matcher'])
                except re.error as e:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="hooks",
                        message=f"Invalid regex in hook {i+1} matcher",
                        details=f"Regex error: {str(e)}",
                        suggestion="Fix the regular expression pattern in the matcher",
                        auto_fixable=False
                    ))
            
            # Validate actions
            if 'actions' in hook:
                if not isinstance(hook['actions'], list):
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="hooks",
                        message=f"Hook {i+1} actions must be an array",
                        details="Actions should be a list of action objects",
                        suggestion="Change actions to an array format",
                        auto_fixable=True
                    ))
                else:
                    for j, action in enumerate(hook['actions']):
                        if not isinstance(action, dict) or 'type' not in action:
                            results.append(ValidationResult(
                                level=ValidationLevel.ERROR,
                                category="hooks",
                                message=f"Hook {i+1} action {j+1} missing type",
                                details="Each action must have a 'type' field",
                                suggestion="Add 'type' field to the action"
                            ))
                        
                        if action.get('type') == 'command' and 'command' not in action:
                            results.append(ValidationResult(
                                level=ValidationLevel.ERROR,
                                category="hooks",
                                message=f"Hook {i+1} command action missing command",
                                details="Command actions must specify the command to run",
                                suggestion="Add 'command' field with the command to execute"
                            ))
        
        return results
    
    def _validate_commands(self, commands: List[Dict]) -> List[ValidationResult]:
        """Validate slash command configurations"""
        results = []
        
        command_names = set()
        
        for i, command in enumerate(commands):
            # Check required fields
            for field in self.command_required_fields:
                if field not in command:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="commands",
                        message=f"Command {i+1} missing required field: {field}",
                        details=f"All commands must have: {', '.join(self.command_required_fields)}",
                        suggestion=f"Add the missing '{field}' field to command {i+1}",
                        auto_fixable=True
                    ))
            
            # Check for duplicate names
            if 'name' in command:
                name = command['name']
                if name in command_names:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="commands",
                        message=f"Duplicate command name: '{name}'",
                        details="Each command must have a unique name",
                        suggestion=f"Rename one of the commands with name '{name}'"
                    ))
                else:
                    command_names.add(name)
                
                # Validate command name format
                if not re.match(r'^[a-z][a-z0-9-]*$', name):
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        category="commands",
                        message=f"Command name '{name}' should follow naming conventions",
                        details="Command names should be lowercase with hyphens",
                        suggestion="Use lowercase letters, numbers, and hyphens only"
                    ))
            
            # Validate command syntax
            if 'command' in command:
                cmd = command['command']
                
                # Check for potentially dangerous commands
                for pattern in self.security_patterns['dangerous_commands']:
                    if re.search(pattern, cmd, re.IGNORECASE):
                        results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            category="security",
                            message=f"Dangerous command in '{command.get('name', i+1)}'",
                            details=f"Command contains potentially dangerous pattern: {pattern}",
                            suggestion="Review and remove dangerous command patterns"
                        ))
        
        return results
    
    def _validate_settings(self, settings: Dict) -> List[ValidationResult]:
        """Validate settings configuration"""
        results = []
        
        # Validate tools permissions
        if 'tools' in settings and 'permissions' in settings['tools']:
            permissions = settings['tools']['permissions']
            
            for tool, perms in permissions.items():
                if tool not in self.valid_tools:
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        category="settings",
                        message=f"Unknown tool in permissions: '{tool}'",
                        details=f"Valid tools: {', '.join(self.valid_tools)}",
                        suggestion="Check tool name spelling or remove if not needed"
                    ))
                
                if isinstance(perms, list):
                    for perm in perms:
                        if perm not in ['allow', 'deny'] and not isinstance(perm, str):
                            results.append(ValidationResult(
                                level=ValidationLevel.WARNING,
                                category="settings",
                                message=f"Unusual permission format for {tool}",
                                details="Permissions are usually 'allow', 'deny', or command patterns",
                                suggestion="Review permission format"
                            ))
        
        return results
    
    def _validate_security(self, config: Dict) -> List[ValidationResult]:
        """Validate security aspects of configuration"""
        results = []
        
        config_str = json.dumps(config).lower()
        
        # Check for API keys or secrets
        for pattern in self.security_patterns['api_keys']:
            if re.search(pattern, config_str):
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="security",
                    message="Potential API key or secret found in configuration",
                    details="Secrets should not be stored in configuration files",
                    suggestion="Use environment variables or secure secret management"
                ))
        
        # Check for sensitive paths
        for pattern in self.security_patterns['sensitive_paths']:
            if re.search(pattern, config_str):
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="security",
                    message="Reference to sensitive path found",
                    details=f"Configuration references sensitive path pattern: {pattern}",
                    suggestion="Ensure access to sensitive paths is intentional and secure"
                ))
        
        # Check tool permissions for security
        if 'settings' in config and 'tools' in config['settings']:
            permissions = config['settings'].get('tools', {}).get('permissions', {})
            
            if 'Bash' in permissions:
                bash_perms = permissions['Bash']
                if bash_perms == ['allow'] or bash_perms == 'allow':
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        category="security",
                        message="Bash tool has unrestricted permissions",
                        details="Allowing all Bash commands can be a security risk",
                        suggestion="Restrict Bash permissions to specific commands or patterns"
                    ))
        
        return results
    
    def _validate_performance(self, config: Dict) -> List[ValidationResult]:
        """Validate performance aspects of configuration"""
        results = []
        
        # Check counts against thresholds
        for section, threshold in self.performance_thresholds.items():
            if section.endswith('_count'):
                section_name = section.replace('_count', 's')
                if section_name in config:
                    count = len(config[section_name])
                    
                    if count >= threshold['error']:
                        results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            category="performance",
                            message=f"Too many {section_name}: {count}",
                            details=f"Large numbers of {section_name} can impact performance",
                            suggestion=f"Consider reducing to fewer than {threshold['warning']} {section_name}"
                        ))
                    elif count >= threshold['warning']:
                        results.append(ValidationResult(
                            level=ValidationLevel.WARNING,
                            category="performance",
                            message=f"Many {section_name}: {count}",
                            details=f"Consider if all {count} {section_name} are necessary",
                            suggestion="Review and consolidate if possible"
                        ))
        
        return results
    
    def _validate_tool_availability(self, config: Dict) -> List[ValidationResult]:
        """Validate that required tools are available"""
        results = []
        
        # Extract tools from hooks and commands
        required_tools = set()
        
        # From hooks
        for hook in config.get('hooks', []):
            for action in hook.get('actions', []):
                if action.get('type') == 'command':
                    cmd = action.get('command', '')
                    # Extract first word as potential tool name
                    tool = cmd.split()[0] if cmd.split() else ''
                    if tool and not tool.startswith('$'):
                        required_tools.add(tool)
        
        # From commands
        for command in config.get('commands', []):
            cmd = command.get('command', '')
            tool = cmd.split()[0] if cmd.split() else ''
            if tool and not tool.startswith('$'):
                required_tools.add(tool)
        
        # Check availability of common tools
        common_tools = ['npm', 'npx', 'python', 'pip', 'node', 'git']
        for tool in required_tools:
            if tool in common_tools:
                try:
                    result = subprocess.run(['which', tool], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode != 0:
                        results.append(ValidationResult(
                            level=ValidationLevel.WARNING,
                            category="tools",
                            message=f"Tool '{tool}' not found in PATH",
                            details="This tool is required by your configuration but may not be installed",
                            suggestion=f"Install {tool} or update configuration to use available tools"
                        ))
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    # Can't check availability, skip
                    pass
        
        return results
    
    def _generate_validation_report(self, results: List[ValidationResult], 
                                  config: Dict) -> ValidationReport:
        """Generate comprehensive validation report"""
        
        # Count results by level
        summary = {
            'errors': len([r for r in results if r.level == ValidationLevel.ERROR]),
            'warnings': len([r for r in results if r.level == ValidationLevel.WARNING]),
            'info': len([r for r in results if r.level == ValidationLevel.INFO]),
            'success': len([r for r in results if r.level == ValidationLevel.SUCCESS])
        }
        
        # Determine overall status
        if summary['errors'] > 0:
            overall_status = ValidationLevel.ERROR
        elif summary['warnings'] > 0:
            overall_status = ValidationLevel.WARNING
        elif summary['info'] > 0:
            overall_status = ValidationLevel.INFO
        else:
            overall_status = ValidationLevel.SUCCESS
        
        # Calculate scores
        performance_score = self._calculate_performance_score(config, results)
        compatibility_score = self._calculate_compatibility_score(results)
        security_score = self._calculate_security_score(results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(results, config)
        
        return ValidationReport(
            overall_status=overall_status,
            results=results,
            summary=summary,
            performance_score=performance_score,
            compatibility_score=compatibility_score,
            security_score=security_score,
            recommendations=recommendations
        )
    
    def _calculate_performance_score(self, config: Dict, results: List[ValidationResult]) -> float:
        """Calculate performance score (0-1)"""
        score = 1.0
        
        # Deduct for performance issues
        perf_errors = [r for r in results if r.category == 'performance' and r.level == ValidationLevel.ERROR]
        perf_warnings = [r for r in results if r.category == 'performance' and r.level == ValidationLevel.WARNING]
        
        score -= len(perf_errors) * 0.2
        score -= len(perf_warnings) * 0.1
        
        return max(0.0, score)
    
    def _calculate_compatibility_score(self, results: List[ValidationResult]) -> float:
        """Calculate compatibility score (0-1)"""
        score = 1.0
        
        # Deduct for schema and tool issues
        schema_errors = [r for r in results if r.category in ['schema', 'tools'] and r.level == ValidationLevel.ERROR]
        schema_warnings = [r for r in results if r.category in ['schema', 'tools'] and r.level == ValidationLevel.WARNING]
        
        score -= len(schema_errors) * 0.3
        score -= len(schema_warnings) * 0.1
        
        return max(0.0, score)
    
    def _calculate_security_score(self, results: List[ValidationResult]) -> float:
        """Calculate security score (0-1)"""
        score = 1.0
        
        # Deduct for security issues
        security_errors = [r for r in results if r.category == 'security' and r.level == ValidationLevel.ERROR]
        security_warnings = [r for r in results if r.category == 'security' and r.level == ValidationLevel.WARNING]
        
        score -= len(security_errors) * 0.4
        score -= len(security_warnings) * 0.2
        
        return max(0.0, score)
    
    def _generate_recommendations(self, results: List[ValidationResult], 
                                config: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Error-based recommendations
        errors = [r for r in results if r.level == ValidationLevel.ERROR]
        if errors:
            recommendations.append(f"Fix {len(errors)} critical errors before deployment")
        
        # Security recommendations
        security_issues = [r for r in results if r.category == 'security']
        if security_issues:
            recommendations.append("Review security findings and implement suggested fixes")
        
        # Performance recommendations
        perf_issues = [r for r in results if r.category == 'performance']
        if perf_issues:
            recommendations.append("Optimize configuration for better performance")
        
        # Auto-fixable recommendations
        auto_fixable = [r for r in results if r.auto_fixable]
        if auto_fixable:
            recommendations.append(f"{len(auto_fixable)} issues can be automatically fixed")
        
        # General recommendations based on config structure
        if not config.get('agents'):
            recommendations.append("Consider adding agents to enhance development workflow")
        
        if not config.get('hooks'):
            recommendations.append("Add hooks to automate common development tasks")
        
        return recommendations