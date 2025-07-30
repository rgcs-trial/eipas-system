"""
Intent Detector

Machine learning model for project intent recognition.
Understands what developers are trying to build beyond just technology stack.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

@dataclass
class ProjectIntent:
    """Detected project intent with confidence scores"""
    primary_intent: str
    confidence: float
    secondary_intents: List[Tuple[str, float]]
    use_cases: List[str]
    target_audience: str
    deployment_context: str
    business_domain: str

class IntentDetector:
    """AI-powered intent detection for development projects"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Intent classification patterns
        self.intent_patterns = {
            'web_application': {
                'keywords': ['website', 'web', 'app', 'frontend', 'backend', 'full-stack', 'dashboard'],
                'files': ['index.html', 'app.js', 'main.py', 'server.js'],
                'frameworks': ['react', 'vue', 'angular', 'django', 'flask', 'express'],
                'weight': 1.0
            },
            'api_service': {
                'keywords': ['api', 'service', 'endpoint', 'rest', 'graphql', 'microservice'],
                'files': ['api.py', 'routes.py', 'controllers', 'handlers'],
                'frameworks': ['fastapi', 'express', 'flask', 'django-rest'],
                'weight': 1.0
            },
            'data_processing': {
                'keywords': ['data', 'analytics', 'etl', 'pipeline', 'processing', 'analysis'],
                'files': ['pipeline.py', 'transform.py', 'etl.py', 'data.py'],
                'frameworks': ['pandas', 'numpy', 'spark', 'airflow'],
                'weight': 1.0
            },
            'machine_learning': {
                'keywords': ['ml', 'ai', 'model', 'prediction', 'training', 'neural', 'deep'],
                'files': ['model.py', 'train.py', 'predict.py', 'neural.py'],
                'frameworks': ['tensorflow', 'pytorch', 'sklearn', 'keras'],
                'weight': 1.0
            },
            'mobile_application': {
                'keywords': ['mobile', 'ios', 'android', 'react-native', 'flutter'],
                'files': ['App.js', 'MainActivity.java', 'AppDelegate.swift'],
                'frameworks': ['react-native', 'flutter', 'ionic'],
                'weight': 1.0
            },
            'desktop_application': {
                'keywords': ['desktop', 'gui', 'electron', 'tkinter', 'qt'],
                'files': ['main.py', 'app.py', 'main.js'],
                'frameworks': ['electron', 'tkinter', 'pyqt', 'kivy'],
                'weight': 1.0
            },
            'automation_tool': {
                'keywords': ['automation', 'script', 'tool', 'utility', 'bot', 'scraper'],
                'files': ['script.py', 'bot.py', 'automation.py', 'scraper.py'],
                'frameworks': ['selenium', 'scrapy', 'requests'],
                'weight': 1.0
            },
            'infrastructure': {
                'keywords': ['infrastructure', 'devops', 'deployment', 'docker', 'kubernetes'],
                'files': ['Dockerfile', 'docker-compose.yml', 'terraform', 'ansible'],
                'frameworks': ['docker', 'kubernetes', 'terraform', 'ansible'],
                'weight': 1.0
            },
            'game_development': {
                'keywords': ['game', 'gaming', 'unity', 'pygame', 'graphics'],
                'files': ['game.py', 'main.unity', 'player.cs'],
                'frameworks': ['pygame', 'unity', 'godot'],
                'weight': 1.0
            },
            'iot_project': {
                'keywords': ['iot', 'sensor', 'arduino', 'raspberry', 'embedded'],
                'files': ['sensor.py', 'arduino.ino', 'device.py'],
                'frameworks': ['micropython', 'arduino', 'raspberry'],
                'weight': 1.0
            }
        }
        
        # Business domain patterns
        self.domain_patterns = {
            'ecommerce': ['shop', 'store', 'cart', 'payment', 'product', 'order'],
            'fintech': ['finance', 'bank', 'payment', 'trading', 'blockchain', 'crypto'],
            'healthcare': ['health', 'medical', 'patient', 'doctor', 'clinic', 'pharma'],
            'education': ['education', 'learning', 'student', 'course', 'school', 'university'],
            'social': ['social', 'chat', 'message', 'friend', 'network', 'community'],
            'enterprise': ['business', 'crm', 'erp', 'hr', 'management', 'corporate'],
            'media': ['media', 'content', 'video', 'audio', 'streaming', 'publishing'],
            'gaming': ['game', 'player', 'score', 'level', 'tournament', 'gaming']
        }
        
        # Target audience patterns
        self.audience_patterns = {
            'consumer': ['user', 'customer', 'public', 'consumer', 'client'],
            'enterprise': ['business', 'corporate', 'enterprise', 'organization'],
            'developer': ['developer', 'api', 'sdk', 'library', 'framework'],
            'internal': ['internal', 'team', 'company', 'organization', 'staff']
        }
    
    def detect_intent(self, project_path: Path, project_name: str = "", 
                     description: str = "") -> ProjectIntent:
        """Detect project intent using ML-powered analysis"""
        self.logger.info(f"Detecting intent for project at {project_path}")
        
        # Gather text sources for analysis
        text_sources = self._gather_text_sources(project_path, project_name, description)
        
        # Analyze file structure
        file_structure = self._analyze_file_structure(project_path)
        
        # Score each intent
        intent_scores = self._score_intents(text_sources, file_structure)
        
        # Determine primary intent
        primary_intent, confidence = self._get_primary_intent(intent_scores)
        
        # Get secondary intents
        secondary_intents = self._get_secondary_intents(intent_scores, primary_intent)
        
        # Detect use cases
        use_cases = self._detect_use_cases(text_sources, primary_intent)
        
        # Detect target audience
        target_audience = self._detect_target_audience(text_sources)
        
        # Detect deployment context
        deployment_context = self._detect_deployment_context(file_structure, text_sources)
        
        # Detect business domain
        business_domain = self._detect_business_domain(text_sources)
        
        intent = ProjectIntent(
            primary_intent=primary_intent,
            confidence=confidence,
            secondary_intents=secondary_intents,
            use_cases=use_cases,
            target_audience=target_audience,
            deployment_context=deployment_context,
            business_domain=business_domain
        )
        
        self.logger.info(f"Intent detected: {primary_intent} (confidence: {confidence:.2f})")
        return intent
    
    def _gather_text_sources(self, project_path: Path, project_name: str, 
                           description: str) -> Dict[str, str]:
        """Gather all text sources for analysis"""
        sources = {
            'project_name': project_name.lower(),
            'description': description.lower(),
            'readme': '',
            'package_description': '',
            'comments': '',
            'file_names': '',
            'directory_names': ''
        }
        
        # Read README files
        for readme_file in ['README.md', 'README.rst', 'README.txt', 'readme.md']:
            readme_path = project_path / readme_file
            if readme_path.exists():
                try:
                    sources['readme'] = readme_path.read_text(encoding='utf-8').lower()
                    break
                except Exception as e:
                    self.logger.warning(f"Could not read {readme_file}: {e}")
        
        # Read package.json description
        package_json = project_path / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    data = json.load(f)
                    sources['package_description'] = data.get('description', '').lower()
            except Exception as e:
                self.logger.warning(f"Could not parse package.json: {e}")
        
        # Extract comments from source files
        sources['comments'] = self._extract_comments(project_path)
        
        # Collect file and directory names
        file_names = []
        dir_names = []
        
        for item in project_path.rglob('*'):
            if self._should_skip_path(item):
                continue
                
            if item.is_file():
                file_names.append(item.name.lower())
            elif item.is_dir():
                dir_names.append(item.name.lower())
        
        sources['file_names'] = ' '.join(file_names)
        sources['directory_names'] = ' '.join(dir_names)
        
        return sources
    
    def _extract_comments(self, project_path: Path) -> str:
        """Extract comments from source files"""
        comments = []
        
        # Python comments
        for py_file in project_path.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8')
                # Extract # comments and docstrings
                python_comments = re.findall(r'#.*|""".*?"""', content, re.DOTALL)
                comments.extend(python_comments)
            except Exception:
                continue
        
        # JavaScript comments
        for js_file in project_path.rglob('*.js'):
            if self._should_skip_path(js_file):
                continue
            try:
                content = js_file.read_text(encoding='utf-8')
                # Extract // and /* */ comments
                js_comments = re.findall(r'//.*|/\*.*?\*/', content, re.DOTALL)
                comments.extend(js_comments)
            except Exception:
                continue
        
        return ' '.join(comments).lower()
    
    def _analyze_file_structure(self, project_path: Path) -> Dict[str, List[str]]:
        """Analyze file structure for intent clues"""
        structure = {
            'files': [],
            'directories': [],
            'extensions': []
        }
        
        for item in project_path.rglob('*'):
            if self._should_skip_path(item):
                continue
            
            if item.is_file():
                structure['files'].append(item.name.lower())
                if item.suffix:
                    structure['extensions'].append(item.suffix.lower())
            elif item.is_dir():
                structure['directories'].append(item.name.lower())
        
        return structure
    
    def _score_intents(self, text_sources: Dict[str, str], 
                      file_structure: Dict[str, List[str]]) -> Dict[str, float]:
        """Score each intent based on evidence"""
        scores = {}
        
        for intent_name, intent_config in self.intent_patterns.items():
            score = 0.0
            
            # Score based on keywords in text
            all_text = ' '.join(text_sources.values())
            for keyword in intent_config['keywords']:
                if keyword in all_text:
                    score += 1.0
                    # Boost score if keyword appears in important places
                    if keyword in text_sources['project_name']:
                        score += 2.0
                    if keyword in text_sources['description']:
                        score += 1.5
                    if keyword in text_sources['readme']:
                        score += 1.0
            
            # Score based on file patterns
            for file_pattern in intent_config['files']:
                for actual_file in file_structure['files']:
                    if file_pattern.lower() in actual_file:
                        score += 2.0
            
            # Score based on frameworks (would be detected separately)
            # This is a simplified version - in production would analyze dependencies
            
            # Apply weight
            score *= intent_config['weight']
            
            scores[intent_name] = score
        
        return scores
    
    def _get_primary_intent(self, scores: Dict[str, float]) -> Tuple[str, float]:
        """Get primary intent with confidence score"""
        if not scores:
            return 'general', 0.0
        
        max_score = max(scores.values())
        if max_score == 0:
            return 'general', 0.0
        
        primary_intent = max(scores.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence based on score distribution
        total_score = sum(scores.values())
        confidence = min(1.0, max_score / max(1.0, total_score - max_score))
        
        return primary_intent, confidence
    
    def _get_secondary_intents(self, scores: Dict[str, float], 
                             primary_intent: str) -> List[Tuple[str, float]]:
        """Get secondary intents ranked by score"""
        secondary = [(intent, score) for intent, score in scores.items() 
                    if intent != primary_intent and score > 0]
        
        # Sort by score and return top 3
        secondary.sort(key=lambda x: x[1], reverse=True)
        return secondary[:3]
    
    def _detect_use_cases(self, text_sources: Dict[str, str], 
                         primary_intent: str) -> List[str]:
        """Detect specific use cases based on intent and text analysis"""
        use_cases = []
        all_text = ' '.join(text_sources.values())
        
        # Intent-specific use case patterns
        use_case_patterns = {
            'web_application': [
                ('user authentication', ['login', 'auth', 'user', 'signup']),
                ('content management', ['cms', 'content', 'blog', 'article']),
                ('e-commerce', ['shop', 'cart', 'payment', 'product']),
                ('dashboard', ['dashboard', 'admin', 'analytics', 'metrics']),
            ],
            'api_service': [
                ('rest api', ['rest', 'api', 'endpoint', 'http']),
                ('data api', ['data', 'database', 'crud', 'model']),
                ('authentication service', ['auth', 'jwt', 'oauth', 'token']),
                ('microservice', ['microservice', 'service', 'distributed']),
            ],
            'data_processing': [
                ('etl pipeline', ['etl', 'extract', 'transform', 'load']),
                ('data analysis', ['analysis', 'analytics', 'insights', 'report']),
                ('batch processing', ['batch', 'job', 'schedule', 'cron']),
                ('real-time processing', ['stream', 'real-time', 'live', 'event']),
            ],
            'machine_learning': [
                ('model training', ['train', 'model', 'fit', 'learning']),
                ('prediction service', ['predict', 'inference', 'model', 'api']),
                ('data preprocessing', ['preprocess', 'clean', 'feature', 'transform']),
                ('model deployment', ['deploy', 'serve', 'production', 'endpoint']),
            ]
        }
        
        if primary_intent in use_case_patterns:
            for use_case, keywords in use_case_patterns[primary_intent]:
                if any(keyword in all_text for keyword in keywords):
                    use_cases.append(use_case)
        
        return use_cases
    
    def _detect_target_audience(self, text_sources: Dict[str, str]) -> str:
        """Detect target audience from text analysis"""
        all_text = ' '.join(text_sources.values())
        
        audience_scores = {}
        for audience, keywords in self.audience_patterns.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            audience_scores[audience] = score
        
        if audience_scores:
            return max(audience_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'general'
    
    def _detect_deployment_context(self, file_structure: Dict[str, List[str]], 
                                 text_sources: Dict[str, str]) -> str:
        """Detect deployment context (cloud, on-premise, etc.)"""
        all_text = ' '.join(text_sources.values())
        files = file_structure['files']
        
        # Check for deployment indicators
        if any(f in files for f in ['dockerfile', 'docker-compose.yml']):
            if 'kubernetes' in all_text or any('k8s' in f for f in files):
                return 'kubernetes'
            else:
                return 'docker'
        
        if any(f in files for f in ['serverless.yml', 'lambda']):
            return 'serverless'
        
        if any(f in files for f in ['terraform', 'cloudformation']):
            return 'infrastructure-as-code'
        
        if 'aws' in all_text or 'gcp' in all_text or 'azure' in all_text:
            return 'cloud'
        
        return 'traditional'
    
    def _detect_business_domain(self, text_sources: Dict[str, str]) -> str:
        """Detect business domain from text analysis"""
        all_text = ' '.join(text_sources.values())
        
        domain_scores = {}
        for domain, keywords in self.domain_patterns.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            # Boost score for project name and description
            if any(keyword in text_sources['project_name'] for keyword in keywords):
                score += 2
            if any(keyword in text_sources['description'] for keyword in keywords):
                score += 1
            domain_scores[domain] = score
        
        if domain_scores and max(domain_scores.values()) > 0:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'general'
    
    def _should_skip_path(self, path: Path) -> bool:
        """Determine if path should be skipped during analysis"""
        skip_patterns = [
            'node_modules', '.git', '__pycache__', '.pytest_cache',
            'venv', 'env', '.venv', 'dist', 'build', '.next', 'target'
        ]
        
        return any(pattern in str(path) for pattern in skip_patterns)