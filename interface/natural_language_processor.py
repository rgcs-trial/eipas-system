"""
Natural Language Processor

Parse setup requests in plain English and convert them to configuration specifications.
Enables conversational configuration setup with intelligent intent understanding.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

class IntentType(Enum):
    """Types of configuration intents"""
    SETUP_PROJECT = "setup_project"
    ADD_AGENT = "add_agent" 
    CREATE_HOOK = "create_hook"
    CONFIGURE_COMMAND = "configure_command"
    SET_PERMISSIONS = "set_permissions"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    ENHANCE_SECURITY = "enhance_security"
    IMPROVE_WORKFLOW = "improve_workflow"
    TROUBLESHOOT = "troubleshoot"
    GET_RECOMMENDATIONS = "get_recommendations"

@dataclass
class NLPIntent:
    """Parsed natural language intent"""
    intent_type: IntentType
    confidence: float
    entities: Dict[str, Any]
    context: Dict[str, Any]
    suggested_actions: List[Dict]
    clarifications_needed: List[str]

@dataclass
class ConfigurationSpec:
    """Generated configuration specification from NLP"""
    agents: List[Dict]
    hooks: List[Dict]
    commands: List[Dict]
    settings: Dict
    installation_options: Dict
    explanation: str

class NaturalLanguageProcessor:
    """Advanced NLP for conversational configuration setup"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Intent recognition patterns
        self.intent_patterns = {
            IntentType.SETUP_PROJECT: [
                r"set up.*(?:claude|configuration|config).*for.*(?:project|app|application)",
                r"configure.*claude.*for.*(?:react|python|node|django|fastapi)",
                r"install.*claude.*(?:configuration|config|setup)",
                r"i want to.*(?:setup|configure|install).*claude",
                r"help me.*(?:configure|setup).*claude.*(?:project|team)"
            ],
            IntentType.ADD_AGENT: [
                r"add.*(?:agent|assistant|helper).*(?:for|to help with).*(?:review|test|format)",
                r"create.*(?:agent|bot).*(?:that can|to).*(?:review|check|validate)",
                r"i need.*(?:agent|assistant).*(?:for|to help with).*(?:code|testing|security)",
                r"set up.*(?:reviewer|tester|formatter).*agent"
            ],
            IntentType.CREATE_HOOK: [
                r"(?:add|create|set up).*hook.*(?:that|to).*(?:runs|executes).*(?:after|before|when)",
                r"automatically.*(?:run|execute).*(?:format|test|lint|build).*(?:after|when)",
                r"i want.*(?:automatic|auto).*(?:formatting|testing|linting)",
                r"hook.*(?:for|to).*(?:prettier|eslint|black|pytest)"
            ],
            IntentType.CONFIGURE_COMMAND: [
                r"(?:add|create).*(?:command|slash command).*(?:for|to).*(?:test|build|deploy|run)",
                r"set up.*(?:/test|/build|/deploy|/run).*command",
                r"i want.*(?:command|shortcut).*(?:to|for).*(?:testing|building|deployment)",
                r"create.*slash command.*(?:that|to).*(?:runs|executes)"
            ],
            IntentType.OPTIMIZE_PERFORMANCE: [
                r"(?:optimize|improve|speed up|make.*faster).*(?:performance|speed|efficiency)",
                r"claude.*(?:is|runs).*(?:slow|slowly|sluggish)",
                r"how.*(?:can i|to).*(?:improve|optimize|speed up).*(?:claude|performance)",
                r"make.*claude.*(?:faster|more efficient|perform better)"
            ],
            IntentType.ENHANCE_SECURITY: [
                r"(?:improve|enhance|increase|add).*security.*(?:to|for).*(?:claude|configuration)",
                r"make.*claude.*(?:more secure|safer)",
                r"(?:add|implement|set up).*security.*(?:features|measures|controls)",
                r"secure.*claude.*(?:configuration|setup|installation)"
            ],
            IntentType.GET_RECOMMENDATIONS: [
                r"(?:what|which).*(?:configuration|setup|agents|hooks).*(?:should i|do you recommend)",
                r"recommend.*(?:configuration|setup|agents).*(?:for|to)",
                r"suggest.*(?:best|optimal).*(?:configuration|setup)",
                r"what.*(?:is the best|are good).*(?:configurations|setups|patterns)"
            ]
        }
        
        # Entity extraction patterns
        self.entity_patterns = {
            'framework': [
                (r'\b(react|vue|angular|next\.?js|nuxt\.?js)\b', 'frontend_framework'),
                (r'\b(django|flask|fastapi|express|koa|nest\.?js)\b', 'backend_framework'),
                (r'\b(pandas|numpy|scikit-learn|tensorflow|pytorch)\b', 'ml_framework')
            ],
            'language': [
                (r'\b(python|javascript|typescript|java|go|rust|c\+\+|c#)\b', 'programming_language')
            ],
            'tool': [
                (r'\b(prettier|eslint|black|ruff|mypy|pytest|jest|vitest)\b', 'development_tool'),
                (r'\b(docker|kubernetes|terraform|ansible)\b', 'infrastructure_tool')
            ],
            'action': [
                (r'\b(format|lint|test|build|deploy|security scan|type check)\b', 'automation_action')
            ],
            'team_size': [
                (r'\b(\d+)\s*(?:person|people|developer|dev|member)s?\b', 'team_size'),
                (r'\b(small|medium|large)\s*team\b', 'team_scale')
            ],
            'urgency': [
                (r'\b(urgent|asap|quickly|fast|immediately)\b', 'high_urgency'),
                (r'\b(when.*time|no rush|eventually)\b', 'low_urgency')
            ]
        }
        
        # Context keywords
        self.context_keywords = {
            'project_type': [
                'startup', 'enterprise', 'open source', 'personal', 'prototype', 'production'
            ],
            'experience_level': [
                'beginner', 'intermediate', 'advanced', 'expert', 'new to', 'familiar with'
            ],
            'constraints': [
                'budget', 'time', 'security', 'compliance', 'performance', 'team size'
            ]
        }
    
    def process_natural_language(self, text: str, context: Dict = None) -> NLPIntent:
        """Process natural language input and extract configuration intent"""
        self.logger.info("Processing natural language configuration request")
        
        text_lower = text.lower()
        
        # Detect intent
        intent_type, confidence = self._detect_intent(text_lower)
        
        # Extract entities
        entities = self._extract_entities(text_lower)
        
        # Extract context
        extracted_context = self._extract_context(text_lower)
        if context:
            extracted_context.update(context)
        
        # Generate suggested actions
        suggested_actions = self._generate_suggested_actions(intent_type, entities, extracted_context)
        
        # Identify clarifications needed
        clarifications = self._identify_clarifications(intent_type, entities, extracted_context)
        
        nlp_intent = NLPIntent(
            intent_type=intent_type,
            confidence=confidence,
            entities=entities,
            context=extracted_context,
            suggested_actions=suggested_actions,
            clarifications_needed=clarifications
        )
        
        self.logger.info(f"Detected intent: {intent_type.value} (confidence: {confidence:.2f})")
        return nlp_intent
    
    def _detect_intent(self, text: str) -> Tuple[IntentType, float]:
        """Detect the primary intent from text"""
        best_intent = IntentType.SETUP_PROJECT
        best_confidence = 0.0
        
        for intent_type, patterns in self.intent_patterns.items():
            confidence = 0.0
            
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    confidence = max(confidence, 0.8)
            
            # Boost confidence for exact matches
            if intent_type.value.replace('_', ' ') in text:
                confidence += 0.1
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_intent = intent_type
        
        return best_intent, min(1.0, best_confidence)
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract relevant entities from text"""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            extracted = []
            
            for pattern, label in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]  # Take first group if tuple
                    extracted.append({
                        'value': match.lower(),
                        'label': label,
                        'confidence': 0.9
                    })
            
            if extracted:
                entities[entity_type] = extracted
        
        return entities
    
    def _extract_context(self, text: str) -> Dict[str, Any]:
        """Extract contextual information from text"""
        context = {}
        
        # Extract project type
        for project_type in self.context_keywords['project_type']:
            if project_type in text:
                context['project_type'] = project_type
                break
        
        # Extract experience level
        for level in self.context_keywords['experience_level']:
            if level in text:
                context['experience_level'] = level
                break
        
        # Extract constraints
        constraints = []
        for constraint in self.context_keywords['constraints']:
            if constraint in text:
                constraints.append(constraint)
        if constraints:
            context['constraints'] = constraints
        
        # Extract urgency
        if any(word in text for word in ['urgent', 'asap', 'quickly', 'fast', 'immediately']):
            context['urgency'] = 'high'
        elif any(phrase in text for phrase in ['when time', 'no rush', 'eventually']):
            context['urgency'] = 'low'
        else:
            context['urgency'] = 'medium'
        
        return context
    
    def _generate_suggested_actions(self, intent_type: IntentType, entities: Dict, 
                                  context: Dict) -> List[Dict]:
        """Generate suggested actions based on intent and entities"""
        actions = []
        
        if intent_type == IntentType.SETUP_PROJECT:
            # Suggest complete project setup
            frameworks = entities.get('framework', [])
            if frameworks:
                for fw in frameworks:
                    actions.append({
                        'type': 'install_profile',
                        'profile': self._map_framework_to_profile(fw['value']),
                        'description': f"Install {fw['value']} optimized configuration",
                        'priority': 'high'
                    })
            else:
                actions.append({
                    'type': 'analyze_project',
                    'description': "Analyze project structure to recommend configuration",
                    'priority': 'high'
                })
        
        elif intent_type == IntentType.ADD_AGENT:
            tools = entities.get('tool', [])
            actions_entities = entities.get('action', [])
            
            if tools or actions_entities:
                for tool in tools:
                    actions.append({
                        'type': 'create_agent',
                        'agent_type': 'code_reviewer',
                        'specializations': [tool['value']],
                        'description': f"Create agent specialized in {tool['value']}",
                        'priority': 'medium'
                    })
                
                for action in actions_entities:
                    actions.append({
                        'type': 'create_agent',
                        'agent_type': self._map_action_to_agent_type(action['value']),
                        'description': f"Create agent for {action['value']} tasks",
                        'priority': 'medium'
                    })
        
        elif intent_type == IntentType.CREATE_HOOK:
            tools = entities.get('tool', [])
            actions_entities = entities.get('action', [])
            
            for tool in tools:
                actions.append({
                    'type': 'create_hook',
                    'hook_type': 'PostToolUse',
                    'command': self._get_tool_command(tool['value']),
                    'description': f"Auto-run {tool['value']} after code changes",
                    'priority': 'high'
                })
            
            for action in actions_entities:
                actions.append({
                    'type': 'create_hook',
                    'hook_type': 'PostToolUse',
                    'command': self._get_action_command(action['value']),
                    'description': f"Auto-{action['value']} after code changes",
                    'priority': 'high'
                })
        
        elif intent_type == IntentType.CONFIGURE_COMMAND:
            actions_entities = entities.get('action', [])
            
            for action in actions_entities:
                actions.append({
                    'type': 'create_command',
                    'command_name': action['value'],
                    'command': self._get_action_command(action['value']),
                    'description': f"Create /{action['value']} slash command",
                    'priority': 'medium'
                })
        
        elif intent_type == IntentType.GET_RECOMMENDATIONS:
            actions.append({
                'type': 'get_recommendations',
                'description': "Analyze project and provide configuration recommendations",
                'priority': 'high'
            })
        
        return actions
    
    def _identify_clarifications(self, intent_type: IntentType, entities: Dict, 
                               context: Dict) -> List[str]:
        """Identify what clarifications are needed"""
        clarifications = []
        
        if intent_type == IntentType.SETUP_PROJECT:
            if not entities.get('framework') and not entities.get('language'):
                clarifications.append("What programming language or framework are you using?")
            
            if not context.get('project_type'):
                clarifications.append("Is this for a personal project, startup, or enterprise?")
            
            team_size = entities.get('team_size')
            if not team_size:
                clarifications.append("How many developers will be using this configuration?")
        
        elif intent_type == IntentType.ADD_AGENT:
            if not entities.get('action') and not entities.get('tool'):
                clarifications.append("What specific task should the agent help with? (e.g., code review, testing, formatting)")
        
        elif intent_type == IntentType.CREATE_HOOK:
            if not entities.get('action') and not entities.get('tool'):
                clarifications.append("What action should the hook perform? (e.g., format code, run tests)")
        
        elif intent_type == IntentType.OPTIMIZE_PERFORMANCE:
            clarifications.append("What specific performance issue are you experiencing?")
            clarifications.append("Are you looking to optimize setup time, runtime performance, or both?")
        
        return clarifications
    
    def _map_framework_to_profile(self, framework: str) -> str:
        """Map framework name to configuration profile"""
        mapping = {
            'react': 'web-frontend',
            'vue': 'web-frontend', 
            'angular': 'web-frontend',
            'next.js': 'web-frontend',
            'nuxt.js': 'web-frontend',
            'django': 'backend-api',
            'flask': 'backend-api',
            'fastapi': 'backend-api',
            'express': 'backend-api',
            'pandas': 'data-science',
            'numpy': 'data-science',
            'tensorflow': 'data-science',
            'pytorch': 'data-science'
        }
        
        return mapping.get(framework, 'general')
    
    def _map_action_to_agent_type(self, action: str) -> str:
        """Map action to appropriate agent type"""
        mapping = {
            'format': 'formatter',
            'lint': 'linter',
            'test': 'tester',
            'build': 'builder',
            'security scan': 'security_auditor',
            'type check': 'type_checker'
        }
        
        return mapping.get(action, 'code_reviewer')
    
    def _get_tool_command(self, tool: str) -> str:
        """Get command for a development tool"""
        commands = {
            'prettier': 'npx prettier --write $CLAUDE_MODIFIED_FILES',
            'eslint': 'npx eslint $CLAUDE_MODIFIED_FILES --fix',
            'black': 'black $CLAUDE_MODIFIED_FILES',
            'ruff': 'ruff check $CLAUDE_MODIFIED_FILES --fix',
            'mypy': 'mypy $CLAUDE_MODIFIED_FILES',
            'pytest': 'pytest',
            'jest': 'npm test'
        }
        
        return commands.get(tool, f'{tool} $CLAUDE_MODIFIED_FILES')
    
    def _get_action_command(self, action: str) -> str:
        """Get command for an action"""
        commands = {
            'format': 'npx prettier --write .',
            'lint': 'npx eslint . --fix',
            'test': 'npm test',
            'build': 'npm run build',
            'deploy': 'npm run deploy',
            'type check': 'npx tsc --noEmit'
        }
        
        return commands.get(action, action)
    
    def generate_configuration_spec(self, nlp_intent: NLPIntent, 
                                  project_context: Dict = None) -> ConfigurationSpec:
        """Generate complete configuration specification from NLP intent"""
        self.logger.info("Generating configuration specification from NLP intent")
        
        agents = []
        hooks = []
        commands = []
        settings = {}
        installation_options = {}
        
        # Process suggested actions
        for action in nlp_intent.suggested_actions:
            if action['type'] == 'create_agent':
                agents.append({
                    'name': f"{action['agent_type'].replace('_', ' ').title()}",
                    'type': action['agent_type'],
                    'description': action['description'],
                    'specializations': action.get('specializations', [])
                })
            
            elif action['type'] == 'create_hook':
                hooks.append({
                    'event': action['hook_type'],
                    'matcher': 'Write|Edit',
                    'actions': [{'type': 'command', 'command': action['command']}],
                    'description': action['description']
                })
            
            elif action['type'] == 'create_command':
                commands.append({
                    'name': action['command_name'],
                    'description': action['description'],
                    'command': action['command']
                })
            
            elif action['type'] == 'install_profile':
                installation_options['profile'] = action['profile']
        
        # Generate settings based on context
        settings = self._generate_settings(nlp_intent, project_context)
        
        # Generate explanation
        explanation = self._generate_explanation(nlp_intent, agents, hooks, commands)
        
        return ConfigurationSpec(
            agents=agents,
            hooks=hooks,
            commands=commands,
            settings=settings,
            installation_options=installation_options,
            explanation=explanation
        )
    
    def _generate_settings(self, nlp_intent: NLPIntent, project_context: Dict = None) -> Dict:
        """Generate appropriate settings based on intent and context"""
        settings = {
            'tools': {
                'permissions': {
                    'Bash': ['allow'],
                    'Edit': ['allow'],
                    'Read': ['allow'],
                    'Write': ['allow']
                }
            }
        }
        
        # Adjust permissions based on security context
        if nlp_intent.context.get('project_type') == 'enterprise':
            settings['tools']['permissions']['Bash'] = ['npm*', 'npx*', 'python*', 'pip*']
        
        # Add team-specific settings
        team_size = nlp_intent.entities.get('team_size')
        if team_size:
            settings['collaboration'] = {
                'team_size': team_size[0]['value'] if team_size else 'unknown',
                'shared_configs': True
            }
        
        return settings
    
    def _generate_explanation(self, nlp_intent: NLPIntent, agents: List[Dict], 
                            hooks: List[Dict], commands: List[Dict]) -> str:
        """Generate human-readable explanation of the configuration"""
        explanation_parts = []
        
        explanation_parts.append(f"Based on your request to {nlp_intent.intent_type.value.replace('_', ' ')}, I've prepared the following configuration:")
        
        if agents:
            agent_names = [agent['name'] for agent in agents]
            explanation_parts.append(f"• **Agents**: {', '.join(agent_names)} - These will help with code review, validation, and assistance.")
        
        if hooks:
            hook_descriptions = [hook['description'] for hook in hooks]
            explanation_parts.append(f"• **Automation Hooks**: {len(hooks)} hooks configured to automatically {', '.join(hook_descriptions).lower()}.")
        
        if commands:
            command_names = [f"/{cmd['name']}" for cmd in commands]
            explanation_parts.append(f"• **Slash Commands**: {', '.join(command_names)} - Quick commands for common tasks.")
        
        # Add context-specific notes
        if nlp_intent.context.get('urgency') == 'high':
            explanation_parts.append("⚡ **Fast Setup**: Configuration optimized for quick installation to meet your urgent timeline.")
        
        if nlp_intent.context.get('experience_level') == 'beginner':
            explanation_parts.append("📚 **Beginner-Friendly**: Includes helpful documentation and gentle defaults.")
        
        return '\n'.join(explanation_parts)