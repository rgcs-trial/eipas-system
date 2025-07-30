"""
Context Analyzer

Semantic project analysis using AST parsing and advanced pattern recognition.
Goes beyond file detection to understand project architecture, patterns, and intent.
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import logging

@dataclass
class ProjectContext:
    """Rich context information about a project"""
    architecture_pattern: str
    frameworks: List[str]
    languages: List[str]
    complexity_score: float
    team_size_estimate: int
    development_stage: str  # 'prototype', 'development', 'production'
    testing_maturity: str   # 'none', 'basic', 'comprehensive'
    ci_cd_maturity: str     # 'none', 'basic', 'advanced'
    security_requirements: str  # 'basic', 'standard', 'high'
    performance_requirements: str  # 'standard', 'high', 'critical'
    
class ContextAnalyzer:
    """Advanced context analysis engine for project understanding"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.architecture_patterns = {
            'microservices': ['docker', 'kubernetes', 'service', 'api'],
            'monolith': ['single', 'unified', 'all-in-one'],
            'serverless': ['lambda', 'function', 'serverless', 'edge'],
            'jamstack': ['static', 'cdn', 'headless', 'gatsby', 'next'],
            'mvc': ['model', 'view', 'controller', 'django', 'rails'],
            'component-based': ['component', 'react', 'vue', 'angular'],
            'event-driven': ['event', 'queue', 'stream', 'kafka', 'redis'],
            'data-pipeline': ['etl', 'pipeline', 'airflow', 'spark', 'kafka']
        }
    
    def analyze_project(self, project_path: Path) -> ProjectContext:
        """Perform comprehensive semantic analysis of project"""
        self.logger.info(f"Starting semantic analysis of {project_path}")
        
        # Gather raw data
        file_analysis = self._analyze_files(project_path)
        dependency_analysis = self._analyze_dependencies(project_path)
        structure_analysis = self._analyze_structure(project_path)
        git_analysis = self._analyze_git_history(project_path)
        
        # Synthesize into context
        context = self._synthesize_context(
            file_analysis, dependency_analysis, structure_analysis, git_analysis
        )
        
        self.logger.info(f"Analysis complete: {context.architecture_pattern} architecture detected")
        return context
    
    def _analyze_files(self, project_path: Path) -> Dict[str, Any]:
        """Deep analysis of source files using AST parsing"""
        analysis = {
            'languages': set(),
            'frameworks': set(),
            'patterns': set(),
            'complexity_indicators': [],
            'function_count': 0,
            'class_count': 0,
            'import_count': 0,
            'test_coverage_estimate': 0.0
        }
        
        # Analyze Python files
        for py_file in project_path.rglob('*.py'):
            if self._should_skip_file(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                self._analyze_python_ast(tree, analysis)
                analysis['languages'].add('Python')
            except Exception as e:
                self.logger.warning(f"Could not parse {py_file}: {e}")
        
        # Analyze JavaScript/TypeScript files
        for js_file in project_path.rglob('*.js'):
            if self._should_skip_file(js_file):
                continue
            self._analyze_javascript_file(js_file, analysis)
            analysis['languages'].add('JavaScript')
        
        for ts_file in project_path.rglob('*.ts'):
            if self._should_skip_file(ts_file):
                continue
            self._analyze_typescript_file(ts_file, analysis)
            analysis['languages'].add('TypeScript')
        
        return analysis
    
    def _analyze_python_ast(self, tree: ast.AST, analysis: Dict[str, Any]):
        """Analyze Python AST for patterns and complexity"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis['function_count'] += 1
                # Detect async patterns
                if node.returns and hasattr(node.returns, 'id'):
                    if 'async' in str(node.returns.id).lower():
                        analysis['patterns'].add('async')
                
            elif isinstance(node, ast.ClassDef):
                analysis['class_count'] += 1
                # Detect design patterns
                class_name = node.name.lower()
                if 'factory' in class_name:
                    analysis['patterns'].add('factory')
                elif 'singleton' in class_name:
                    analysis['patterns'].add('singleton')
                elif 'observer' in class_name:
                    analysis['patterns'].add('observer')
                
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                analysis['import_count'] += 1
                # Detect frameworks from imports
                if isinstance(node, ast.ImportFrom) and node.module:
                    module = node.module.lower()
                    if 'django' in module:
                        analysis['frameworks'].add('Django')
                    elif 'fastapi' in module:
                        analysis['frameworks'].add('FastAPI')
                    elif 'flask' in module:
                        analysis['frameworks'].add('Flask')
                    elif 'pandas' in module:
                        analysis['frameworks'].add('Pandas')
                    elif 'tensorflow' in module or 'torch' in module:
                        analysis['frameworks'].add('ML')
    
    def _analyze_javascript_file(self, js_file: Path, analysis: Dict[str, Any]):
        """Analyze JavaScript file for frameworks and patterns"""
        try:
            content = js_file.read_text(encoding='utf-8')
            
            # Detect frameworks
            if 'react' in content.lower():
                analysis['frameworks'].add('React')
            if 'vue' in content.lower():
                analysis['frameworks'].add('Vue')
            if 'angular' in content.lower():
                analysis['frameworks'].add('Angular')
            
            # Count functions and classes (basic regex approach)
            function_count = len(re.findall(r'function\s+\w+|const\s+\w+\s*=\s*\(', content))
            class_count = len(re.findall(r'class\s+\w+', content))
            
            analysis['function_count'] += function_count
            analysis['class_count'] += class_count
            
        except Exception as e:
            self.logger.warning(f"Could not analyze {js_file}: {e}")
    
    def _analyze_typescript_file(self, ts_file: Path, analysis: Dict[str, Any]):
        """Analyze TypeScript file for advanced patterns"""
        try:
            content = ts_file.read_text(encoding='utf-8')
            
            # TypeScript indicates more mature development
            analysis['patterns'].add('typed')
            
            # Detect Angular specifically
            if '@component' in content.lower() or '@injectable' in content.lower():
                analysis['frameworks'].add('Angular')
            
            # Detect interface usage (good architecture indicator)
            interface_count = len(re.findall(r'interface\s+\w+', content))
            if interface_count > 0:
                analysis['patterns'].add('interface-driven')
            
        except Exception as e:
            self.logger.warning(f"Could not analyze {ts_file}: {e}")
    
    def _analyze_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project dependencies for insights"""
        analysis = {
            'package_managers': set(),
            'dependency_count': 0,
            'dev_dependency_count': 0,
            'security_packages': set(),
            'testing_packages': set(),
            'quality_packages': set()
        }
        
        # Analyze package.json
        package_json = project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                
                analysis['package_managers'].add('npm')
                
                deps = data.get('dependencies', {})
                dev_deps = data.get('devDependencies', {})
                
                analysis['dependency_count'] = len(deps)
                analysis['dev_dependency_count'] = len(dev_deps)
                
                all_deps = {**deps, **dev_deps}
                
                # Categorize dependencies
                for dep in all_deps.keys():
                    dep_lower = dep.lower()
                    if any(security in dep_lower for security in ['helmet', 'cors', 'auth', 'jwt']):
                        analysis['security_packages'].add(dep)
                    if any(test in dep_lower for test in ['jest', 'mocha', 'chai', 'cypress', 'playwright']):
                        analysis['testing_packages'].add(dep)
                    if any(quality in dep_lower for quality in ['eslint', 'prettier', 'typescript']):
                        analysis['quality_packages'].add(dep)
                        
            except Exception as e:
                self.logger.warning(f"Could not parse package.json: {e}")
        
        # Analyze Python dependencies
        requirements_txt = project_path / 'requirements.txt'
        pyproject_toml = project_path / 'pyproject.toml'
        
        if requirements_txt.exists():
            analysis['package_managers'].add('pip')
            self._analyze_python_requirements(requirements_txt, analysis)
        
        if pyproject_toml.exists():
            analysis['package_managers'].add('poetry')
            self._analyze_pyproject_toml(pyproject_toml, analysis)
        
        return analysis
    
    def _analyze_python_requirements(self, req_file: Path, analysis: Dict[str, Any]):
        """Analyze Python requirements file"""
        try:
            content = req_file.read_text()
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
            
            analysis['dependency_count'] += len(lines)
            
            for line in lines:
                package = line.split('==')[0].split('>=')[0].split('~=')[0].lower()
                if any(sec in package for sec in ['cryptography', 'bcrypt', 'passlib']):
                    analysis['security_packages'].add(package)
                if any(test in package for test in ['pytest', 'unittest', 'nose']):
                    analysis['testing_packages'].add(package)
                if any(quality in package for quality in ['black', 'ruff', 'mypy', 'flake8']):
                    analysis['quality_packages'].add(package)
                    
        except Exception as e:
            self.logger.warning(f"Could not analyze requirements.txt: {e}")
    
    def _analyze_pyproject_toml(self, pyproject_file: Path, analysis: Dict[str, Any]):
        """Analyze pyproject.toml for modern Python projects"""
        try:
            content = pyproject_file.read_text()
            # Basic parsing - in production would use tomli/tomllib
            if 'dependencies' in content:
                analysis['patterns'].add('modern-python')
            if 'pytest' in content:
                analysis['testing_packages'].add('pytest')
            if 'black' in content or 'ruff' in content:
                analysis['quality_packages'].add('formatter')
                
        except Exception as e:
            self.logger.warning(f"Could not analyze pyproject.toml: {e}")
    
    def _analyze_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project structure for architectural patterns"""
        analysis = {
            'directory_structure': [],
            'architecture_indicators': set(),
            'file_count': 0,
            'directory_count': 0
        }
        
        # Count files and directories
        for path in project_path.rglob('*'):
            if path.is_file():
                analysis['file_count'] += 1
            elif path.is_dir():
                analysis['directory_count'] += 1
                
                # Detect architectural patterns from directory names
                dir_name = path.name.lower()
                if dir_name in ['services', 'microservices']:
                    analysis['architecture_indicators'].add('microservices')
                elif dir_name in ['components', 'widgets']:
                    analysis['architecture_indicators'].add('component-based')
                elif dir_name in ['models', 'views', 'controllers']:
                    analysis['architecture_indicators'].add('mvc')
                elif dir_name in ['handlers', 'events', 'listeners']:
                    analysis['architecture_indicators'].add('event-driven')
                elif dir_name in ['tests', 'test', '__tests__']:
                    analysis['architecture_indicators'].add('tested')
        
        return analysis
    
    def _analyze_git_history(self, project_path: Path) -> Dict[str, Any]:
        """Analyze git history for team and development insights"""
        analysis = {
            'has_git': False,
            'commit_count_estimate': 0,
            'contributor_estimate': 1,
            'development_stage': 'prototype'
        }
        
        git_dir = project_path / '.git'
        if git_dir.exists():
            analysis['has_git'] = True
            
            # Simple heuristics based on git structure
            try:
                # Check for branches (indicates more mature development)
                refs_heads = git_dir / 'refs' / 'heads'
                if refs_heads.exists():
                    branches = list(refs_heads.iterdir())
                    if len(branches) > 1:
                        analysis['development_stage'] = 'development'
                    if len(branches) > 3:
                        analysis['development_stage'] = 'production'
                
                # Estimate contributors from logs (if accessible)
                logs_dir = git_dir / 'logs'
                if logs_dir.exists():
                    analysis['contributor_estimate'] = min(5, max(1, len(list(logs_dir.rglob('*')))))
                    
            except Exception as e:
                self.logger.warning(f"Could not analyze git history: {e}")
        
        return analysis
    
    def _synthesize_context(self, file_analysis: Dict, dependency_analysis: Dict, 
                          structure_analysis: Dict, git_analysis: Dict) -> ProjectContext:
        """Synthesize all analysis into coherent project context"""
        
        # Determine architecture pattern
        architecture_pattern = self._determine_architecture_pattern(
            file_analysis, dependency_analysis, structure_analysis
        )
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(file_analysis, dependency_analysis)
        
        # Estimate team size
        team_size = max(1, git_analysis.get('contributor_estimate', 1))
        
        # Determine development stage
        development_stage = self._determine_development_stage(
            dependency_analysis, structure_analysis, git_analysis
        )
        
        # Assess testing maturity
        testing_maturity = self._assess_testing_maturity(dependency_analysis, structure_analysis)
        
        # Assess CI/CD maturity
        ci_cd_maturity = self._assess_ci_cd_maturity(structure_analysis)
        
        # Determine security requirements
        security_requirements = self._determine_security_requirements(dependency_analysis)
        
        # Determine performance requirements
        performance_requirements = self._determine_performance_requirements(file_analysis)
        
        return ProjectContext(
            architecture_pattern=architecture_pattern,
            frameworks=list(file_analysis.get('frameworks', [])),
            languages=list(file_analysis.get('languages', [])),
            complexity_score=complexity_score,
            team_size_estimate=team_size,
            development_stage=development_stage,
            testing_maturity=testing_maturity,
            ci_cd_maturity=ci_cd_maturity,
            security_requirements=security_requirements,
            performance_requirements=performance_requirements
        )
    
    def _determine_architecture_pattern(self, file_analysis: Dict, dependency_analysis: Dict, 
                                      structure_analysis: Dict) -> str:
        """Determine the primary architectural pattern"""
        indicators = structure_analysis.get('architecture_indicators', set())
        
        # Score each pattern
        pattern_scores = defaultdict(int)
        
        for indicator in indicators:
            pattern_scores[indicator] += 2
        
        # Add framework-based scoring
        frameworks = file_analysis.get('frameworks', set())
        for framework in frameworks:
            if framework in ['React', 'Vue', 'Angular']:
                pattern_scores['component-based'] += 1
            elif framework in ['Django', 'Rails']:
                pattern_scores['mvc'] += 1
            elif framework in ['FastAPI', 'Express']:
                pattern_scores['microservices'] += 1
        
        # Return highest scoring pattern
        if pattern_scores:
            return max(pattern_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'general'
    
    def _calculate_complexity_score(self, file_analysis: Dict, dependency_analysis: Dict) -> float:
        """Calculate project complexity score (0.0 to 1.0)"""
        score = 0.0
        
        # Function/class count contribution
        function_count = file_analysis.get('function_count', 0)
        class_count = file_analysis.get('class_count', 0)
        
        if function_count + class_count > 0:
            score += min(0.3, (function_count + class_count) / 1000)
        
        # Dependency count contribution
        dep_count = dependency_analysis.get('dependency_count', 0)
        dev_dep_count = dependency_analysis.get('dev_dependency_count', 0)
        
        if dep_count + dev_dep_count > 0:
            score += min(0.3, (dep_count + dev_dep_count) / 100)
        
        # Language diversity contribution
        language_count = len(file_analysis.get('languages', []))
        score += min(0.2, language_count / 5)
        
        # Framework diversity contribution
        framework_count = len(file_analysis.get('frameworks', []))
        score += min(0.2, framework_count / 5)
        
        return min(1.0, score)
    
    def _determine_development_stage(self, dependency_analysis: Dict, structure_analysis: Dict,
                                   git_analysis: Dict) -> str:
        """Determine the development stage of the project"""
        # Check for production indicators
        security_packages = len(dependency_analysis.get('security_packages', set()))
        testing_packages = len(dependency_analysis.get('testing_packages', set()))
        
        if security_packages >= 2 and testing_packages >= 1:
            return 'production'
        elif testing_packages >= 1 or 'tested' in structure_analysis.get('architecture_indicators', set()):
            return 'development'
        else:
            return 'prototype'
    
    def _assess_testing_maturity(self, dependency_analysis: Dict, structure_analysis: Dict) -> str:
        """Assess testing maturity level"""
        testing_packages = len(dependency_analysis.get('testing_packages', set()))
        has_test_structure = 'tested' in structure_analysis.get('architecture_indicators', set())
        
        if testing_packages >= 2 and has_test_structure:
            return 'comprehensive'
        elif testing_packages >= 1 or has_test_structure:
            return 'basic'
        else:
            return 'none'
    
    def _assess_ci_cd_maturity(self, structure_analysis: Dict) -> str:
        """Assess CI/CD maturity (placeholder - would analyze CI files)"""
        # This would analyze .github/workflows, .gitlab-ci.yml, etc.
        return 'basic'
    
    def _determine_security_requirements(self, dependency_analysis: Dict) -> str:
        """Determine security requirements level"""
        security_packages = len(dependency_analysis.get('security_packages', set()))
        
        if security_packages >= 3:
            return 'high'
        elif security_packages >= 1:
            return 'standard'
        else:
            return 'basic'
    
    def _determine_performance_requirements(self, file_analysis: Dict) -> str:
        """Determine performance requirements level"""
        frameworks = file_analysis.get('frameworks', set())
        
        # ML and data processing typically need high performance
        if any(fw in frameworks for fw in ['ML', 'Pandas', 'TensorFlow']):
            return 'critical'
        
        # Web frameworks need good performance
        if any(fw in frameworks for fw in ['React', 'Vue', 'Angular', 'FastAPI']):
            return 'high'
        
        return 'standard'
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if file should be skipped during analysis"""
        skip_patterns = [
            'node_modules', '.git', '__pycache__', '.pytest_cache',
            'venv', 'env', '.venv', 'dist', 'build', '.next'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)