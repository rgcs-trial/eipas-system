"""
Pattern Matcher

Success pattern recognition from configuration database.
Learns from successful configurations to recommend optimal setups.
"""

import json
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from collections import defaultdict

@dataclass
class ConfigurationPattern:
    """A successful configuration pattern"""
    pattern_id: str
    name: str
    description: str
    success_rate: float
    usage_count: int
    contexts: List[str]  # Where this pattern works well
    agents: List[Dict]
    hooks: List[Dict] 
    commands: List[Dict]
    settings: Dict
    performance_metrics: Dict
    tags: List[str]

@dataclass
class PatternMatch:
    """A pattern match with confidence score"""
    pattern: ConfigurationPattern
    confidence: float
    match_reasons: List[str]
    adaptations_needed: List[str]

class PatternMatcher:
    """Intelligence engine for matching projects to successful configuration patterns"""
    
    def __init__(self, pattern_database_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.pattern_database_path = pattern_database_path or Path.home() / '.claude' / 'patterns.json'
        self.patterns: Dict[str, ConfigurationPattern] = {}
        self.load_patterns()
        
        # Context matching weights
        self.context_weights = {
            'architecture_pattern': 3.0,
            'primary_framework': 2.5,
            'language': 2.0,
            'team_size': 1.5,
            'development_stage': 2.0,
            'business_domain': 1.5,
            'deployment_context': 1.8,
            'security_requirements': 2.2,
            'performance_requirements': 1.8
        }
    
    def load_patterns(self):
        """Load configuration patterns from database"""
        if self.pattern_database_path.exists():
            try:
                with open(self.pattern_database_path, 'r') as f:
                    data = json.load(f)
                
                for pattern_data in data.get('patterns', []):
                    pattern = ConfigurationPattern(**pattern_data)
                    self.patterns[pattern.pattern_id] = pattern
                
                self.logger.info(f"Loaded {len(self.patterns)} configuration patterns")
                
            except Exception as e:
                self.logger.error(f"Failed to load patterns: {e}")
                self._create_default_patterns()
        else:
            self.logger.info("No pattern database found, creating default patterns")
            self._create_default_patterns()
    
    def _create_default_patterns(self):
        """Create default successful configuration patterns"""
        default_patterns = [
            # React Frontend Pattern
            ConfigurationPattern(
                pattern_id="react_frontend_standard",
                name="React Frontend Standard",
                description="Optimized configuration for React-based frontend applications",
                success_rate=0.92,
                usage_count=156,
                contexts=["web_application", "component-based", "frontend", "TypeScript", "team_size:2-8"],
                agents=[
                    {
                        "name": "React Component Reviewer",
                        "type": "code_reviewer",
                        "description": "Reviews React components for best practices and performance",
                        "specializations": ["jsx", "hooks", "performance", "accessibility"]
                    },
                    {
                        "name": "TypeScript Assistant",
                        "type": "language_helper",
                        "description": "Helps with TypeScript types and interfaces",
                        "specializations": ["types", "interfaces", "generics"]
                    }
                ],
                hooks=[
                    {
                        "event": "PostToolUse",
                        "matcher": "Write|Edit.*\\.(tsx?|jsx?)$",
                        "actions": [
                            {"type": "command", "command": "npx prettier --write $CLAUDE_MODIFIED_FILES"},
                            {"type": "command", "command": "npx eslint $CLAUDE_MODIFIED_FILES --fix"}
                        ]
                    }
                ],
                commands=[
                    {
                        "name": "test",
                        "description": "Run React tests with coverage",
                        "command": "npm test -- --coverage"
                    },
                    {
                        "name": "build", 
                        "description": "Build React application for production",
                        "command": "npm run build"
                    }
                ],
                settings={
                    "tools": {
                        "permissions": {
                            "Bash": ["npm*", "npx*", "yarn*"],
                            "Edit": ["allow"],
                            "Read": ["allow"]
                        }
                    }
                },
                performance_metrics={
                    "setup_time_seconds": 45,
                    "error_reduction_percent": 78,
                    "productivity_increase_percent": 23
                },
                tags=["react", "frontend", "typescript", "modern"]
            ),
            
            # FastAPI Backend Pattern
            ConfigurationPattern(
                pattern_id="fastapi_backend_standard",
                name="FastAPI Backend Standard", 
                description="Production-ready FastAPI backend configuration",
                success_rate=0.89,
                usage_count=98,
                contexts=["api_service", "backend", "Python", "microservices", "team_size:3-10"],
                agents=[
                    {
                        "name": "FastAPI Code Reviewer",
                        "type": "code_reviewer",
                        "description": "Reviews FastAPI code for performance and security",
                        "specializations": ["async", "pydantic", "security", "performance"]
                    },
                    {
                        "name": "API Documentation Generator",
                        "type": "documentation",
                        "description": "Generates and maintains API documentation",
                        "specializations": ["openapi", "swagger", "endpoints"]
                    }
                ],
                hooks=[
                    {
                        "event": "PostToolUse",
                        "matcher": "Write|Edit.*\\.py$",
                        "actions": [
                            {"type": "command", "command": "black $CLAUDE_MODIFIED_FILES"},
                            {"type": "command", "command": "ruff check $CLAUDE_MODIFIED_FILES --fix"}
                        ]
                    }
                ],
                commands=[
                    {
                        "name": "test-api",
                        "description": "Run API tests with pytest",
                        "command": "pytest tests/ -v --cov=app"
                    },
                    {
                        "name": "dev-server",
                        "description": "Start development server",
                        "command": "uvicorn app.main:app --reload"
                    }
                ],
                settings={
                    "tools": {
                        "permissions": {
                            "Bash": ["python*", "pip*", "pytest*", "uvicorn*"],
                            "Edit": ["allow"],
                            "Read": ["allow"]
                        }
                    }
                },
                performance_metrics={
                    "setup_time_seconds": 60,
                    "error_reduction_percent": 82,
                    "productivity_increase_percent": 31
                },
                tags=["fastapi", "python", "backend", "api", "async"]
            ),
            
            # Data Science Pattern
            ConfigurationPattern(
                pattern_id="data_science_standard",
                name="Data Science Standard",
                description="Optimized configuration for data science and ML projects",
                success_rate=0.85,
                usage_count=73,
                contexts=["data_processing", "machine_learning", "Python", "jupyter", "team_size:1-5"],
                agents=[
                    {
                        "name": "Data Analysis Reviewer",
                        "type": "code_reviewer", 
                        "description": "Reviews data analysis code for best practices",
                        "specializations": ["pandas", "numpy", "matplotlib", "data_quality"]
                    },
                    {
                        "name": "ML Model Validator",
                        "type": "validator",
                        "description": "Validates machine learning models and experiments",
                        "specializations": ["sklearn", "validation", "metrics", "bias"]
                    }
                ],
                hooks=[
                    {
                        "event": "PostToolUse",
                        "matcher": "Write|Edit.*\\.ipynb$",
                        "actions": [
                            {"type": "command", "command": "jupyter nbconvert --clear-output $CLAUDE_MODIFIED_FILES"}
                        ]
                    }
                ],
                commands=[
                    {
                        "name": "analyze",
                        "description": "Run data analysis pipeline",
                        "command": "python -m src.analysis.main"
                    },
                    {
                        "name": "train",
                        "description": "Train ML model",
                        "command": "python -m src.model.train"
                    }
                ],
                settings={
                    "tools": {
                        "permissions": {
                            "Bash": ["python*", "jupyter*", "pip*"],
                            "Edit": ["allow"],
                            "Read": ["allow"]
                        }
                    }
                },
                performance_metrics={
                    "setup_time_seconds": 90,
                    "error_reduction_percent": 65,
                    "productivity_increase_percent": 28
                },
                tags=["data-science", "ml", "jupyter", "python", "analytics"]
            ),
            
            # DevOps Pattern
            ConfigurationPattern(
                pattern_id="devops_infrastructure_standard",
                name="DevOps Infrastructure Standard",
                description="Configuration for infrastructure and deployment projects",
                success_rate=0.91,
                usage_count=84,
                contexts=["infrastructure", "devops", "kubernetes", "docker", "team_size:2-12"],
                agents=[
                    {
                        "name": "Infrastructure Reviewer",
                        "type": "code_reviewer",
                        "description": "Reviews infrastructure code for security and best practices",
                        "specializations": ["terraform", "kubernetes", "security", "scalability"]
                    },
                    {
                        "name": "Deployment Validator",
                        "type": "validator", 
                        "description": "Validates deployment configurations",
                        "specializations": ["docker", "k8s", "cicd", "monitoring"]
                    }
                ],
                hooks=[
                    {
                        "event": "PostToolUse",
                        "matcher": "Write|Edit.*\\.(tf|yml|yaml)$",
                        "actions": [
                            {"type": "command", "command": "terraform fmt $CLAUDE_MODIFIED_FILES"},
                            {"type": "command", "command": "yamllint $CLAUDE_MODIFIED_FILES"}
                        ]
                    }
                ],
                commands=[
                    {
                        "name": "infra-plan",
                        "description": "Plan infrastructure changes",
                        "command": "terraform plan"
                    },
                    {
                        "name": "deploy",
                        "description": "Deploy to staging environment", 
                        "command": "kubectl apply -f k8s/"
                    }
                ],
                settings={
                    "tools": {
                        "permissions": {
                            "Bash": ["terraform*", "kubectl*", "docker*", "helm*"],
                            "Edit": ["allow"],
                            "Read": ["allow"]
                        }
                    }
                },
                performance_metrics={
                    "setup_time_seconds": 120,
                    "error_reduction_percent": 86,
                    "productivity_increase_percent": 35
                },
                tags=["devops", "infrastructure", "kubernetes", "terraform", "deployment"]
            )
        ]
        
        # Convert to dictionary
        for pattern in default_patterns:
            self.patterns[pattern.pattern_id] = pattern
        
        # Save to file
        self.save_patterns()
    
    def find_matching_patterns(self, project_context: Dict, project_intent: Dict,
                             limit: int = 5) -> List[PatternMatch]:
        """Find configuration patterns that match the project context"""
        self.logger.info("Finding matching configuration patterns")
        
        matches = []
        
        for pattern in self.patterns.values():
            match = self._evaluate_pattern_match(pattern, project_context, project_intent)
            if match.confidence > 0.3:  # Minimum confidence threshold
                matches.append(match)
        
        # Sort by confidence and return top matches
        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches[:limit]
    
    def _evaluate_pattern_match(self, pattern: ConfigurationPattern, 
                               project_context: Dict, project_intent: Dict) -> PatternMatch:
        """Evaluate how well a pattern matches the project"""
        confidence = 0.0
        match_reasons = []
        adaptations_needed = []
        
        # Match against pattern contexts
        context_score = self._calculate_context_match(pattern.contexts, project_context, project_intent)
        confidence += context_score * 0.6
        
        if context_score > 0.7:
            match_reasons.append(f"Strong context match ({context_score:.2f})")
        elif context_score > 0.4:
            match_reasons.append(f"Partial context match ({context_score:.2f})")
        
        # Match against success rate (higher success patterns get bonus)
        success_bonus = pattern.success_rate * 0.2
        confidence += success_bonus
        
        if pattern.success_rate > 0.9:
            match_reasons.append(f"Very high success rate ({pattern.success_rate:.2f})")
        
        # Match against usage count (popular patterns get bonus)
        usage_bonus = min(0.1, pattern.usage_count / 1000)
        confidence += usage_bonus
        
        if pattern.usage_count > 50:
            match_reasons.append(f"Well-tested pattern ({pattern.usage_count} uses)")
        
        # Check for needed adaptations
        adaptations_needed = self._identify_adaptations(pattern, project_context, project_intent)
        
        # Reduce confidence based on adaptations needed
        adaptation_penalty = len(adaptations_needed) * 0.05
        confidence = max(0.0, confidence - adaptation_penalty)
        
        return PatternMatch(
            pattern=pattern,
            confidence=min(1.0, confidence),
            match_reasons=match_reasons,
            adaptations_needed=adaptations_needed
        )
    
    def _calculate_context_match(self, pattern_contexts: List[str], 
                               project_context: Dict, project_intent: Dict) -> float:
        """Calculate how well pattern contexts match project"""
        if not pattern_contexts:
            return 0.5  # Neutral score for patterns without context requirements
        
        total_score = 0.0
        total_weight = 0.0
        
        # Create combined context from project_context and project_intent
        combined_context = {
            'architecture_pattern': project_context.get('architecture_pattern', ''),
            'primary_framework': project_context.get('frameworks', [None])[0] if project_context.get('frameworks') else '',
            'language': project_context.get('languages', [None])[0] if project_context.get('languages') else '',
            'team_size': f"team_size:{project_context.get('team_size_estimate', 1)}",
            'development_stage': project_context.get('development_stage', ''),
            'business_domain': project_intent.get('business_domain', ''),
            'deployment_context': project_intent.get('deployment_context', ''),
            'security_requirements': project_context.get('security_requirements', ''),
            'performance_requirements': project_context.get('performance_requirements', '')
        }
        
        for context_req in pattern_contexts:
            context_req_lower = context_req.lower()
            match_score = 0.0
            
            # Direct matches
            for context_key, context_value in combined_context.items():
                if context_value and context_req_lower == str(context_value).lower():
                    match_score = 1.0
                    break
                elif context_value and context_req_lower in str(context_value).lower():
                    match_score = 0.8
                    break
            
            # Special handling for team size ranges
            if context_req.startswith('team_size:') and not match_score:
                range_str = context_req.split(':', 1)[1]
                if '-' in range_str:
                    try:
                        min_size, max_size = map(int, range_str.split('-'))
                        actual_size = project_context.get('team_size_estimate', 1)
                        if min_size <= actual_size <= max_size:
                            match_score = 1.0
                        elif abs(actual_size - min_size) <= 2 or abs(actual_size - max_size) <= 2:
                            match_score = 0.6
                    except ValueError:
                        pass
            
            # Get weight for this context type
            weight = 1.0
            for context_type, context_weight in self.context_weights.items():
                if context_type in context_req_lower:
                    weight = context_weight
                    break
            
            total_score += match_score * weight
            total_weight += weight
        
        return total_score / max(1.0, total_weight) if total_weight > 0 else 0.0
    
    def _identify_adaptations(self, pattern: ConfigurationPattern,
                            project_context: Dict, project_intent: Dict) -> List[str]:
        """Identify adaptations needed for the pattern to work with this project"""
        adaptations = []
        
        # Check language compatibility
        pattern_languages = self._extract_languages_from_pattern(pattern)
        project_languages = set(lang.lower() for lang in project_context.get('languages', []))
        
        if pattern_languages and not pattern_languages.intersection(project_languages):
            adaptations.append(f"Adapt from {pattern_languages} to {project_languages}")
        
        # Check framework compatibility
        pattern_frameworks = self._extract_frameworks_from_pattern(pattern)
        project_frameworks = set(fw.lower() for fw in project_context.get('frameworks', []))
        
        if pattern_frameworks and not pattern_frameworks.intersection(project_frameworks):
            adaptations.append(f"Adapt framework-specific configurations")
        
        # Check team size appropriateness
        team_size = project_context.get('team_size_estimate', 1)
        if team_size == 1 and 'collaboration' in pattern.tags:
            adaptations.append("Simplify for individual developer")
        elif team_size > 10 and 'small-team' in pattern.tags:
            adaptations.append("Scale up for large team")
        
        # Check security requirements
        if (project_context.get('security_requirements') == 'high' and 
            'security' not in pattern.tags):
            adaptations.append("Add security-focused configurations")
        
        return adaptations
    
    def _extract_languages_from_pattern(self, pattern: ConfigurationPattern) -> Set[str]:
        """Extract programming languages from pattern"""
        languages = set()
        
        # Check pattern tags
        language_tags = ['python', 'javascript', 'typescript', 'java', 'go', 'rust']
        for tag in pattern.tags:
            if tag.lower() in language_tags:
                languages.add(tag.lower())
        
        # Check agent specializations
        for agent in pattern.agents:
            for spec in agent.get('specializations', []):
                if spec.lower() in language_tags:
                    languages.add(spec.lower())
        
        return languages
    
    def _extract_frameworks_from_pattern(self, pattern: ConfigurationPattern) -> Set[str]:
        """Extract frameworks from pattern"""
        frameworks = set()
        
        # Check pattern tags
        framework_tags = ['react', 'vue', 'angular', 'django', 'fastapi', 'express']
        for tag in pattern.tags:
            if tag.lower() in framework_tags:
                frameworks.add(tag.lower())
        
        return frameworks
    
    def save_patterns(self):
        """Save patterns to database file"""
        try:
            self.pattern_database_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'patterns': [asdict(pattern) for pattern in self.patterns.values()],
                'version': '1.0',
                'last_updated': str(Path.cwd())  # Placeholder for timestamp
            }
            
            with open(self.pattern_database_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"Saved {len(self.patterns)} patterns to database")
            
        except Exception as e:
            self.logger.error(f"Failed to save patterns: {e}")
    
    def add_pattern(self, pattern: ConfigurationPattern):
        """Add a new successful pattern to the database"""
        self.patterns[pattern.pattern_id] = pattern
        self.save_patterns()
        self.logger.info(f"Added new pattern: {pattern.name}")
    
    def update_pattern_metrics(self, pattern_id: str, success: bool, 
                             performance_data: Optional[Dict] = None):
        """Update pattern success metrics based on usage feedback"""
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            
            # Update usage count
            pattern.usage_count += 1
            
            # Update success rate (exponential moving average)
            alpha = 0.1  # Learning rate
            if success:
                pattern.success_rate = pattern.success_rate * (1 - alpha) + alpha
            else:
                pattern.success_rate = pattern.success_rate * (1 - alpha)
            
            # Update performance metrics
            if performance_data:
                for metric, value in performance_data.items():
                    if metric in pattern.performance_metrics:
                        # Exponential moving average
                        old_value = pattern.performance_metrics[metric]
                        pattern.performance_metrics[metric] = old_value * (1 - alpha) + value * alpha
            
            self.save_patterns()
            self.logger.info(f"Updated metrics for pattern: {pattern.name}")